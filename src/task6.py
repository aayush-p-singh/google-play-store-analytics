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

def clean_reviews(review_str):
    if pd.isna(review_str):
        return 0
    try:
        return int(float(str(review_str).replace(',', '')))
    except ValueError:
        return 0

def load_and_filter_task6(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. Clean core numerical columns
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Reviews_Numeric'] = df['Reviews'].apply(clean_reviews)
    df['Size_MB'] = df['Size'].apply(clean_size)
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    
    df = df.dropna(subset=['Last Updated', 'App'])
    
    # 2. Apply strict numerical filters
    df = df[df['Rating'] >= 4.2]
    df = df[df['Reviews_Numeric'] > 1000]
    df = df[(df['Size_MB'] >= 20.0) & (df['Size_MB'] <= 80.0)]
    
    # 3. Apply string constraints
    # App names must NOT contain numbers
    df = df[~df['App'].str.contains(r'\d', regex=True, na=False)]
    # Categories must start with T or P
    df = df[df['Category'].str.match('^[TP]', case=True, na=False)]
    
    # 4. Translation mapping
    translation_map = {
        'TRAVEL_AND_LOCAL': 'Voyages et infos locales (French)',
        'PRODUCTIVITY': 'Productividad (Spanish)',
        'PHOTOGRAPHY': '写真 - Photography (Japanese)'
    }
    df['Category'] = df['Category'].apply(lambda x: translation_map.get(str(x).upper(), str(x).upper()))
    
    # 5. Time series grouping and calculations
    df['YearMonth'] = df['Last Updated'].dt.to_period('M').dt.to_timestamp()
    
    # Group to get total monthly installs per category
    monthly_data = df.groupby(['Category', 'YearMonth'])['Installs_Numeric'].sum().reset_index()
    monthly_data = monthly_data.sort_values(by=['Category', 'YearMonth'])
    
    # Calculate Month-over-Month growth based on the monthly totals
    monthly_data['MoM_Growth'] = monthly_data.groupby('Category')['Installs_Numeric'].pct_change()
    
    # Calculate Cumulative Installs for the Stacked Area Chart
    monthly_data['Cumulative_Installs'] = monthly_data.groupby('Category')['Installs_Numeric'].cumsum()
    
    return monthly_data

def render_task6_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task6(df)
    
    if chart_data.empty:
        st.warning("No data points matched the strict filter parameters for Module 6.")
        return
        
    fig = px.area(
        chart_data,
        x="YearMonth",
        y="Cumulative_Installs",
        color="Category",
        title="Task 6: Cumulative Installs by Category (25%+ MoM Growth Highlighted)",
        labels={'YearMonth': 'Timeline', 'Cumulative_Installs': 'Cumulative Installs'},
        template="plotly_dark"
    )
    
    # Highlight logic: Draw intensity bands for > 25% MoM growth
    growth_spikes = chart_data[chart_data['MoM_Growth'] > 0.25]
    
    for _, row in growth_spikes.iterrows():
        fig.add_vrect(
            x0=row['YearMonth'], 
            x1=row['YearMonth'] + pd.DateOffset(days=20),
            fillcolor="rgba(255, 255, 255, 0.25)", # Adds visual intensity to the bands
            layer="above", 
            line_width=0
        )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, width="stretch")