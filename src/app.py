import streamlit as st
import pandas as pd

from utils.time_engine import is_window_active 
from task1 import render_task1_chart
from task2 import render_task2_chart
from task3 import render_task3_chart
from task4 import render_task4_chart
from task5 import render_task5_chart
from task6 import render_task6_chart

st.set_page_config(layout="wide", page_title="Elevance Skills Analyst Dashboard")
st.title("Enterprise Google Play Store Analytics Portal")

@st.cache_data
def get_play_store_data():
    # Fetching directly from the original training repository
    url = "https://raw.githubusercontent.com/vaish-vkb/Google-Play-Store-Analytics/main/Play%20Store%20Data.csv"
    return pd.read_csv(url)

@st.cache_data
def get_review_data():
    # Fetching directly from the original training repository
    url = "https://raw.githubusercontent.com/vaish-vkb/Google-Play-Store-Analytics/main/User%20Reviews.csv"
    return pd.read_csv(url)

try:
    raw_df = get_play_store_data()
    reviews_df = get_review_data()
    
    st.sidebar.header("Navigation & Status Control")
    override_mode = st.sidebar.checkbox("Dev Mode: Override Time-Gating", value=False)
    
    st.subheader("Analytical Modules")
    
    # TASK 3: 1 PM - 2 PM IST
    t3_active = is_window_active(13, 14)
    if t3_active or override_mode:
        st.markdown("### Module 3: Monetization and Platform Compatibility Study")
        render_task3_chart(raw_df)
    else:
        st.info("Module 3 is offline. Mounts between 1:00 PM and 2:00 PM IST.")

    st.divider()

    # TASK 1: 3 PM - 5 PM IST
    t1_active = is_window_active(15, 17)
    if t1_active or override_mode:
        st.markdown("### Module 1: High-Install Category Deep-Dive")
        render_task1_chart(raw_df)
    else:
        st.info("Module 1 is offline. Mounts between 3:00 PM and 5:00 PM IST.")
        
    st.divider()
    
    # TASK 6: 4 PM - 6 PM IST
    t6_active = is_window_active(16, 18)
    if t6_active or override_mode:
        st.markdown("### Module 6: Cumulative Category Progression")
        render_task6_chart(raw_df)
    else:
        st.info("Module 6 is offline. Mounts between 4:00 PM and 6:00 PM IST.")

    st.divider()
    
    # TASK 5: 5 PM - 7 PM IST
    t5_active = is_window_active(17, 19)
    if t5_active or override_mode:
        st.markdown("### Module 5: Sentiment & Size Relationship Analysis")
        render_task5_chart(raw_df, reviews_df)
    else:
        st.info("Module 5 is offline. Mounts between 5:00 PM and 7:00 PM IST.")

    st.divider()
    
    # TASK 2: 6 PM - 8 PM IST
    t2_active = is_window_active(18, 20)
    if t2_active or override_mode:
        st.markdown("### Module 2: Spatial Category Distribution")
        render_task2_chart(raw_df)
    else:
        st.info("Module 2 is offline. Mounts between 6:00 PM and 8:00 PM IST.")

    st.divider()
    
    # TASK 4: 6 PM - 9 PM IST
    t4_active = is_window_active(18, 21)
    if t4_active or override_mode:
        st.markdown("### Module 4: Time Series Growth & Localization")
        render_task4_chart(raw_df)
    else:
        st.info("Module 4 is offline. Mounts between 6:00 PM and 9:00 PM IST.")

except Exception as e:
    st.error(f"Failed to fetch external data assets. Please verify network connection. Error: {e}")
