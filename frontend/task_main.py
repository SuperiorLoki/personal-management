import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def main_screen_tasks():
    selected_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed")
    response = requests.get(f"{API_URL}/tasks/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
        #st.write(existing_expenses)
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []


    # users = users_list()
    tasks = []

    with st.form(key="task_form"):
        for i in range(5):
            if i < len(existing_expenses):
                name = existing_expenses[i]["task_name"]
                notes = existing_expenses[i]["notes"]
                stat = existing_expenses[i]["task_status"]
                status = True

            else:
                name = "Enter Task Name"
                notes = "Task Description"
                stat = False
                status = False



            col1, col2, col3 = st.columns([0.2,1.5,2])


            with col1:
                if i == 0:
                    st.write("✅")
                if status:
                    select_input = st.checkbox(label="Task Status", value=stat, key=f"stat_{i}_{selected_date}", label_visibility="collapsed")
                else:
                    select_input = st.checkbox(label="Task Status", value=False, key=f"stat_{i}_{selected_date}",
                                               label_visibility="collapsed")

            with col2:
                if i == 0:
                    st.write("Task Name")
                if status:
                    text_input = st.text_input(label="Task Name", value=name,
                                           key=f"name_{i}_{selected_date}", label_visibility="collapsed")
                else:
                    text_input = st.text_input(label="Task Name", value="",
                                               key=f"name_{i}_{selected_date}", placeholder=name,
                                               label_visibility="collapsed")

            '''with col2:
                if i == 0:
                    st.write("Category")
                category_input = st.selectbox(label="Category", options=categories, index=categories.index(category),
                                              key=f"category_{i}_{selected_date}", label_visibility="collapsed")
            with col3:
                if i == 0:
                    st.write("User")
                user_input = st.text_input(label="Users", value=user, key = f"user_{i}", label_visibility="collapsed")
            '''
            with col3:
                if i == 0:
                    st.write("Notes")
                if status:
                    notes_input = st.text_input(label="Notes", value=notes, key=f"notes_{i}_{selected_date}",
                                            label_visibility="collapsed")
                else:
                    notes_input = st.text_input(label="Notes", value="",placeholder=notes, key=f"notes_{i}_{selected_date}",
                                                label_visibility="collapsed")

            tasks.append({
                'task_name': text_input,
                'notes': notes_input,
                'task_status': select_input,
                # 'users': user_input
            })

        submit_button_task = st.form_submit_button(label="Submit Tasks")
        if submit_button_task:
            filtered_tasks = [task for task in tasks if task["task_name"]]
            response = requests.post(f"{API_URL}/tasks/{selected_date}", json=filtered_tasks)
            # st.write(filtered_expenses)
            if response.status_code == 200:
                st.success("Expenses updated successfully.")
            else:
                st.error("Failed to update expenses.")