'''
import streamlit as st
import requests

import pandas as pd
import plotly.express as px


def user_analytics():
    API_URL = "http://127.0.0.1:8000/"


    response = requests.get(f"{API_URL}/user_breakdown/")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses.")
        existing_expenses = []



    df = pd.DataFrame(existing_expenses)



    st.title("Expense Breakdown By User")
    #st.subheader("Bar Chart")
    st.bar_chart(data=df.set_index("User")["total_expense"], width=0, height=0)
    fig = px.pie(df, names="User", values="total_expense")
    st.plotly_chart(fig)
    #st.subheader("Pie Chart")
    st.write(df)

'''


