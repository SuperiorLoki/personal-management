import streamlit as st

from all_tasks import all_tasks
from main_page import main_screen
from analytics_ui import analytics
from month_analytics import months
from report_ui import report
from task_main import main_screen_tasks
#from user_analytics import user_analytics

col_left, col_center, col_right = st.columns([0.001, 150, 0.001])  # center is slightly wider
#st.set_page_config(layout="centered")

side_tab = st.sidebar.radio(
    "Menu Options",
    ["Expense Tracker", "Planning System"]
)



if side_tab == "Expense Tracker":
    st.title("Expense Tracking System")
    tab1, tab2, tab3, tab4 = st.tabs(["Add/Update", "Analytics", "Month by Month Breakdown", "Report"])

    with tab1:
        main_screen()
    with tab2:
        analytics()
    with tab3:
        months()
    with tab4:
        report()

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



