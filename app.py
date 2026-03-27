import streamlit as st

from frontend.all_tasks import all_tasks
from frontend.main_page import main_screen
from frontend.analytics_ui import analytics
from frontend.month_analytics import months
from frontend.receipt_scanner import scanner
from frontend.report_ui import report
from frontend.task_main import main_screen_tasks
#from user_analytics import user_analytics

col_left, col_center, col_right = st.columns([0.001, 150, 0.001])  # center is slightly wider
#st.set_page_config(layout="centered")

import streamlit as st
from supabase import create_client

# # Initialize Supabase
# url = st.secrets["SUPABASE_URL"]
# key = st.secrets["SUPABASE_KEY"]
# supabase = create_client(url, key)
# 
# if "user" not in st.session_state:
#     st.session_state["user"] = None
# 
# # Login form
# email = st.text_input("Email")
# password = st.text_input("Password", type="password")
# 
# if st.button("Login"):
#     try:
#         res = supabase.auth.sign_in_with_password({"email": email, "password": password})
#         st.session_state["user"] = res.user
#         st.success("Logged in!")
#     except Exception as e:
#         st.error(f"Login failed: {e}")
# 
# # Use user_id when logged in
# if st.session_state["user"]:
#     user_id = st.session_state["user"].id
#     st.write(f"Hello, your ID is {user_id}")


side_tab = st.sidebar.radio(
    "Menu Options",
    ["Expense Tracker", "Planning System"]
)



if side_tab == "Expense Tracker":
    st.title("Expense Tracking System")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add/Update", "Analytics", "Month by Month Breakdown", "Report", "Scanner"])

    with tab1:
        main_screen()
    with tab2:
        analytics()
    with tab3:
        months()
    with tab4:
        report()
    with tab5:
        scanner()

if side_tab == "Planning System":
    st.title("Planning System")
    tab1, tab2  = st.tabs(["To-Do List", "Planner"])

    with tab1:
        main_screen_tasks()
    with tab2:
        all_tasks()

    #



# if side_tab == "Important URLs":
#     st.title("Important Links")
#     tab1, tab2 = st.tabs(["College", "Career"])
#
#     with tab1:
#         st.subheader("UCSD Links")
#     with tab2:
#         st.subheader("Career-Related Links")






