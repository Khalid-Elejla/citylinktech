import streamlit as st

# Local imports
from control_center.map.map import map_page
from control_center.alerts.alerts import alerts_page
from control_center.dashboard.dashboard import dashboard_page
from apps.parking.parking import parking_page
from apps.gate.gate import gate_page
from tools.search import search_page
from tools.history import history_page

# Configure page
st.set_page_config(
    page_title="City Link",
    page_icon="logo.png",
    layout="wide",
)

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Display logo
st.logo("logo.png")


# Login function
def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


# Logout function
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


# Login and logout pages
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# Control center Pages
map = st.Page(map_page, title="Map", icon=":material/map:", default=True)
alerts = st.Page(alerts_page, title="Alerts", icon=":material/notification_important:")
dashboard = st.Page(dashboard_page, title="Dashboard", icon=":material/dashboard:")

# Apps Pages
parking = st.Page(parking_page, title="Parking", icon=":material/local_taxi:")
gate = st.Page(gate_page, title="Gates", icon=":material/speed_camera:")

# Tools Pages
search = st.Page(search_page, title="Search", icon=":material/search:")
history = st.Page(history_page, title="History", icon=":material/history:")

# Navigate between pages
if st.session_state.logged_in:

    pg = st.navigation(
        {
            "Account": [logout_page],
            "Control Center": [map, alerts, dashboard],
            "apps": [parking, gate],
            "Tools": [search, history],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
