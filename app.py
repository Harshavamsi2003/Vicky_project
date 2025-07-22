# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('DATA.xlsx')
    # Split into two groups
    df['Group'] = ['General Physiotherapists']*20 + ['Pediatric Neuro Physios']*20
    return df

df = load_data()

# Set up the Streamlit app
st.set_page_config(layout="wide")
st.title("Comparative Analysis of Ergonomic Risk Factors")

# REBA Category Distribution
st.header("1. REBA Category Distribution by Group")
reba_counts = df.groupby(['Group', 'REBA_CATEGORY']).size().unstack().fillna(0)
reba_counts = reba_counts.reindex(columns=[0,1,2,3,4], fill_value=0)  # Ensure all categories are present

fig1 = px.bar(reba_counts.T, 
              barmode='group',
              labels={'value': 'Count', 'variable': 'Group', 'index': 'REBA Category'},
              title="Distribution of REBA Risk Categories by Group",
              color_discrete_sequence=px.colors.qualitative.Pastel)
fig1.update_traces(hovertemplate="Group: %{variable}<br>REBA Category: %{x}<br>Count: %{y}")
st.plotly_chart(fig1, use_container_width=True)

# REBA Score Comparison
st.header("2. REBA Score Comparison")
fig2 = px.box(df, x='Group', y='REBA_CATEGORY', 
             color='Group',
             labels={'REBA_CATEGORY': 'REBA Score', 'Group': ''},
             title="Box Plot of REBA Scores by Group")
fig2.update_traces(hovertemplate="Group: %{x}<br>REBA Score: %{y}")
st.plotly_chart(fig2, use_container_width=True)

# Pain Prevalence Comparison
st.header("3. Pain Prevalence Comparison (Last 12 Months)")

# Get all pain columns (P12_*)
pain_cols = [col for col in df.columns if col.startswith('P12_')]
pain_data = []
for col in pain_cols:
    body_part = col.split('_')[1]
    general_pain = df[df['Group']=='General Physiotherapists'][col].sum()
    neuro_pain = df[df['Group']=='Pediatric Neuro Physios'][col].sum()
    pain_data.append({
        'Body Part': body_part,
        'General Physiotherapists': general_pain,
        'Pediatric Neuro Physios': neuro_pain
    })
pain_df = pd.DataFrame(pain_data)

# Melt for plotting
melted_pain = pain_df.melt(id_vars='Body Part', var_name='Group', value_name='Count')

fig3 = px.bar(melted_pain, 
             x='Body Part', 
             y='Count', 
             color='Group',
             barmode='group',
             title="Pain Prevalence by Body Part and Group",
             labels={'Count': 'Number of Reports', 'Body Part': 'Body Region'},
             color_discrete_sequence=px.colors.qualitative.Pastel)
fig3.update_traces(hovertemplate="Group: %{customdata[0]}<br>Body Part: %{x}<br>Count: %{y}")
st.plotly_chart(fig3, use_container_width=True)

# REBA vs Pain Correlation
st.header("4. REBA Score vs Pain Reports")
df['Total_Pain'] = df[pain_cols].sum(axis=1)
fig4 = px.scatter(df, 
                 x='REBA_CATEGORY', 
                 y='Total_Pain', 
                 color='Group',
                 trendline="lowess",
                 labels={'REBA_CATEGORY': 'REBA Score', 'Total_Pain': 'Total Pain Reports'},
                 title="REBA Score vs Total Pain Reports")
fig4.update_traces(hovertemplate="REBA Score: %{x}<br>Pain Reports: %{y}")
st.plotly_chart(fig4, use_container_width=True)
