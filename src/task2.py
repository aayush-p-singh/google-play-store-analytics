import pandas as pd
import plotly.express as px
import streamlit as st

def clean_installs(install_str):
    if pd.isna(install_str):
        return 0
    install_str = str(install_str).replace('+', '').replace(',', '').strip()
    if install_str.isdigit():
        return int(install_str)
    return 0

def load_and_filter_task2(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    
    # Strictly filter out categories starting with A, C, G, or S (case-insensitive)
    filtered_df = df[~df['Category'].str.contains("^[ACGSacgs]", regex=True, na=False)]
    
    # Aggregate total installs per category and isolate the Top 5
    cat_summary = filtered_df.groupby('Category')['Installs_Numeric'].sum().reset_index()
    top_5 = cat_summary.nlargest(5, 'Installs_Numeric').copy()
    
    # Apply standard project ISO alpha-3 regional mapping parameters
    iso_mapping = ['USA', 'IND', 'GBR', 'CAN', 'AUS']
    top_5['ISO_Code'] = iso_mapping[:len(top_5)]
    return top_5

def render_task2_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task2(df)
    
    if chart_data.empty:
        st.warning("No data points matched the strict filter parameters for Module 2.")
        return

    # FIXED: Changed 'range_continuous_scale' to 'range_color'
    fig = px.choropleth(
        chart_data,
        locations="ISO_Code",
        color="Installs_Numeric",
        hover_name="Category",
        color_continuous_scale=["#ff0000", "#00ff00"],  
        range_color=[0, 1000000],            
        title="Task 2: Global Category Installs Distribution (>1M Installs Highlighted)",
        projection="natural earth",
        template="plotly_dark"
    )
    
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, width="stretch")