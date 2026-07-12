import streamlit as st
import requests
from datetime import datetime
import plotly.express as px
import pandas as pd


API_URL = "https://personal-management-1.onrender.com"

def months():
    headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
    response = requests.get(f"{API_URL}/month_breakdown/", headers=headers)
    if response.status_code == 200:
        existing_expenses = response.json()
        st.write(existing_expenses)
    else:
        st.error("Failed to retrieve expenses.")
        existing_expenses = []


    df = pd.DataFrame(existing_expenses)
    if df.empty or "month" not in df.columns:
        st.info("No monthly expense data found yet. Add some expenses first.")
        return 
    new_months = []
    for month in df["month"]:
        date_obj = datetime.strptime(month, "%Y-%m")
        month_s = date_obj.strftime("%B %Y")
        new_months.append(month_s)

    df["month"] = new_months


    st.title("Expense Breakdown By Month")
    #st.subheader("Bar Chart")
    st.bar_chart(data=df.set_index("month")["total_expenses"], width=0, height=0)
    fig = px.pie(df, names="month", values="total_expenses")
    st.plotly_chart(fig)
    #st.subheader("Pie Chart")
    st.write(df)
