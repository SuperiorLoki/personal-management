import streamlit as st
import requests
import pandas as pd

API_URL = "https://personal-management-1.onrender.com"

def report():
    token = st.session_state.get('token')
    
    # TEMPORARY DEBUG: Print the first 15 characters of your token to the screen!
    st.write(f"🔑 Current Token in Memory: {str(token)[:15]}...")
    headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
    response = requests.get(f"{API_URL}/report/")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error(f"Render Error {response.status_code}: {response.text}")
        existing_expenses = []

    st.header("Full Expenses List")
    df = pd.DataFrame(existing_expenses)
    if df.empty:
        st.info("No expenses recorded yet. Head over to the Add/Update tab or the Scanner to add your first receipt!")
        return
    df = df.drop('id', axis=1)
    st.write(df)
