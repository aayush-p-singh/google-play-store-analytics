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

def load_and_filter_task5(df_play: pd.DataFrame, df_reviews: pd.DataFrame) -> pd.DataFrame:
    df = df_play.copy()
    rev = df_reviews.copy()
    
    # Standard cleaning
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Size_MB'] = df['Size'].apply(clean_size)
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Reviews_Numeric'] = df['Reviews'].apply(clean_reviews)
    
    # Calculate average sentiment subjectivity per app
    rev['Sentiment_Subjectivity'] = pd.to_numeric(rev['Sentiment_Subjectivity'], errors='coerce')
    app_sentiment = rev.groupby('App')['Sentiment_Subjectivity'].mean().reset_index()
    
    # Merge datasets
    merged_df = pd.merge(df, app_sentiment, on='App', how='inner')
    
    # Apply strict numerical filters
    merged_df = merged_df[merged_df['Rating'] > 3.5]
    merged_df = merged_df[merged_df['Reviews_Numeric'] > 500]
    merged_df = merged_df[merged_df['Installs_Numeric'] > 50000]
    merged_df = merged_df[merged_df['Sentiment_Subjectivity'] > 0.5]
    
    # Exclude apps containing the letter 'S' (case-sensitive)
    merged_df = merged_df[~merged_df['App'].str.contains('S', case=True, na=False)]
    
    # Isolate specific target categories
    target_categories = [
        'GAME', 'BEAUTY', 'BUSINESS', 'COMICS', 
        'COMMUNICATION', 'DATING', 'ENTERTAINMENT', 
        'SOCIAL', 'EVENTS'
    ]
    merged_df = merged_df[merged_df['Category'].str.upper().isin(target_categories)]
    
    # Apply category string translations
    translation_map = {
        'BEAUTY': 'सौंदर्य (Beauty)',
        'BUSINESS': 'வணிகம் (Business)',
        'DATING': 'Partnersuche (Dating)'
    }
    merged_df['Category'] = merged_df['Category'].apply(lambda x: translation_map.get(str(x).upper(), str(x).upper()))
    
    return merged_df

def render_task5_chart(df_play: pd.DataFrame, df_reviews: pd.DataFrame):
    chart_data = load_and_filter_task5(df_play, df_reviews)
    
    if chart_data.empty:
        st.warning("No data points matched the strict filter parameters for Module 5.")
        return
        
    # Programmatically assign pink (#FFC0CB) to GAME, and default colors to others
    unique_categories = chart_data['Category'].unique()
    color_map = {}
    default_colors = px.colors.qualitative.Plotly
    
    color_index = 0
    for cat in unique_categories:
        if cat == "GAME":
            color_map[cat] = "#FFC0CB" # Pink
        else:
            color_map[cat] = default_colors[color_index % len(default_colors)]
            color_index += 1
            
    fig = px.scatter(
        chart_data,
        x="Size_MB",
        y="Rating",
        size="Installs_Numeric",
        color="Category",
        color_discrete_map=color_map,
        hover_name="App",
        title="Task 5: App Size vs Rating by Category (Sized by Installs)",
        template="plotly_dark",
        size_max=50
    )
    
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, width="stretch")