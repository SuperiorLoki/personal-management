import pandas as pd
import streamlit as st
from datetime import datetime
import requests

API_URL = "https://personal-management-c1qo.onrender.com"

def all_tasks():
    response = requests.get(f"{API_URL}/tasks/")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    st.header("Master Tasks Viewing List")
    df = pd.DataFrame(existing_expenses)
    df = df.drop('id', axis=1)
    st.write(df)
