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

def clean_reviews(review_str):
    if pd.isna(review_str):
        return 0
    try:
        return int(float(str(review_str).replace(',', '')))
    except ValueError:
        return 0

def load_and_filter_task4(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Reviews_Numeric'] = df['Reviews'].apply(clean_reviews)
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    
    # Drop rows with missing dates or missing app names
    df = df.dropna(subset=['Last Updated', 'App'])
    
    # Filter 1: Reviews > 500
    df = df[df['Reviews_Numeric'] > 500]
    
    # Filter 2: App name does not start with x, y, z (case-insensitive)
    invalid_starts = ('x', 'y', 'z')
    df = df[~df['App'].str.lower().str.startswith(invalid_starts, na=False)]
    
    # Filter 3: App name does not contain "S" (case-sensitive as per strict instruction)
    df = df[~df['App'].str.contains('S', case=True, na=False)]
    
    # Filter 4: Category starts with E, C, or B
    df = df[df['Category'].str.match('^[ECB]', case=True, na=False)]
    
    # Translation Dictionary implementation
    # Beauty -> Hindi, Business -> Tamil, Dating -> German
    translation_map = {
        'BEAUTY': 'सौंदर्य (Beauty)',
        'BUSINESS': 'வணிகம் (Business)',
        'DATING': 'Partnersuche (Dating)'
    }
    
    # Apply translations to the Category column
    df['Category'] = df['Category'].apply(lambda x: translation_map.get(str(x).upper(), x))
    
    # Time Series Aggregation
    # Convert dates to Year-Month period, then back to timestamp for Plotly compatibility
    df['YearMonth'] = df['Last Updated'].dt.to_period('M').dt.to_timestamp()
    
    # Group by Category and YearMonth to get total installs
    ts_data = df.groupby(['Category', 'YearMonth'])['Installs_Numeric'].sum().reset_index()
    
    # Sort values chronologically to calculate Month-over-Month growth accurately
    ts_data = ts_data.sort_values(by=['Category', 'YearMonth'])
    
    # Calculate percentage change month-over-month per category
    ts_data['MoM_Growth'] = ts_data.groupby('Category')['Installs_Numeric'].pct_change()
    
    return ts_data

def render_task4_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task4(df)
    
    if chart_data.empty:
        st.warning("No data points matched the strict filter parameters for Module 4.")
        return
        
    fig = px.line(
        chart_data,
        x='YearMonth',
        y='Installs_Numeric',
        color='Category',
        title="Task 4: Trend of Total Installs Over Time (MoM Growth > 20% Highlighted)",
        labels={'YearMonth': 'Timeline', 'Installs_Numeric': 'Total Installs'},
        template="plotly_dark",
        markers=True
    )
    
    # Highlight logic: iterate through data and shade areas where MoM > 20%
    # We find rows where growth > 0.20 and draw a faint vertical rectangle on that specific date
    growth_spikes = chart_data[chart_data['MoM_Growth'] > 0.20]
    
    for _, row in growth_spikes.iterrows():
        # Add a visual highlight on the timeline for significant growth
        fig.add_vrect(
            x0=row['YearMonth'], 
            x1=row['YearMonth'] + pd.DateOffset(days=15), # Slight width for visibility
            fillcolor="rgba(255, 255, 255, 0.15)", 
            opacity=0.5, 
            layer="below", 
            line_width=0
        )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)