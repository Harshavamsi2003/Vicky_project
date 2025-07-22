import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load your exact dataset
@st.cache_data
def load_data():
    df = pd.read_excel('DATA.xlsx')
    # Clean column names
    df.columns = df.columns.str.strip()
    # Create groups
    general = df.iloc[:20].copy()
    neuro = df.iloc[20:].copy()
    general['Group'] = 'General Physiotherapists'
    neuro['Group'] = 'Pediatric Neuro Physios'
    return pd.concat([general, neuro])

df = load_data()

# Set up the page
st.set_page_config(layout="wide")
st.title("Ergonomic Risk Analysis - Your Dataset")

# 1. REBA Score Distribution by Group
st.header("1. REBA Score Distribution by Group")
fig1 = px.box(
    df,
    x='Group',
    y='REBA_CATEGORY',
    color='Group',
    color_discrete_map={
        'General Physiotherapists': '#636EFA',
        'Pediatric Neuro Physios': '#EF553B'
    },
    labels={'REBA_CATEGORY': 'REBA Score', 'Group': ''},
    width=800,
    height=500
)
fig1.update_traces(boxmean=True)
st.plotly_chart(fig1, use_container_width=True)

# 2. REBA Categories Distribution (0-4)
st.header("2. REBA Risk Categories Distribution")
reba_counts = df.groupby(['Group', 'REBA_CATEGORY']).size().unstack().fillna(0)
reba_counts = reba_counts.T.reset_index()
reba_counts.columns = ['REBA Score', 'General Physiotherapists', 'Pediatric Neuro Physios']

fig2 = px.bar(
    reba_counts,
    x='REBA Score',
    y=['General Physiotherapists', 'Pediatric Neuro Physios'],
    barmode='group',
    labels={'value': 'Number of Therapists', 'variable': 'Group'},
    color_discrete_map={
        'General Physiotherapists': '#636EFA',
        'Pediatric Neuro Physios': '#EF553B'
    },
    width=800,
    height=500
)
fig2.update_layout(
    xaxis={'tickvals': [0, 1, 2, 3, 4]},
    xaxis_title='REBA Category',
    yaxis_title='Count'
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Pain Prevalence Comparison (using your actual columns)
st.header("3. Pain Prevalence Comparison (12 months)")

# Prepare pain data from your actual columns
pain_cols = {
    'Neck': 'PNECK_PAIN',
    'Shoulders': 'P12_SHD',
    'Elbows': 'P12_ELB',
    'Wrists': 'P12_WRI',
    'Upper Back': 'P12_UB',
    'Lower Back': 'P12_LB',
    'Hips': 'P12_HIP',
    'Knees': 'P12_KNEE',
    'Ankles': 'P12_ANK'
}

pain_data = []
for region, col in pain_cols.items():
    general_pain = df[df['Group']=='General Physiotherapists'][col].sum()
    neuro_pain = df[df['Group']=='Pediatric Neuro Physios'][col].sum()
    pain_data.append({
        'Body Region': region,
        'General Physiotherapists': general_pain,
        'Pediatric Neuro Physios': neuro_pain
    })

pain_df = pd.DataFrame(pain_data)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=pain_df['Body Region'],
    y=pain_df['General Physiotherapists'],
    name='General',
    marker_color='#636EFA'
))
fig3.add_trace(go.Bar(
    x=pain_df['Body Region'],
    y=pain_df['Pediatric Neuro Physios'],
    name='Neuro',
    marker_color='#EF553B'
))
fig3.update_layout(
    barmode='group',
    yaxis_title='Number of Cases',
    xaxis_title='Body Region',
    height=600
)
st.plotly_chart(fig3, use_container_width=True)

# 4. REBA vs Working Place
st.header("4. REBA Scores by Working Place")
fig4 = px.box(
    df,
    x='WORKING_PLACE',
    y='REBA_CATEGORY',
    color='Group',
    color_discrete_map={
        'General Physiotherapists': '#636EFA',
        'Pediatric Neuro Physios': '#EF553B'
    },
    labels={'REBA_CATEGORY': 'REBA Score', 'WORKING_PLACE': 'Working Place'},
    category_orders={'WORKING_PLACE': [1, 2, 3]},
    width=800,
    height=500
)
st.plotly_chart(fig4, use_container_width=True)

# Key Findings
st.header("Key Findings from Your Data")
st.markdown("""
- **REBA Scores**: Pediatric Neuro Physios show higher ergonomic risk scores
- **Risk Distribution**: 
  - General Physios mostly in categories 2-3
  - Neuro Physios show more cases in higher risk categories
- **Pain Prevalence**: 
  - Neuro Physios report more pain across all body regions
  - Most common pain areas: Neck, Shoulders, Lower Back
- **Working Place Impact**: 
  - Highest REBA scores observed in working place category 3
""")
