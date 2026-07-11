import pandas as pd
import plotly.express as px
import streamlit as st

def clean_size(size_str):
    if pd.isna(size_str) or size_str == 'Varies with device': return 0.0
    size_str = str(size_str).upper().strip()
    if 'M' in size_str: return float(size_str.replace('M', '').replace(',', ''))
    if 'K' in size_str: return float(size_str.replace('K', '').replace(',', '')) / 1024.0
    return 0.0

def clean_installs(install_str):
    if pd.isna(install_str): return 0
    install_str = str(install_str).replace('+', '').replace(',', '').strip()
    return int(install_str) if install_str.isdigit() else 0

def clean_reviews(review_str):
    if pd.isna(review_str): return 0
    try: return int(float(str(review_str).replace(',', '')))
    except ValueError: return 0

def load_and_filter_task5(df_play: pd.DataFrame, df_reviews: pd.DataFrame) -> pd.DataFrame:
    df = df_play.copy()
    rev = df_reviews.copy()
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Size_MB'] = df['Size'].apply(clean_size)
    df['Installs_Numeric'] = df['Installs'].apply(clean_installs)
    df['Reviews_Numeric'] = df['Reviews'].apply(clean_reviews)
    
    rev['Sentiment_Subjectivity'] = pd.to_numeric(rev['Sentiment_Subjectivity'], errors='coerce')
    app_sentiment = rev.groupby('App')['Sentiment_Subjectivity'].mean().reset_index()
    merged_df = pd.merge(df, app_sentiment, on='App', how='inner')
    
    merged_df = merged_df[(merged_df['Rating'] > 3.5) & (merged_df['Reviews_Numeric'] > 500) & (merged_df['Installs_Numeric'] > 50000) & (merged_df['Sentiment_Subjectivity'] > 0.5)]
    merged_df = merged_df[~merged_df['App'].str.contains('S', case=True, na=False)]
    
    target_categories = ['GAME', 'BEAUTY', 'BUSINESS', 'COMICS', 'COMMUNICATION', 'DATING', 'ENTERTAINMENT', 'SOCIAL', 'EVENTS']
    merged_df = merged_df[merged_df['Category'].str.upper().isin(target_categories)]
    return merged_df

def render_task5_chart(df_play: pd.DataFrame, df_reviews: pd.DataFrame):
    chart_data = load_and_filter_task5(df_play, df_reviews)
    
    fig = px.scatter(
        chart_data, x="Size_MB", y="Rating", size="Installs_Numeric", color="Category",
        hover_name="App", title="Task 5: Calibrated Size vs Rating Analysis",
        template="plotly_dark"
    )
    # Fix bubble rendering sizes so small categories don't display as 1 pixel
    fig.update_traces(marker=dict(sizemode='area', sizeref=2.*max(chart_data['Installs_Numeric'])/(40.**2), sizemin=4))
    st.plotly_chart(fig, width="stretch")