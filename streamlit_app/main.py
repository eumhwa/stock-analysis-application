import os, requests, json

import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

from datetime import datetime
from variables import config, load_code_json

st.title("Stock price Analysis Application")

@st.cache
def load_demo_data(nrow:int):
    params = f"stock_name={config.demo_stock_name}&start_year={config.demo_year}\
                &start_month={config.demo_month}&start_day={config.demo_day}" 
        
    data = requests.get(f"{config.backend_url}/crawl/scrap-price?{params}")
    df = pd.read_json(data.json(), orient="key")
    df["date"] = pd.to_datetime(df["date"])
    # df = df.set_index("date")
    print(df.head())
    return df.iloc[:nrow, :]



data = load_demo_data(config.demo_ndata)
code_dict = load_code_json(config.code_json_path)

st.subheader("Demo data")
c1, c2 = st.columns(2)
if c1.checkbox(f'Show table'):
    st.subheader(f'Raw data: {config.demo_stock_name}')
    st.write(data)
if c2.checkbox(f'Show line chart'):
    st.subheader(f'Line chart: {config.demo_stock_name}')
    chart_df = data.drop("volume", axis=1).melt('date')
    line_chart = alt.Chart(chart_df).mark_line().encode(
        x='date',
        y=alt.Y('value', scale=alt.Scale(zero=False)),
        color='variable'
    ).interactive()
    st.altair_chart(line_chart, use_container_width=True)

st.subheader("Training")
parameters = st.expander("Train parameters", False)
model = parameters.selectbox('model selection', config.available_model_set)
stocks = parameters.selectbox('target stock', tuple(code_dict.keys()))
date = parameters.date_input("start date", min_value=datetime.strptime(f"2018.01.01", "%Y.%m.%d"))
iw = parameters.number_input("input window size", 1, 15)
ow = parameters.number_input("output window size", 1, 5)
val_ratio = parameters.slider('validation data ratio', 0.5, 1.0, step=0.05)

t1, t2 = st.columns(2)
if t1.button("Start training"):
    train_data = {
        "stock_name": str(stocks), 
        "start_year": int(date.year), 
        "start_month": int(date.month), 
        "start_day": int(date.day), 
        "train_parameter": {
            "model_name": model, "valid_rate":float(val_ratio), "input_window":iw, "output_window":ow
            }
        }
    resp = requests.post(f"{config.test_backend_url}/train/start-training", data=json.dumps(train_data))
    if str(resp.status_code) == "200":
        st.write("Training started..")
        st.success(f"parameter set: [{train_data}]")
    else:
        st.write(f"Trainig failed: {resp.status_code}")
        st.error("Error")
        

if t2.button("Check training"):
    st.write("Training started..")
    st.success("in progress")

# if t1.button("Setup"):
#     st.sidebar.write("Training information")
#     model = st.sidebar.selectbox('model selection', ('ARIMA', 'TFT', 'N-Beats'))
#     stocks = st.sidebar.selectbox('target stock', tuple(code_dict.keys()))
#     year = st.sidebar.selectbox('start year', tuple(range(2018, 2022)))
#     month = st.sidebar.selectbox('start month', tuple(range(1, 13)))
#     day = st.sidebar.selectbox('start day', tuple(range(1, 32)))
#     val_ratio = st.sidebar.slider('validation data ratio', 0.0, 1.0, step=0.05)

#     if st.sidebar.button("Save configuration"):
#         st.sidebar.write("saved!")
#         st.sidebar.success("Success")

