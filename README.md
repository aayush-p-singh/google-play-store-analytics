# Enterprise Google Play Store Analytics Portal

A time-gated, interactive data analytics dashboard built with Python, Streamlit, and Plotly. This project processes and visualizes Google Play Store metrics and user sentiment data under strict operational parameters.

## Architecture & Features
* **Dynamic Time-Gating Engine:** Analytical modules are programmatically restricted to specific execution windows (e.g., 15:00 - 17:00 IST) using timezone-aware logic (`pytz`).
* **Advanced Data Processing:** Utilizes `pandas` for complex string manipulation, regex-based exclusion filtering, and conditional aggregation across dual datasets.
* **Spatial & Sentiment Analysis:** Features synthetic geographical mapping via Plotly Choropleth and inner-join data merges to calculate app-level sentiment subjectivity.
* **Automated Localization:** Implements programmatic translation mapping for dynamic category rendering in multiple languages (Hindi, Tamil, German, French, Spanish, Japanese).

## Local Execution
1. Clone the repository.
2. Place the target datasets (`Play Store Data.csv` and `User Reviews.csv`) into a local `/data` directory at the root level.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `streamlit run src/app.py`