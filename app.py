import streamlit as st
import requests
from frontend.main_page import main_screen
from frontend.analytics_ui import analytics
from frontend.month_analytics import months
from frontend.receipt_scanner import scanner
from frontend.report_ui import report
from frontend.chat_ui import ai_chat
#from user_analytics import user_analytics

col_left, col_center, col_right = st.columns([0.001, 150, 0.001])  # center is slightly wider
#st.set_page_config(layout="centered")

import streamlit as st
from supabase import create_client

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

st.title("Expense Tracking System")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Add/Update", "Analytics", "Month by Month Breakdown", "Report", "Scanner", "Chat With AI"])

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
with tab6:
    ai_chat()

    #



# if side_tab == "Important URLs":
#     st.title("Important Links")
#     tab1, tab2 = st.tabs(["College", "Career"])
#
#     with tab1:
#         st.subheader("UCSD Links")
#     with tab2:
#         st.subheader("Career-Related Links")

