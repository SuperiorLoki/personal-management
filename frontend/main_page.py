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

        categories = ["Rent", "Food", "Shopping", "Entertainment", "Travel", "Other"]


        if existing_expenses:
            df_data=[{"Notes": expense["notes"], "Category": expense["category"], "Amount": expense["amount"]} for expense in existing_expenses]
            df = pd.DataFrame(df_data)
        else:
            df = pd.DataFrame([{"Notes": "", "Category": "Shopping", "Amount": 0.0}])

        st.write("Add or edit expenses below. Click the + at the bottom to add more rows.")
        edited_df = st.data_editor(
            df, 
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount ($)", min_value=0.0, format="$%.2f", step=1.0),
                "Category": st.column_config.SelectboxColumn("Category", options=categories),
                "Notes": st.column_config.TextColumn("Notes")
            },
            key=f"editor_{selected_date}"
        )

        submit_button = st.button("Save Expenses", type="primary")

        if submit_button:
            valid_rows = edited_df[(edited_df["Amount"] > 0) & (edited_df["Notes"].str.strip() != "")]

            if valid_rows.empty:
                st.warning("Please enter at least one expense with an amount greater than $0.00 and a Note before saving.")
                return 
            
            filtered_expenses = []
            for _, row in valid_rows.iterrows():
                filtered_expenses.append({
                    "amount": float(row["Amount"]),
                    "category": row["Category"],
                    "notes": str(row["Notes"])
                })
            
            response = requests.post(f"{API_URL}/expenses/{selected_date}", json = filtered_expenses, headers=headers)
            #st.write(filtered_expenses)
            if response.status_code == 200:
                st.success("Expenses updated successfully.")
            else:
                st.error("Failed to update expenses.")


'''
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
                with col3:
                    if i == 0:
                        st.write("User")
                    user_input = st.text_input(label="Users", value=user, key = f"user_{i}", label_visibility="collapsed")
                
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
                


st.title("Expense Tracking System")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add/Update", "Analytics", "Month by Month Breakdown", "Report", "Scanner"])

with tab1:
    main_screen()
with tab2:
    analytics_ui()'''
