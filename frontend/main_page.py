import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "https://personal-management-1.onrender.com"

def main_screen():
        
        if "token" not in st.session_state:
            st.warning("🔒 Please log in to view and add expenses.")
            return
        
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        selected_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed")
        response = requests.get(f"{API_URL}/expenses/{selected_date}", headers=headers)
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.error("Failed to retrieve expenses")
            existing_expenses = []

        row_state_key = f"row_count_{selected_date}"
        if row_state_key not in st.session_state:
            st.session_state[row_state_key] = max(5, len(existing_expenses))

        row_count = st.session_state[row_state_key]
        categories = ["Rent", "Food", "Shopping", "Entertainment", "Travel", "Other"]


        #users = users_list()
        expenses = []
        with st.form(key=f"expense_form_{selected_date}"):
            for i in range(row_count):
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

                col1, col2, col3, col4 = st.columns([2,2,3,1])

                with col1:
                    if i == 0:
                        st.write("Amount")
                    amount_input = st.number_input(label="Amount", min_value=0.0, step=1.0, value=amount, key=f"amount_{i}_{selected_date}", label_visibility="collapsed")
                with col2:
                    if i == 0:
                        st.write("Category")
                    safe_index = categories.index(category) if category in categories else 2
                    category_input = st.selectbox(label="Category", options=categories, index=safe_index, key=f"category_{i}_{selected_date}", label_visibility="collapsed")
                '''
                with col3:
                    if i == 0:
                        st.write("User")
                    user_input = st.text_input(label="Users", value=user, key = f"user_{i}", label_visibility="collapsed")
                '''
                with col3:
                    if i == 0:
                        st.write("Notes")
                    notes_input = st.text_input(label="Notes", value=notes, key=f"notes_{i}_{selected_date}", label_visibility="collapsed")

                with col4:
                    if i == 0:
                        st.write("Delete")
                    delete_input = st.checkbox("🗑️", key=f"delete_{i}_{selected_date}")

                expenses.append({
                    'amount': amount_input,
                    'category': category_input,
                    'notes': notes_input,
                    'delete': delete_input
                    #'users': user_input
                })
            st.write("")
            col_button1, col_button2 = st.columns([1,3])
            with col_button1:
                add_row_button = st.form_submit_button("Add Row")
            with col_button2:
                submit_button = st.form_submit_button("Save Expenses", type="primary")
            
            if add_row_button:
                st.session_state[row_state_key] += 1
                st.rerun()

            if submit_button:

                filtered_expenses = [expense for expense in expenses if expense['amount']>0.0 and not expense['delete']]

                clean_payload = [
                    {"amount": exp["amount"], "category": exp["category"], "notes": exp["notes"]} for exp in filtered_expenses]
                if not clean_payload and len(existing_expenses) == 0:
                    st.warning("Please enter at least one expense with an amount greater than $0.00 before saving.")
                    return
                else:
                    with st.spinner("Saving expenses to database..."):
                        response = requests.post(f"{API_URL}/expenses/{selected_date}", json=clean_payload, headers=headers)
                        if response.status_code == 200:
                            st.success("Expenses updated successfully.")
                            if row_state_key in st.session_state:
                                del st.session_state[row_state_key]
                            st.rerun()
                        else:
                            st.error("Failed to update expenses.")

'''
st.title("Expense Tracking System")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add/Update", "Analytics", "Month by Month Breakdown", "Report", "Scanner"])

with tab1:
    main_screen()
with tab2:
    analytics_ui()'''
