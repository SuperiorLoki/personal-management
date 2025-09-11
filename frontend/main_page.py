import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def main_screen():
        selected_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed")
        response = requests.get(f"{API_URL}/expenses/{selected_date}")
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.error("Failed to retrieve expenses")
            existing_expenses = []

        categories = ["Rent", "Food", "Shopping", "Entertainment", "Travel", "Other"]
        #users = users_list()
        expenses = []
        with st.form(key="expense_form"):
            for i in range(5):
                if i < len(existing_expenses):
                    amount = existing_expenses[i]["amount"]
                    category = existing_expenses[i]["category"]
                    notes = existing_expenses[i]["notes"]
                    #user = existing_expenses[i]["user"]
                else:
                    amount = 0.0
                    category = "Shopping"
                    notes = ""
                    #user = ""

                col1, col2, col3 = st.columns(3)

                with col1:
                    if i == 0:
                        st.write("Amount")
                    amount_input = st.number_input(label="Amount", min_value=0.0, step=1.0, value=amount, key=f"amount_{i}_{selected_date}", label_visibility="collapsed")
                with col2:
                    if i == 0:
                        st.write("Category")
                    category_input = st.selectbox(label="Category", options=categories, index=categories.index(category), key=f"category_{i}_{selected_date}", label_visibility="collapsed")
                '''with col3:
                    if i == 0:
                        st.write("User")
                    user_input = st.text_input(label="Users", value=user, key = f"user_{i}", label_visibility="collapsed")
                '''
                with col3:
                    if i == 0:
                        st.write("Notes")
                    notes_input = st.text_input(label="Notes", value=notes, key=f"notes_{i}_{selected_date}", label_visibility="collapsed")

                expenses.append({
                    'amount': amount_input,
                    'category': category_input,
                    'notes': notes_input,
                    #'users': user_input
                })

            submit_button = st.form_submit_button()
            if submit_button:
                filtered_expenses = [expense for expense in expenses if expense['amount']>0.0]
                response = requests.post(f"{API_URL}/expenses/{selected_date}", json = filtered_expenses)
                #st.write(filtered_expenses)
                if response.status_code == 200:
                    st.success("Expenses updated successfully.")
                else:
                    st.error("Failed to update expenses.")


