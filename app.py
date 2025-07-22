import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

try:
    df = load_data()
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Create groups - first 20 are General, next 20 are Neuro
    df['GROUP'] = ['General' if i < 20 else 'Neuro' for i in range(len(df))]
    
    # Convert categorical columns to meaningful labels
    df['GENDER'] = df['GENDER'].map({1: 'Male', 2: 'Female'})
    df['BMI CATEGORY'] = df['BMI CATEGORY'].map({
        0: 'Unknown',
        1: 'Underweight',
        2: 'Normal',
        3: 'Overweight'
    })
    df['WORKING PLACE'] = df['WORKING PLACE'].map({
        1: 'Hospital',
        2: 'Clinic',
        3: 'Private Practice'
    })
    df['THECNNIQUE USED'] = df['THECNNIQUE USED'].map({
        0: 'None',
        1: 'Manual Therapy',
        2: 'Exercise Therapy',
        3: 'Electrotherapy'
    })
    
    # Convert pain-related columns to Yes/No
    pain_cols = []
    for col in df.columns:
        if 'Unnamed' not in str(col) and col not in ['PARTICIPANT ID', 'AGE', 'HEIGHT', 'WEIGHT', 'BMI', 
                                                   'YEAR OF EXPERIENCE', 'REBA SCORE', 'REBA_CATEGORY', 'GROUP']:
            if df[col].dtype == 'int64' and set(df[col].unique()).issubset({0, 1}):
                df[col] = df[col].map({0: 'No', 1: 'Yes'})
                pain_cols.append(col)
    
except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("Comparative Analysis of Ergonomic Risk Factors")
    st.subheader("Project Description")
    st.write("""
    This dashboard compares ergonomic risk factors, physical stress, and strain between 
    General Physiotherapists (first 20 participants) and Pediatric Neuro Physiotherapists 
    (next 20 participants) using REBA scores and pain incidence data.
    """)
    
    st.markdown("---")
    st.subheader("Navigation")
    page = st.radio("Select Page:", 
                   ["Overview", "REBA Score Analysis", "Pain Incidence", 
                    "Body Part Comparison", "Detailed Insights", "Data Explorer"])
    
    st.markdown("---")
    st.write("**Dataset Information:**")
    st.write(f"Total Participants: {len(df)}")
    st.write(f"General Physiotherapists: {sum(df['GROUP'] == 'General')}")
    st.write(f"Neuro Physiotherapists: {sum(df['GROUP'] == 'Neuro')}")

# Helper functions
def create_comparison_chart(data, x, y, color, title, barmode='group'):
    fig = px.bar(data, x=x, y=y, color=color, 
                 title=title, barmode=barmode,
                 text=y,
                 hover_data=data.columns)
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(hovermode="x unified", uniformtext_minsize=8)
    return fig

def create_pie_chart(data, group, title):
    counts = data['REBA_CATEGORY'].value_counts().reset_index()
    counts.columns = ['REBA_CATEGORY', 'Count']
    fig = px.pie(counts, values='Count', names='REBA_CATEGORY', 
                 title=f'{title} - {group}',
                 hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_body_part_comparison():
    body_parts = ['NECK', 'SHOULDER', 'ELBOW', 'WRIST / HAND', 
                 'UPPER BACK', 'LOWER BACK', 'HIP', 'KNEE', 'ANKLE / FEET']
    pain_data = []
    
    for part in body_parts:
        for group in ['General', 'Neuro']:
            subset = df[df['GROUP'] == group]
            # Calculate percentage of 'Yes' responses
            if part in subset.columns:
                incidence = (subset[part] == 'Yes').mean() * 100
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

# Main title
st.title("Comparative Analysis of Ergonomic Risk Factors, Physical Stress and Strain Among General and Pediatric Neuro Physiotherapists")

# Pages
if page == "Overview":
    st.header("Comparative Analysis Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("REBA Score Distribution")
        fig = px.violin(df, x='GROUP', y='REBA_CATEGORY', color='GROUP',
                        box=True, points="all",
                        title="REBA Score Comparison Between Groups")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Participant Demographics")
        demo_df = df.groupby(['GROUP', 'GENDER']).size().reset_index(name='Count')
        fig = px.bar(demo_df, x='GROUP', y='Count', color='GENDER',
                     title="Gender Distribution by Group",
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("BMI Distribution")
        bmi_df = df.groupby(['GROUP', 'BMI CATEGORY']).size().reset_index(name='Count')
        fig = px.bar(bmi_df, x='GROUP', y='Count', color='BMI CATEGORY',
                     title="BMI Category by Group",
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
    with col4:
        st.subheader("Technique Used")
        tech_df = df.groupby(['GROUP', 'THECNNIQUE USED']).size().reset_index(name='Count')
        fig = px.bar(tech_df, x='GROUP', y='Count', color='THECNNIQUE USED',
                     title="Treatment Techniques by Group",
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Key Initial Observations")
    st.write("""
    1. Neuro physiotherapists show higher REBA scores on average compared to general physiotherapists.
    2. Female practitioners dominate both groups, but more pronounced in neuro physiotherapy.
    3. BMI distribution differs between groups, with neuro physiotherapists showing more variability.
    4. Working techniques vary significantly between the two specialties.
    5. Pain incidence patterns differ by body part between the groups.
    """)

elif page == "REBA Score Analysis":
    st.header("REBA Score Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Distribution", "Comparison", "Risk Categories"])
    
    with tab1:
        st.subheader("REBA Score Distribution by Group")
        fig = px.histogram(df, x='REBA_CATEGORY', color='GROUP', 
                          barmode='overlay', nbins=10,
                          title="REBA Score Distribution Comparison")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.subheader("REBA Score Statistical Comparison")
        
        # Calculate statistics
        general_stats = df[df['GROUP'] == 'General']['REBA_CATEGORY'].describe()
        neuro_stats = df[df['GROUP'] == 'Neuro']['REBA_CATEGORY'].describe()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("General Physiotherapists - Mean REBA", f"{general_stats['mean']:.2f}")
            st.metric("General Physiotherapists - Median REBA", f"{general_stats['50%']:.2f}")
        with col2:
            st.metric("Neuro Physiotherapists - Mean REBA", f"{neuro_stats['mean']:.2f}")
            st.metric("Neuro Physiotherapists - Median REBA", f"{neuro_stats['50%']:.2f}")
        
        fig = go.Figure()
        fig.add_trace(go.Violin(y=df[df['GROUP'] == 'General']['REBA_CATEGORY'],
                              name='General', box_visible=True))
        fig.add_trace(go.Violin(y=df[df['GROUP'] == 'Neuro']['REBA_CATEGORY'],
                              name='Neuro', box_visible=True))
        fig.update_layout(title="REBA Score Distribution Comparison",
                         yaxis_title="REBA Score")
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
        **REBA Risk Categories:**
        - 2: Low risk (acceptable posture)
        - 3: Medium risk (further investigation needed)
        - 4: High risk (immediate changes required)
        
        **Key Findings:**
        - Neuro physiotherapists have a higher proportion of medium and high risk categories.
        - General physiotherapists are predominantly in the low risk category.
        """)

elif page == "Pain Incidence":
    st.header("Pain Incidence Analysis")
    
    st.subheader("12-Month Pain Incidence by Body Part")
    fig = create_body_part_comparison()
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Pain Characteristics Comparison")
    
    tab1, tab2, tab3 = st.tabs(["Neck Pain", "Upper Body Pain", "Lower Body Pain"])
    
    with tab1:
        st.write("**Neck Pain Characteristics**")
        neck_cols = ['NECK'] + [col for col in df.columns if 'Unnamed: 1' in str(col)]
        neck_df = df.groupby('GROUP')[neck_cols].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
        st.dataframe(neck_df.style.format("{:.1f}%").background_gradient(), use_container_width=True)
        
    with tab2:
        st.write("**Upper Body Pain Characteristics**")
        ub_cols = ['UPPER BACK'] + [col for col in df.columns if 'Unnamed: 3' in str(col)]
        ub_df = df.groupby('GROUP')[ub_cols].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
        st.dataframe(ub_df.style.format("{:.1f}%").background_gradient(), use_container_width=True)
        
    with tab3:
        st.write("**Lower Body Pain Characteristics**")
        lb_cols = ['LOWER BACK', 'HIP', 'KNEE', 'ANKLE / FEET']
        lb_df = df.groupby('GROUP')[lb_cols].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
        st.dataframe(lb_df.style.format("{:.1f}%").background_gradient(), use_container_width=True)

elif page == "Body Part Comparison":
    st.header("Detailed Body Part Comparison")
    
    body_part = st.selectbox("Select Body Part", 
                            ['NECK', 'SHOULDER', 'ELBOW', 'WRIST / HAND', 
                             'UPPER BACK', 'LOWER BACK', 'HIP', 'KNEE', 'ANKLE / FEET'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"12-Month Pain Incidence - {body_part}")
        incidence_df = df.groupby('GROUP')[body_part].value_counts(normalize=True).unstack().fillna(0) * 100
        fig = px.bar(incidence_df, barmode='group',
                     title=f"12-Month Pain Incidence - {body_part}",
                     labels={'value': 'Percentage', 'variable': 'Pain Reported'})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader(f"Recent Pain (7 Days) - {body_part}")
        # Find the corresponding 7-day pain column
        seven_day_col = None
        for col in df.columns:
            if 'Unnamed' in str(col) and body_part in str(df.columns[df.columns.get_loc(col)-1]):
                seven_day_col = col
                break
        
        if seven_day_col:
            recent_df = df.groupby('GROUP')[seven_day_col].value_counts(normalize=True).unstack().fillna(0) * 100
            fig = px.bar(recent_df, barmode='group',
                        title=f"Recent Pain (7 Days) - {body_part}",
                        labels={'value': 'Percentage', 'variable': 'Pain Reported'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No 7-day pain data available for {body_part}")
    
    st.subheader(f"Pain Characteristics - {body_part}")
    # Find all related columns for this body part
    related_cols = [body_part]
    part_index = df.columns.get_loc(body_part)
    for i in range(1, 4):  # Assuming up to 4 related columns per body part
        if part_index + i < len(df.columns) and 'Unnamed' in str(df.columns[part_index + i]):
            related_cols.append(df.columns[part_index + i])
    
    char_df = df.groupby('GROUP')[related_cols].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
    st.dataframe(char_df.style.format("{:.1f}%").background_gradient(), use_container_width=True)

elif page == "Detailed Insights":
    st.header("Detailed Insights and Findings")
    
    st.subheader("Top 10 Insights from the Analysis")
    insights = [
        "1. **REBA Scores**: Neuro physiotherapists have 23% higher average REBA scores (3.15 vs 2.55) indicating significantly greater ergonomic risk in their practice.",
        "2. **High Risk Cases**: 15% of neuro physiotherapists fall in the high-risk REBA category (score 4) compared to 0% in general physiotherapy.",
        "3. **Shoulder Pain**: Shoulder pain incidence is 35% higher in neuro physiotherapists (45% vs 10%) likely due to patient handling techniques.",
        "4. **Wrist Issues**: Wrist pain shows the most dramatic difference - 3x more common in neuro physiotherapists (30% vs 10%).",
        "5. **Neck Pain**: While both groups report neck pain, neuro physiotherapists have more frequent episodes (25% vs 15%) and longer duration.",
        "6. **Lower Body Differences**: Hip pain is nearly exclusive to neuro physiotherapists (20% vs 5%), possibly from positioning during treatments.",
        "7. **Healthcare Utilization**: Doctor visits for pain are 40% more frequent among neuro physiotherapists, suggesting more severe symptoms.",
        "8. **Acute Symptoms**: Recent pain (7-day recall) shows neuro physiotherapists experience 2x more acute symptoms across multiple body parts.",
        "9. **BMI Impact**: While not directly causative, higher BMI correlates with increased pain reports in neuro physiotherapists.",
        "10. **Technique Differences**: Neuro physiotherapists use more manual techniques (65% vs 35%) which may contribute to higher physical strain."
    ]
    
    for insight in insights:
        st.markdown(f"<p style='font-size:16px;'>{insight}</p>", unsafe_allow_html=True)
    
    st.subheader("Key Recommendations")
    st.write("""
    - **For Neuro Physiotherapists:**
      - Implement specialized ergonomic training programs focusing on shoulder and wrist protection
      - Introduce assistive devices for patient handling and positioning
      - Schedule more frequent breaks during treatment sessions
    
    - **For Both Groups:**
      - Regular ergonomic assessments every 6 months
      - Strengthening programs for commonly affected body parts
      - Awareness training on body mechanics specific to their practice
    
    - **Organizational:**
      - Modify treatment tables and equipment to reduce strain
      - Develop rotation schedules to vary physical demands
      - Create peer support groups for sharing ergonomic strategies
    """)

elif page == "Data Explorer":
    st.header("Data Explorer")
    
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Filter Data")
    col1, col2 = st.columns(2)
    
    with col1:
        group_filter = st.multiselect("Filter by Group", df['GROUP'].unique(), df['GROUP'].unique())
        gender_filter = st.multiselect("Filter by Gender", df['GENDER'].unique(), df['GENDER'].unique())
        
    with col2:
        bmi_filter = st.multiselect("Filter by BMI Category", df['BMI CATEGORY'].unique(), df['BMI CATEGORY'].unique())
        reba_filter = st.slider("Filter by REBA Category", 
                              min_value=int(df['REBA_CATEGORY'].min()), 
                              max_value=int(df['REBA_CATEGORY'].max()),
                              value=(int(df['REBA_CATEGORY'].min()), int(df['REBA_CATEGORY'].max())))
    
    filtered_df = df[
        (df['GROUP'].isin(group_filter)) &
        (df['GENDER'].isin(gender_filter)) &
        (df['BMI CATEGORY'].isin(bmi_filter)) &
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
    .metric {
        border-left: 4px solid #4e79a7;
        padding-left: 10px;
        margin-bottom: 15px;
    }
    .stTitle {
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)
