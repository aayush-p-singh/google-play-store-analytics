import pandas as pd
import plotly.express as px
import streamlit as st

def clean_size(size_str):
    if pd.isna(size_str) or size_str == 'Varies with device':
        return 0.0
    size_str = str(size_str).upper().strip()
    if 'M' in size_str:
        return float(size_str.replace('M', '').replace(',', ''))
    if 'K' in size_str:
        return float(size_str.replace('K', '').replace(',', '')) / 1024.0
    return 0.0

def clean_installs(install_str):
    if pd.isna(install_str):
        return 0
    install_str = str(install_str).replace('+', '').replace(',', '').strip()
    if install_str.isdigit():
        return int(install_str)
    return 0

def load_and_filter_task1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
    df['Size_MB'] = df['Size'].apply(clean_size)
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    
    cat_summary = df.groupby('Category')['Installs_Numeric'].sum().reset_index()
    top_10_categories = cat_summary.nlargest(10, 'Installs_Numeric')['Category'].tolist()
    df_top10 = df[df['Category'].isin(top_10_categories)].copy()
    
    grouped = df_top10.groupby('Category').agg(
        avg_rating=('Rating', 'mean'),
        avg_size=('Size_MB', 'mean'),
        last_updates=('Last Updated', lambda x: x.dt.month.tolist())
    ).reset_index()
    
    valid_categories = []
    for _, row in grouped.iterrows():
        rating_fail = row['avg_rating'] < 4.0
        size_fail = row['avg_size'] < 10.0
        jan_fail = 1 in row['last_updates']
        
        if not (rating_fail and size_fail and jan_fail):
            valid_categories.append(row['Category'])
            
    final_df = df_top10[df_top10['Category'].isin(valid_categories)]
    
    return final_df.groupby('Category').agg(
        Average_Rating=('Rating', 'mean'),
        Total_Reviews=('Reviews', 'sum')
    ).reset_index()

def render_task1_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task1(df)
    melted_df = chart_data.melt(
        id_vars=['Category'], 
        value_vars=['Average_Rating', 'Total_Reviews'],
        var_name='Metric', 
        value_name='Value'
    )
    
    fig = px.bar(
        melted_df,
        x='Category',
        y='Value',
        color='Metric',
        barmode='group',
        title="Task 1: Average Rating & Total Reviews for Top Categories",
        template="plotly_dark"
    )
    fig.update_layout(yaxis_type="log", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")