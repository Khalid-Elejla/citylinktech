import streamlit as st
from .map_utils import handle_map_routing



#  Helper function to handle button actions
def handle_buttons(coordinates: list) -> None:
    DEFAULT_LAYOUT = [4, 1, 1, 1, 1, 4]
    col31, col32, col33, col34, col35, col36 = st.columns(DEFAULT_LAYOUT)

    with col32:
        if st.button("🗺️", use_container_width=True) and len(coordinates) >= 2:
            handle_map_routing(coordinates)

    with col33:
        if st.button("🖱️", use_container_width=True):
            st.session_state["dynamic_mode"] = not st.session_state["dynamic_mode"]

    # Placeholder for additional button logic (✨, 📊)
    with col34:
        if st.button("✨", use_container_width=True):
            pass

    with col35:
        if st.button("📊", use_container_width=True):
            pass
