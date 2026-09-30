import os
import streamlit as st
import requests
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8003")

ITEMS = [
    'BLACK VELVET',
    'FIREBALL CINNAMON WHISKEY',
    'HAWKEYE VODKA',
    'TITOS HANDMADE VODKA',
    "FIVE O'CLOCK VODKA"
]


st.set_page_config(page_title="Iowa Sales Predictor", page_icon="📊")

st.title('📊 Iowa Alcohol Sales Forecast')

item_name = st.selectbox('Product', ITEMS)

if st.button('Generate Forecast', type="primary"):
    try:
        response = requests.get(f"{API_URL}/predict/{item_name}", timeout=10)

        if response.status_code == 200:
            result = response.json()

            st.success(f"Forecast for: **{result['item']}**")

            df = pd.DataFrame(result['predictions'])
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df['mean'] = df['mean'].round(2)
            df = df[['date', 'mean']].rename(columns={'date': 'Date', 'mean': 'Predicted Sales'})

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.line_chart(df.set_index('Date')['Predicted Sales'])
        else:
            st.error(f"Error: {response.status_code}")

    except Exception as e:
        st.error(f"Cannot connect to backend at {API_URL}")
