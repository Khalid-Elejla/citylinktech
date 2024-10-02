import streamlit as st


# Helper function to initialize session state
def initialize_session_state(sheet_names: list[str]) -> None:
    default_states = {
        "selected_sheet_index": 0,
        "btn_prsd_status": [False] * len(sheet_names),
        "dynamic_mode": False,
        "route_coords": [],
        "warning_message": "",
#        "filtered_coordinates": coordinates
    }
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Helper function to display warning
def display_warning() -> None:
    warning_message = st.session_state.get("warning_message", "")
    if warning_message:
        st.warning(warning_message)