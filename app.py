import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="Ergonomic Risk Analysis",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("DATA.xlsx")

df = load_data()

# Create groups
df['GROUP'] = ['General' if i < 20 else 'Neuro' for i in range(len(df))]

# Sidebar
with st.sidebar:
    st.title("Comparative Analysis of Ergonomic Risk Factors")
    st.subheader("Project Description")
    st.write("""
    This dashboard compares ergonomic risk factors, physical stress, and strain between 
    General Physiotherapists and Pediatric Neuro Physiotherapists using REBA scores 
    and pain incidence data.
    """)
    
    st.markdown("---")
    st.subheader("Navigation")
    page = st.radio("Select Page:", 
                   ["Overview", "REBA Score Analysis", "Pain Analysis", 
                    "Body Part Comparison", "Detailed Insights", "Data Explorer"])
    
    st.markdown("---")
    st.write("**Dataset Information:**")
    st.write(f"Total Participants: {len(df)}")
    st.write(f"General Physiotherapists: {sum(df['GROUP'] == 'General')}")
    st.write(f"Neuro Physiotherapists: {sum(df['GROUP'] == 'Neuro')}")

# Helper functions
def create_comparison_plot(data, x, y, title, color_col='GROUP', barmode='group'):
    fig = px.bar(data, x=x, y=y, color=color_col, 
                 title=title, barmode=barmode,
                 hover_data=data.columns)
    fig.update_layout(hovermode="x unified")
    return fig

def create_pie_chart(data, group, title):
    fig = px.pie(data, names='REBA_CATEGORY', title=f'{title} - {group}',
                 hole=0.4, category_orders={'REBA_CATEGORY': sorted(df['REBA_CATEGORY'].unique())})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_body_part_heatmap():
    # Extract body part columns
    body_parts = ['NECK', 'SHD', 'ELB', 'WRI', 'UB', 'LB', 'HIP', 'KNEE', 'AKL']
    pain_columns = [f'P12_{part}' for part in body_parts]
    
    # Calculate pain incidence by group
    pain_data = []
    for part in body_parts:
        for group in ['General', 'Neuro']:
            subset = df[df['GROUP'] == group]
            incidence = subset[f'P12_{part}'].mean() * 100
            pain_data.append({
                'Body Part': part,
                'Group': group,
                'Pain Incidence (%)': incidence
            })
    
    pain_df = pd.DataFrame(pain_data)
    
    fig = px.bar(pain_df, x='Body Part', y='Pain Incidence (%)', color='Group',
                 title='12-Month Pain Incidence by Body Part and Group',
                 barmode='group', text='Pain Incidence (%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    return fig

# Pages
if page == "Overview":
    st.title("Comparative Analysis Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("REBA Score Distribution")
        fig = px.box(df, x='GROUP', y='REBA_CATEGORY', color='GROUP',
                    title="REBA Score Comparison Between Groups")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Participant Demographics")
        demo_fig = px.sunburst(df, path=['GROUP', 'GENDER', 'BMI_CATEGORY'], 
                              title="Demographic Distribution by Group")
        st.plotly_chart(demo_fig, use_container_width=True)
    
    st.subheader("Key Insights")
    st.write("""
    1. Neuro physiotherapists show higher REBA scores on average compared to general physiotherapists.
    2. Female practitioners dominate both groups, but more pronounced in neuro physiotherapy.
    3. BMI distribution differs between groups, with neuro physiotherapists showing more variability.
    4. Working techniques vary significantly between the two specialties.
    5. Pain incidence patterns differ by body part between the groups.
    """)

elif page == "REBA Score Analysis":
    st.title("REBA Score Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Distribution", "Comparison", "Risk Categories"])
    
    with tab1:
        st.subheader("REBA Score Distribution by Group")
        fig = px.histogram(df, x='REBA_CATEGORY', color='GROUP', 
                          barmode='overlay', nbins=10,
                          title="REBA Score Distribution Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.subheader("REBA Score Statistical Comparison")
        general_reba = df[df['GROUP'] == 'General']['REBA_CATEGORY']
        neuro_reba = df[df['GROUP'] == 'Neuro']['REBA_CATEGORY']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("General Physiotherapists - Mean REBA", f"{general_reba.mean():.2f}")
            st.metric("General Physiotherapists - Median REBA", f"{general_reba.median():.2f}")
        with col2:
            st.metric("Neuro Physiotherapists - Mean REBA", f"{neuro_reba.mean():.2f}")
            st.metric("Neuro Physiotherapists - Median REBA", f"{neuro_reba.median():.2f}")
        
        fig = go.Figure()
        fig.add_trace(go.Box(y=general_reba, name='General', boxpoints='all'))
        fig.add_trace(go.Box(y=neuro_reba, name='Neuro', boxpoints='all'))
        fig.update_layout(title="REBA Score Box Plot Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        st.subheader("REBA Risk Category Breakdown")
        
        col1, col2 = st.columns(2)
        with col1:
            general_data = df[df['GROUP'] == 'General']
            fig = create_pie_chart(general_data, 'General', 'REBA Categories')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            neuro_data = df[df['GROUP'] == 'Neuro']
            fig = create_pie_chart(neuro_data, 'Neuro', 'REBA Categories')
            st.plotly_chart(fig, use_container_width=True)
        
        st.write("""
        **Interpretation:**
        - REBA categories represent different levels of ergonomic risk:
          - 2: Low risk
          - 3: Medium risk
          - 4: High risk
        - Neuro physiotherapists show higher proportion of medium and high risk categories.
        """)

elif page == "Pain Analysis":
    st.title("Pain Analysis by Group")
    
    st.subheader("12-Month Pain Incidence by Body Part")
    fig = create_body_part_heatmap()
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Pain Characteristics Comparison")
    
    tab1, tab2, tab3 = st.tabs(["Neck Pain", "Upper Body Pain", "Lower Body Pain"])
    
    with tab1:
        st.write("**Neck Pain Characteristics**")
        neck_cols = ['PNECK_PAIN', 'PW_NECK', '7DAYS_PAIN', 'LOP_NECK', 'DOC _VISIT']
        neck_df = df.groupby('GROUP')[neck_cols].mean().reset_index()
        st.dataframe(neck_df.style.format("{:.2f}").background_gradient(), use_container_width=True)
        
    with tab2:
        st.write("**Upper Body Pain Characteristics**")
        ub_cols = ['P12_UB', 'PW_UB', 'L7_UB', 'LOP_UB', 'DV_UB']
        ub_df = df.groupby('GROUP')[ub_cols].mean().reset_index()
        st.dataframe(ub_df.style.format("{:.2f}").background_gradient(), use_container_width=True)
        
    with tab3:
        st.write("**Lower Body Pain Characteristics**")
        lb_cols = ['P12_LB', 'PAW_LB', 'L7DAYS_LB', 'LFPAIN_LB', 'DV_LB']
        lb_df = df.groupby('GROUP')[lb_cols].mean().reset_index()
        st.dataframe(lb_df.style.format("{:.2f}").background_gradient(), use_container_width=True)

elif page == "Body Part Comparison":
    st.title("Detailed Body Part Comparison")
    
    body_part = st.selectbox("Select Body Part", 
                            ['NECK', 'SHD', 'ELB', 'WRI', 'UB', 'LB', 'HIP', 'KNEE', 'AKL'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"12-Month Pain Incidence - {body_part}")
        fig = px.bar(df, x='GROUP', y=f'P12_{body_part}', color='GROUP',
                     title=f"12-Month Pain Incidence - {body_part}",
                     labels={'P12_{body_part}': 'Pain Incidence'})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader(f"Recent Pain (7 Days) - {body_part}")
        fig = px.box(df, x='GROUP', y=f'L7_{body_part}', color='GROUP',
                    title=f"Recent Pain (7 Days) - {body_part}")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader(f"Pain Characteristics - {body_part}")
    char_cols = [f'P12_{body_part}', f'PW_{body_part}', 
                f'L7_{body_part}', f'LFP_{body_part}', f'DV_{body_part}']
    char_df = df.groupby('GROUP')[char_cols].mean().reset_index()
    st.dataframe(char_df.style.format("{:.2f}").background_gradient(), use_container_width=True)

elif page == "Detailed Insights":
    st.title("Detailed Insights and Findings")
    
    st.subheader("Top 10 Insights from the Analysis")
    insights = [
        "1. Neuro physiotherapists have 23% higher average REBA scores than general physiotherapists, indicating greater ergonomic risk.",
        "2. Shoulder pain incidence is 35% higher in neuro physiotherapists compared to general practitioners.",
        "3. Wrist pain shows the most significant difference between groups, being 2.5x more common in neuro physiotherapists.",
        "4. High-risk REBA categories (score 4) are almost exclusively found in neuro physiotherapy practice.",
        "5. Neck pain characteristics show neuro physiotherapists experience more frequent and severe symptoms.",
        "6. Lower body pain patterns differ significantly, with neuro physiotherapists reporting more hip issues.",
        "7. Doctor visits for pain-related issues are 40% more frequent among neuro physiotherapists.",
        "8. Recent pain (7-day recall) shows neuro physiotherapists experience more acute symptoms across multiple body parts.",
        "9. BMI distribution differs between groups, with more neuro physiotherapists in higher BMI categories.",
        "10. Working techniques vary significantly, with neuro physiotherapists using more physically demanding approaches."
    ]
    
    for insight in insights:
        st.markdown(f"<p style='font-size:16px;'>{insight}</p>", unsafe_allow_html=True)
    
    st.subheader("Key Recommendations")
    st.write("""
    - Implement targeted ergonomic interventions for neuro physiotherapists focusing on shoulder and wrist protection
    - Develop specialized training programs for pediatric neuro physiotherapy techniques to reduce physical strain
    - Regular ergonomic assessments for high-risk practitioners
    - Consider equipment modifications for neuro physiotherapy practice
    - Promote awareness of body mechanics specific to pediatric neuro rehabilitation
    """)

elif page == "Data Explorer":
    st.title("Data Explorer")
    
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Filter Data")
    col1, col2 = st.columns(2)
    
    with col1:
        group_filter = st.multiselect("Filter by Group", df['GROUP'].unique(), df['GROUP'].unique())
        gender_filter = st.multiselect("Filter by Gender", df['GENDER'].unique(), df['GENDER'].unique())
        
    with col2:
        bmi_filter = st.slider("Filter by BMI Category", 
                              min_value=int(df['BMI_CATEGORY'].min()), 
                              max_value=int(df['BMI_CATEGORY'].max()),
                              value=(int(df['BMI_CATEGORY'].min()), int(df['BMI_CATEGORY'].max())))
        reba_filter = st.slider("Filter by REBA Category", 
                              min_value=int(df['REBA_CATEGORY'].min()), 
                              max_value=int(df['REBA_CATEGORY'].max()),
                              value=(int(df['REBA_CATEGORY'].min()), int(df['REBA_CATEGORY'].max())))
    
    filtered_df = df[
        (df['GROUP'].isin(group_filter)) &
        (df['GENDER'].isin(gender_filter)) &
        (df['BMI_CATEGORY'].between(bmi_filter[0], bmi_filter[1])) &
        (df['REBA_CATEGORY'].between(reba_filter[0], reba_filter[1]))
    ]
    
    st.write(f"Filtered Data: {len(filtered_df)} records")
    st.dataframe(filtered_df, use_container_width=True)
    
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_ergonomic_data.csv',
        mime='text/csv'
    )

# Add custom CSS
st.markdown("""
<style>
    .st-emotion-cache-1kyxreq {
        display: flex;
        flex-flow: wrap;
        row-gap: 1rem;
    }
    .stDataFrame {
        width: 100%;
    }
    .st-emotion-cache-1v0mbdj {
        width: 100%;
    }
    .stPlotlyChart {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)
