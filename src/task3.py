import pandas as pd
import plotly.graph_objects as px_go
from plotly.subplots import make_subplots
import streamlit as st

def clean_installs(install_str):
    if pd.isna(install_str):
        return 0
    install_str = str(install_str).replace('+', '').replace(',', '').strip()
    if install_str.isdigit():
        return int(install_str)
    return 0

def clean_price(price_str):
    if pd.isna(price_str):
        return 0.0
    price_str = str(price_str).replace('$', '').replace(',', '').strip()
    try:
        return float(price_str)
    except ValueError:
        return 0.0

def clean_size(size_str):
    if pd.isna(size_str) or size_str == 'Varies with device':
        return 0.0
    size_str = str(size_str).upper().strip()
    if 'M' in size_str:
        return float(size_str.replace('M', '').replace(',', ''))
    if 'K' in size_str:
        return float(size_str.replace('K', '').replace(',', '')) / 1024.0
    return 0.0

def clean_android_ver(ver_str):
    if pd.isna(ver_str):
        return 0.0
    ver_str = str(ver_str).strip().split()[0]
    # Extract leading numeric characters
    pure_num = ''
    for char in ver_str:
        if char.isdigit() or char == '.':
            pure_num += char
        else:
            break
    try:
        if pure_num.count('.') > 1:
            # Handle cases like 4.0.3 by shortening to 4.0
            pure_num = '.'.join(pure_num.split('.')[:2])
        return float(pure_num)
    except ValueError:
        return 0.0

def load_and_filter_task3(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Apply baseline data transformations
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Price_Numeric'] = df['Price'].apply(clean_price)
    df['Size_MB'] = df['Size'].apply(clean_size)
    df['Android_Ver_Numeric'] = df['Android Ver'].apply(clean_android_ver)
    df['App_Length'] = df['App'].astype(str).str.len()
    
    # Compute Revenue: Installs * Price
    df['Revenue'] = df['Installs_Numeric'] * df['Price_Numeric']
    
    # Strict Filters Application
    # 1. Exclude apps with < 10,000 installs
    df = df[df['Installs_Numeric'] >= 10000]
    
    # 2. Exclude paid apps with revenue < $10,000 (Free apps have 0 revenue, so we keep them if Type == Free)
    df = df[(df['Type'] == 'Free') | (df['Revenue'] >= 10000)]
    
    # 3. Android version > 4.0
    df = df[df['Android_Ver_Numeric'] > 4.0]
    
    # 4. Size > 15M
    df = df[df['Size_MB'] > 15.0]
    
    # 5. Content Rating = Everyone
    df = df[df['Content Rating'].str.lower() == 'everyone']
    
    # 6. App name length <= 30 characters
    df = df[df['App_Length'] <= 30]
    
    # Identify top 3 categories by remaining volume/installs to narrow focus
    top_3_categories = df.groupby('Category')['Installs_Numeric'].sum().nlargest(3).index.tolist()
    df_filtered = df[df['Category'].isin(top_3_categories)]
    
    # Aggregate data by Category and Type (Free vs Paid)
    aggregated = df_filtered.groupby(['Category', 'Type']).agg(
        Avg_Installs=('Installs_Numeric', 'mean'),
        Avg_Revenue=('Revenue', 'mean')
    ).reset_index()
    
    return aggregated

def render_task3_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task3(df)
    
    if chart_data.empty:
        st.warning("No data points matched the strict filter parameters for Module 3.")
        return
        
    # Create distinct groupings for the X axis
    chart_data['X_Axis_Labels'] = chart_data['Category'] + " (" + chart_data['Type'] + ")"
    
    # Initialize a Plotly Subplot with a secondary Y axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add Average Installs to the Primary Y Axis
    fig.add_trace(
        px_go.Bar(
            x=chart_data['X_Axis_Labels'],
            y=chart_data['Avg_Installs'],
            name="Average Installs",
            marker_color="#1f77b4"
        ),
        secondary_y=False
    )
    
    # Add Average Revenue to the Secondary Y Axis
    fig.add_trace(
        px_go.Scatter(
            x=chart_data['X_Axis_Labels'],
            y=chart_data['Avg_Revenue'],
            name="Average Revenue ($)",
            mode="lines+markers",
            marker_color="#ff7f0e"
        ),
        secondary_y=True
    )
    
    # Configure formal styling parameters
    fig.update_layout(
        title_text="Task 3: Operational Analysis of Free vs Paid Segment Performance",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)")
    )
    
    fig.update_yaxes(title_text="Volume of Installs", secondary_y=False)
    fig.update_yaxes(title_text="Generated Revenue ($)", secondary_y=True)
    
    st.plotly_chart(fig, width="stretch")