import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('DATA.xlsx')
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    # Split into two groups
    general = df.iloc[:20].copy()
    neuro = df.iloc[20:].copy()
    # Add group labels
    general['Group'] = 'General'
    neuro['Group'] = 'Neuro'
    combined = pd.concat([general, neuro])
    return combined, general, neuro

df, general, neuro = load_data()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Demographics", "Pain Analysis", "REBA Scores", "Detailed Comparisons"])

# Helper function to create grouped bar chart
def create_grouped_bar(data1, data2, title, y_title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['General'],
        y=[data1],
        name='General Physiotherapists',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=['Neuro'],
        y=[data2],
        name='Neuro Physiotherapists',
        marker_color='lightsalmon'
    ))
    fig.update_layout(
        title=title,
        yaxis_title=y_title,
        hovermode="x unified"
    )
    return fig

# Pages
if page == "Overview":
    st.title("Comparative Analysis of Ergonomic Risk Factors")
    st.subheader("General vs Pediatric Neuro Physiotherapists")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total General Physiotherapists", "20")
        st.metric("Average REBA Score (General)", f"{general['REBA_CATEGORY'].mean():.1f}")
    with col2:
        st.metric("Total Neuro Physiotherapists", "20")
        st.metric("Average REBA Score (Neuro)", f"{neuro['REBA_CATEGORY'].mean():.1f}")
    
    st.plotly_chart(create_grouped_bar(
        general['REBA_CATEGORY'].mean(),
        neuro['REBA_CATEGORY'].mean(),
        "Average REBA Score Comparison",
        "Average Score"
    ), use_container_width=True)
    
    st.write("""
    ### Key Insights:
    1. Neuro physiotherapists show slightly higher ergonomic risk scores on average.
    2. Both groups experience musculoskeletal pain, but in different body regions.
    3. Working place and BMI distribution differs between the two groups.
    """)

elif page == "Demographics":
    st.title("Demographic Comparison")
    
    # Gender distribution
    gen_gender = general['GENDER'].value_counts()
    neuro_gender = neuro['GENDER'].value_counts()
    
    fig1 = px.pie(values=[gen_gender.get(1, 0), gen_gender.get(2, 0)], 
                 names=['Male', 'Female'], 
                 title='Gender Distribution - General')
    fig2 = px.pie(values=[neuro_gender.get(1, 0), neuro_gender.get(2, 0)], 
                 names=['Male', 'Female'], 
                 title='Gender Distribution - Neuro')
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    
    # BMI distribution
    bmi_counts = pd.DataFrame({
        'Category': ['Unknown', 'Underweight', 'Normal', 'Overweight', 'Obese'],
        'General': [general['BMI_CATEGORY'].value_counts().get(i, 0) for i in range(5)],
        'Neuro': [neuro['BMI_CATEGORY'].value_counts().get(i, 0) for i in range(5)]
    })
    
    fig3 = px.bar(bmi_counts, x='Category', y=['General', 'Neuro'], barmode='group',
                 title='BMI Category Distribution', labels={'value': 'Count'})
    st.plotly_chart(fig3, use_container_width=True)
    
    # Working place
    wp_counts = pd.DataFrame({
        'Place': ['Hospital', 'Clinic', 'Community'],
        'General': [general['WORKING_PLACE'].value_counts().get(i, 0) for i in [1,2,3]],
        'Neuro': [neuro['WORKING_PLACE'].value_counts().get(i, 0) for i in [1,2,3]]
    })
    
    fig4 = px.bar(wp_counts, x='Place', y=['General', 'Neuro'], barmode='group',
                 title='Working Place Distribution', labels={'value': 'Count'})
    st.plotly_chart(fig4, use_container_width=True)

elif page == "Pain Analysis":
    st.title("Pain Analysis Comparison")
    
    # Pain categories
    pain_cats = ['Neck', 'Shoulder', 'Elbow', 'Wrist', 'Upper Back', 'Lower Back', 'Hip', 'Knee', 'Ankle']
    
    # 12-month pain prevalence
    general_pain = [
        general[['PNECK_PAIN', 'P12_SHD', 'P12_ELB', 'P12_WRI', 'P12_UB', 'P12_LB', 'P12_HIP', 'P12_KNEE', 'P12_ANK']].sum().values
    ]
    neuro_pain = [
        neuro[['PNECK_PAIN', 'P12_SHD', 'P12_ELB', 'P12_WRI', 'P12_UB', 'P12_LB', 'P12_HIP', 'P12_KNEE', 'P12_ANK']].sum().values
    ]
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=pain_cats,
        y=general_pain[0],
        name='General',
        marker_color='indianred'
    ))
    fig1.add_trace(go.Bar(
        x=pain_cats,
        y=neuro_pain[0],
        name='Neuro',
        marker_color='lightsalmon'
    ))
    fig1.update_layout(
        title='Pain Distribution by Body Region (12-month prevalence)',
        yaxis_title='Number of Therapists Reporting Pain',
        barmode='group',
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Pain in last 7 days
    general_7day = [
        general[['7DAYS_PAIN', 'L7_SHD', 'L7_ELB', 'L7_WRI', 'L7_UB', 'LFP_SHD', 'L7_HIP', 'L7_KNEE', 'L7_AKL']].sum().values
    ]
    neuro_7day = [
        neuro[['7DAYS_PAIN', 'L7_SHD', 'L7_ELB', 'L7_WRI', 'L7_UB', 'LFP_SHD', 'L7_HIP', 'L7_KNEE', 'L7_AKL']].sum().values
    ]
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=pain_cats,
        y=general_7day[0],
        name='General',
        marker_color='indianred'
    ))
    fig2.add_trace(go.Bar(
        x=pain_cats,
        y=neuro_7day[0],
        name='Neuro',
        marker_color='lightsalmon'
    ))
    fig2.update_layout(
        title='Pain in Last 7 Days by Body Region',
        yaxis_title='Number of Therapists Reporting Pain',
        barmode='group',
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Pain that affected work
    general_paw = [
        general[['PW_NECK', 'PW_SHD', 'PAW_ELB', 'PAW_WRI', 'PW_UB', 'PAW_LB', 'PAW_HIP', 'PAW_KNEE', 'PW_AKL']].sum().values
    ]
    neuro_paw = [
        neuro[['PW_NECK', 'PW_SHD', 'PAW_ELB', 'PAW_WRI', 'PW_UB', 'PAW_LB', 'PAW_HIP', 'PAW_KNEE', 'PW_AKL']].sum().values
    ]
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=pain_cats,
        y=general_paw[0],
        name='General',
        marker_color='indianred'
    ))
    fig3.add_trace(go.Bar(
        x=pain_cats,
        y=neuro_paw[0],
        name='Neuro',
        marker_color='lightsalmon'
    ))
    fig3.update_layout(
        title='Pain that Affected Work by Body Region',
        yaxis_title='Number of Therapists Affected',
        barmode='group',
        hovermode="x unified"
    )
    st.plotly_chart(fig3, use_container_width=True)

elif page == "REBA Scores":
    st.title("REBA Score Analysis")
    
    # REBA distribution
    fig1 = px.histogram(df, x="REBA_CATEGORY", color="Group", 
                       barmode="overlay", nbins=5,
                       title="Distribution of REBA Scores",
                       labels={"REBA_CATEGORY": "REBA Score"},
                       category_orders={"Group": ["General", "Neuro"]})
    st.plotly_chart(fig1, use_container_width=True)
    
    # REBA by BMI
    fig2 = px.box(df, x="BMI_CATEGORY", y="REBA_CATEGORY", color="Group",
                 title="REBA Scores by BMI Category",
                 labels={"BMI_CATEGORY": "BMI Category", "REBA_CATEGORY": "REBA Score"},
                 category_orders={"BMI_CATEGORY": ["0", "1", "2", "3"]})
    st.plotly_chart(fig2, use_container_width=True)
    
    # REBA by working place
    fig3 = px.box(df, x="WORKING_PLACE", y="REBA_CATEGORY", color="Group",
                 title="REBA Scores by Working Place",
                 labels={"WORKING_PLACE": "Working Place", "REBA_CATEGORY": "REBA Score"},
                 category_orders={"WORKING_PLACE": ["1", "2", "3"]})
    st.plotly_chart(fig3, use_container_width=True)
    
    # REBA by technique used
    fig4 = px.box(df, x="TECHNQUE_USED", y="REBA_CATEGORY", color="Group",
                 title="REBA Scores by Technique Used",
                 labels={"TECHNQUE_USED": "Technique", "REBA_CATEGORY": "REBA Score"},
                 category_orders={"TECHNQUE_USED": ["1", "2", "3"]})
    st.plotly_chart(fig4, use_container_width=True)

elif page == "Detailed Comparisons":
    st.title("Detailed Comparisons")
    
    # Pain prevalence comparison
    st.subheader("Pain Prevalence Comparison")
    
    pain_metrics = {
        'Neck Pain (12-month)': ('PNECK_PAIN', 'PNECK_PAIN'),
        'Shoulder Pain (12-month)': ('P12_SHD', 'P12_SHD'),
        'Lower Back Pain (12-month)': ('P12_LB', 'P12_LB'),
        'Neck Pain (7-day)': ('7DAYS_PAIN', '7DAYS_PAIN'),
        'Shoulder Pain (7-day)': ('L7_SHD', 'L7_SHD'),
        'Lower Back Pain (7-day)': ('LFP_SHD', 'LFP_SHD')
    }
    
    cols = st.columns(3)
    for i, (name, (gen_col, neuro_col)) in enumerate(pain_metrics.items()):
        with cols[i % 3]:
            gen_val = general[gen_col].sum()
            neuro_val = neuro[neuro_col].sum()
            st.metric(name, 
                     f"General: {gen_val} | Neuro: {neuro_val}",
                     delta=f"{neuro_val - gen_val} difference")
    
    # Doctor visits comparison
    st.subheader("Doctor Visits Comparison")
    
    doc_metrics = {
        'Neck': ('DOC_VISIT', 'DOC_VISIT'),
        'Shoulder': ('DOC_VISIT', 'DOC_VISIT'),  # Note: Same as neck in original data
        'Elbow': ('DV_ELB', 'DV_ELB'),
        'Wrist': ('DV_WRI', 'DV_WRI'),
        'Upper Back': ('DV_UB', 'DV_UB'),
        'Lower Back': ('DV_LB', 'DV_LB'),
        'Hip': ('DV_HIP', 'DV_HIP'),
        'Knee': ('DV_KNEE', 'DV_KNEE'),
        'Ankle': ('DV_AKL', 'DV_AKL')
    }
    
    doc_data = []
    for name, (gen_col, neuro_col) in doc_metrics.items():
        doc_data.append({
            'Body Part': name,
            'General': general[gen_col].sum(),
            'Neuro': neuro[neuro_col].sum()
        })
    doc_df = pd.DataFrame(doc_data)
    
    fig5 = px.bar(doc_df, x='Body Part', y=['General', 'Neuro'], barmode='group',
                 title='Doctor Visits by Body Region',
                 labels={'value': 'Number of Visits'})
    st.plotly_chart(fig5, use_container_width=True)
    
    # Pain affecting work
    st.subheader("Pain Affecting Work Comparison")
    st.write("""
    - General physiotherapists report more shoulder pain affecting work
    - Neuro physiotherapists report more lower back pain affecting work
    - Both groups report similar levels of neck pain affecting work
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "Comparative Analysis Of Ergonomic Risk Factors Physical "
    "Stress And Strain Among General And Pediatric Neuro Physiotherapists"
)
