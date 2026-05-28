
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
from scipy.stats import mannwhitneyu

st.set_page_config(page_title="Teiko Dashboard", layout="wide")
st.title("🔬 Teiko Immune Cell Analysis Dashboard")

# Database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'teiko.db')

@st.cache_data
def load_data():
    conn = sqlite3.connect(db_path)
    
    # Load and prepare data for all parts
    samples = pd.read_sql_query("SELECT * FROM samples", conn)
    cell_counts = pd.read_sql_query("SELECT * FROM cell_counts", conn)
    subjects = pd.read_sql_query("SELECT * FROM subjects", conn)
    
    conn.close()
    
    # Merge for analysis
    merged = cell_counts.merge(samples, on='sample_id')
    merged = merged.merge(subjects, on='subject_id')
    
    # Calculate percentages
    merged['total_count'] = merged.groupby('sample_id')['count'].transform('sum')
    merged['percentage'] = (merged['count'] / merged['total_count']) * 100
    
    return merged, samples, subjects

if not os.path.exists(db_path):
    st.error("Database not found. Run 'make pipeline' first.")
    st.stop()

try:
    df, samples, subjects = load_data()
    st.success(f"✅ Database connected: {len(samples)} samples, {len(df)} cell measurements")
    
    # ========== PART 2 ==========
    st.header("📊 Part 2: Cell Population Frequencies")
    part2_table = df[['sample_id', 'total_count', 'population', 'count', 'percentage']].drop_duplicates()
    st.dataframe(part2_table.head(100), use_container_width=True)
    st.download_button("Download CSV", part2_table.to_csv(index=False), "part2_frequencies.csv")
    
    # ========== PART 3 ==========
    st.header("🎯 Part 3: Responders vs Non-Responders")
    
    melanoma = df[
        (df['condition'] == 'melanoma') &
        (df['treatment'] == 'miraclib') &
        (df['sample_type'] == 'PBMC') &
        (df['response'].isin(['yes', 'no']))
    ]
    
    if len(melanoma) > 0:
        fig = px.box(melanoma, x='population', y='percentage', color='response',
                     title="Cell Population Frequencies by Response")
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.subheader("Statistical Results")
        for pop in melanoma['population'].unique():
            resp = melanoma[(melanoma['population']==pop) & (melanoma['response']=='yes')]['percentage']
            nonresp = melanoma[(melanoma['population']==pop) & (melanoma['response']=='no')]['percentage']
            _, p = mannwhitneyu(resp, nonresp)
            sig = "✅" if p < 0.05 else "❌"
            st.write(f"{sig} {pop}: p = {p:.4f}")

        # Summary conclusion
        st.subheader("📈 Summary")
        sig_pops = [pop for pop in melanoma['population'].unique() 
                    if mannwhitneyu(
                        melanoma[(melanoma['population']==pop) & (melanoma['response']=='yes')]['percentage'],
                        melanoma[(melanoma['population']==pop) & (melanoma['response']=='no')]['percentage']
                    )[1] < 0.05]
        if sig_pops:
            st.success(f"Significant differences found in: {', '.join(sig_pops)}")
        else:
            st.info("No statistically significant differences found")  
    
    # ========== PART 4 ==========
    st.header("🔍 Part 4: Baseline Subset Analysis")
    
    baseline = df[
        (df['condition'] == 'melanoma') &
        (df['sample_type'] == 'PBMC') &
        (df['time_from_treatment_start'] == 0) &
        (df['treatment'] == 'miraclib')
    ]
    
    if len(baseline) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Baseline Samples", baseline['sample_id'].nunique())
        with col2:
            responders = baseline[baseline['response']=='yes']['subject_id'].nunique()
            nonresponders = baseline[baseline['response']=='no']['subject_id'].nunique()
            st.metric("Response", f"{responders} / {nonresponders}")
        with col3:
            males = baseline[baseline['sex']=='M']['subject_id'].nunique()
            females = baseline[baseline['sex']=='F']['subject_id'].nunique()
            st.metric("Gender", f"M: {males} | F: {females}")
        
        avg_b = baseline[(baseline['sex']=='M') & (baseline['response']=='yes') & (baseline['population']=='b_cell')]['count'].mean()
        st.info(f"🎯 Average B cells for male responders at baseline: **{avg_b:.2f}**")

        # Bar charts
        st.subheader("📊 Distribution Visualizations")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("**Samples per Project**")
            project_counts = baseline[['sample_id', 'project']].drop_duplicates()['project'].value_counts()
            st.bar_chart(project_counts)
        
        with col_b:
            st.write("**Response Status**")
            response_counts = baseline[['subject_id', 'response']].drop_duplicates()['response'].value_counts()
            st.bar_chart(response_counts)
        
        st.write("**Gender Distribution**")
        sex_counts = baseline[['subject_id', 'sex']].drop_duplicates()['sex'].value_counts()
        st.bar_chart(sex_counts)
    
except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")
st.caption("Teiko Dashboard | Data from clinical trial cytometry analysis")
