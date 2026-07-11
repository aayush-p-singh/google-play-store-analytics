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
    try: return int(float(str(review_str).replace(',', '')))
    except ValueError: return 0

def load_and_filter_task4(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Reviews_Numeric'] = df['Reviews'].apply(clean_reviews)
    df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
    df = df.dropna(subset=['Last Updated', 'App'])
    
    df = df[df['Reviews_Numeric'] > 500]
    df = df[~df['App'].str.lower().str.startswith(('x', 'y', 'z'), na=False)]
    df = df[~df['App'].str.contains('S', case=True, na=False)]
    df = df[df['Category'].str.match('^[ECB]', case=True, na=False)]
    
    translation_map = {'BEAUTY': 'सौंदर्य (Beauty)', 'BUSINESS': 'வணிகம் (Business)', 'DATING': 'Partnersuche (Dating)'}
    df['Category'] = df['Category'].apply(lambda x: translation_map.get(str(x).upper(), x))
    
    df['YearMonth'] = df['Last Updated'].dt.to_period('M').dt.to_timestamp()
    ts_data = df.groupby(['Category', 'YearMonth'])['Installs_Numeric'].sum().reset_index()
    ts_data = ts_data.sort_values(by=['Category', 'YearMonth'])
    ts_data['MoM_Growth'] = ts_data.groupby('Category')['Installs_Numeric'].pct_change()
    return ts_data

def render_task4_chart(df: pd.DataFrame):
    chart_data = load_and_filter_task4(df)
    
    fig = px.line(
        chart_data, x='YearMonth', y='Installs_Numeric', color='Category',
        title="Task 4: Normalized Category Growth Trends",
        template="plotly_dark", markers=True
    )
    # Fix outlier compression using a log axis
    fig.update_layout(yaxis_type="log", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")