import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "https://personal-management-1.onrender.com"

if "token" not in st.session_state:
    st.session_state["token"] = None 
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

def auth_screen():
    st.title("Welcome to AI Expense Tracker")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        with st.form("Login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login"):
                res = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    st.session_state["token"] = res.json()["access_token"]
                    st.session_state["user_email"] = email
                    st.success("Log In Success!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")

            if st.form_submit_button("Create Account"):
                res = requests.post(f"{API_URL}/register", json={"email": new_email, "password": new_password})

                if res.status_code == 201:
                    st.success("Account Created! Please switch to the Login tab to login.")
                else:
                    st.error("Failed to create account. That email might already be registered.")

if not st.session_state["token"]:
    auth_screen()

    st.stop()

with st.sidebar:
    st.write(f"Logged in as:\n**{st.session_state['user_email']}**")
    if st.button("Logout"):
        st.session_state["token"] = None
        st.session_state["user_email"] = None
        
        st.rerun()



def main_screen():
        headers = {"Authorization": f"Bearer {st.session_state.get('token')}"}
        selected_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed")
        response = requests.get(f"{API_URL}/expenses/{selected_date}", headers=headers)
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
                if not filtered_expenses:
                    st.warning("Please enter at least one expense with an amount greater than $0.00 before saving.")
                    return
                response = requests.post(f"{API_URL}/expenses/{selected_date}", json = filtered_expenses, headers=headers)
                #st.write(filtered_expenses)
                if response.status_code == 200:
                    st.success("Expenses updated successfully.")
                else:
                    st.error("Failed to update expenses.")


