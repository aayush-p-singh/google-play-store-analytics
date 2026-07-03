import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

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
    
    # 1. String Exclusions: Category should not start with "A", "C", "G", or "S"
    # We use regex to filter these out (^ means 'starts with')
    pattern = "^[ACGSacgs]"
    filtered_df = df[~df['Category'].str.contains(pattern, regex=True, na=False)]
    
    # 2. Aggregate installs by Category
    cat_summary = filtered_df.groupby('Category')['Installs_Numeric'].sum().reset_index()
    
    # 3. Get Top 5 App Categories
    top_5 = cat_summary.nlargest(5, 'Installs_Numeric').copy()
    
    # 4. Synthetic Geographical Mapping 
    # Plotly Choropleth needs ISO alpha-3 country codes. We map the top 5 to major global regions.
    iso_mapping = ['USA', 'IND', 'GBR', 'CAN', 'AUS']
    # Ensure we don't out-of-bounds error if there are fewer than 5 categories
    top_5['ISO_Code'] = iso_mapping[:len(top_5)]
    
    # 5. Highlight logic: Identify if installs > 1 Million
    top_5['Highlight'] = np.where(top_5['Installs_Numeric'] > 1000000, 'Exceeds 1M', 'Below 1M')
    
    return top_5

def render_task2_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task2(df)
    
    # Build the Choropleth
    fig = px.choropleth(
        chart_data,
        locations="ISO_Code",
        color="Highlight",
        hover_name="Category",
        hover_data={"Installs_Numeric": True, "ISO_Code": False},
        color_discrete_map={"Exceeds 1M": "#00ff00", "Below 1M": "#ff0000"}, # Green for > 1M, Red for < 1M
        title="Task 2: Global Installs by Category (Top 5 Filtered)",
        projection="natural earth",
        template="plotly_dark"
    )
    
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, width="stretch")