import streamlit as st

from frontend.all_tasks import all_tasks
from frontend.main_page import main_screen
from frontend.analytics_ui import analytics
from frontend.month_analytics import months
from frontend.report_ui import report
from frontend.task_main import main_screen_tasks
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



