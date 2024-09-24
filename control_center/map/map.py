import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium, folium_static
from datetime import datetime
from matplotlib import pyplot as plt
from utils.route_utils import construct_osrm_url, get_trip_data
from folium import PolyLine
from st_aggrid import AgGrid, GridOptionsBuilder
from .utils.button_utils import ChkBtnStatusAndAssignColour, render_sheet_buttons
from .utils.data_loader import load_data
from .utils.kpi_calculations import calculate_emergency_kpis, calculate_workforce_kpis
from .utils.map_utils import create_map
from .utils.layout_utils import inject_custom_css


# Main function for the history page
def map_page():

    # inject your custom css style
    inject_custom_css()

    # Load data from Excel
    data_url = "data/data.xlsx"
    sheets_dict = load_data(data_url)
    sheet_names = list(sheets_dict.keys())

    # Initialize session state if not already
    if "selected_sheet_index" not in st.session_state:
        st.session_state.selected_sheet_index = 0
    if "btn_prsd_status" not in st.session_state:
        st.session_state.btn_prsd_status = [False] * len(sheet_names)
    if "dynamic_mode" not in st.session_state:
        st.session_state["dynamic_mode"] = False
    if "route_coords" not in st.session_state:
        st.session_state["route_coords"] = []
    if "warning_message" not in st.session_state:
        st.session_state["warning_message"] = ""

    # Initialize tabs buttons
    render_sheet_buttons(sheet_names, st.session_state)

    # Check if any sheet is selected
    if st.session_state.selected_sheet_index is not None:
        selected_sheet = sheet_names[st.session_state.selected_sheet_index]
        df = sheets_dict[selected_sheet]
        coordinates = df[["Latitude", "Longitude"]].values.tolist()

        if selected_sheet == "Emergency":
            # Call the KPI calculation function
            kpis = calculate_emergency_kpis(df)
            print(kpis)

            # Display the KPIs
            st.write("## Key Performance Indicators (KPIs)")
            col11, col12, col13, col14, col15 = st.columns([1, 1.5, 1, 1, 1.5])
            col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
            col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
            col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
            col14.metric("Emergency Numbers", kpis["Emergency Numbers"])
            col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

        elif selected_sheet == "Workforce":
            # Call the KPI calculation function
            kpis = calculate_workforce_kpis(df)

            # Display the KPIs in Streamlit
            st.write("## Key Performance Indicators (KPIs)")
            col11, col12, col13, col14, col15 = st.columns([1, 1.5, 1, 1, 1.5])
            col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
            col12.metric("Working Hours", kpis["Working Hours"])
            col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}%")
            col14.metric("Complain Numbers", kpis["Complain Numbers"])
            col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")

            # col21, col22, col23 = st.columns([1,2,1])
            # # Display the pie chart in Streamlit
            # with col22:
            #     st.pyplot(kpis['fig'])

        # Display map
        m = create_map(df, coordinates)

        # Add route to the map if it exists
        if st.session_state["route_coords"]:
            PolyLine(
                st.session_state["route_coords"], color="blue", weight=2.5, opacity=1
            ).add_to(m)
        folium_static(m)

        col31, col32, col33, col34, col35, col36 = st.columns([4, 1, 1, 1, 1, 4])
        with col32:
            if st.button("🗺️", use_container_width=True):
                if len(coordinates) >= 2:
                    # Check if number of waypoints exceeds OSRM limit
                    if len(coordinates) > 100:
                        st.session_state["warning_message"] = (
                            "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
                        )
                    else:
                        osrm_url = construct_osrm_url(
                            coordinates[0], coordinates[-1], coordinates[1:-1]
                        )
                        trip_data = get_trip_data(osrm_url)

                        route_coords = trip_data["trips"][0]["geometry"]["coordinates"]
                        route_coords = [(lat, lon) for lon, lat in route_coords]

                        st.session_state["route_coords"] = route_coords
                        st.session_state["warning_message"] = (
                            None  # Clear warning message
                        )

                        # Force a rerun of the app to refresh the map with the new route
                        st.rerun()

        with col33:
            if st.button("🖱️", use_container_width=True):
                st.session_state["dynamic_mode"] = not st.session_state["dynamic_mode"]

        with col34:
            if st.button("✨", use_container_width=True):
                pass

        with col35:
            if st.button("📊", use_container_width=True):
                pass

        if st.session_state["warning_message"]:
            st.warning(
                "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
            )

    # Specify the column you want to filter on (e.g., 'Age')
    filter_column = "Type*"  # Change this to the desired column name

    # Create Grid Options Builder
    # Create Grid Options Builder
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering only for the specified column and hide other column options
    for col in df.columns:
        if col == filter_column:
            gb.configure_column(
                col, filter=True, menuTabs=["filterMenuTab"]
            )  # suppressMenu=False)
        else:
            gb.configure_column(
                col, suppressMenu=True
            )  # Suppress menu for other columns

    # Build grid options and suppress the column selection panel
    gridOptions = gb.build()

    # Display AgGrid with custom column settings
    AgGrid(df, gridOptions=gridOptions, use_container_width=True)

    # Apply the correct button colors after rendering the buttons
    ChkBtnStatusAndAssignColour(sheet_names, st.session_state)
