import streamlit as st
import requests
import pandas as pd

API_URL = "https://personal-management-1.onrender.com"

def report():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{API_URL}/report/")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    st.header("Full Expenses List")
    df = pd.DataFrame(existing_expenses)
    if df.empty:
        st.info("No expenses recorded yet. Head over to the Add/Update tab or the Scanner to add your first receipt!")
        return
    df = df.drop('id', axis=1)
    st.write(df)
