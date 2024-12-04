import streamlit as st
import json
import time
import pandas as pd

METRICS_PATH = "./metric1.json"

st.title("Real-Time Model Evaluation")
st.subheader("RMSE Evolution")

chart = st.line_chart()

while True:
    try:
       
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)

        
        df = pd.DataFrame(metrics)
        chart.line_chart(df.set_index("batch"))
    except Exception as e:
        st.error(f"Error loading metrics: {e}")

    time.sleep(5)  
