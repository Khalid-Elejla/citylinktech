import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static


def create_map(df, coordinates):
    m = folium.Map(
        tiles="https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png",
        attr="OpenStreetMap HOT",
    )
    m.fit_bounds(coordinates)

    asterisk_columns = [col for col in df.columns if col.endswith("*")]
    tooltip_col = asterisk_columns[0] if asterisk_columns else None
    asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

    for idx, row in df.iterrows():
        popup_content = "".join(
            f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
        )
        icon_color = "blue" if row.get("Status*", "") == "Closed" else "red"
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"<div><b>{row[tooltip_col]}</b><br>{popup_content}</div>",
            tooltip=row[tooltip_col] if tooltip_col else "",
            icon=folium.Icon(color=icon_color, prefix="fa", icon="lightbulb"),
        ).add_to(m)
    return m


import requests


def construct_osrm_url(start_point, end_point, waypoints):
    """
    Construct the OSRM URL for routing with given start, end, and waypoints.
    """
    coordinates = [start_point] + waypoints + [end_point]
    coordinates_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
    return f"http://router.project-osrm.org/trip/v1/driving/{coordinates_str}?overview=full&geometries=geojson&steps=true&source=first&destination=last&roundtrip=false"


def get_trip_data(osrm_url):
    """
    Get trip data from the OSRM API.
    """
    response = requests.get(osrm_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to get the trip.")


# Helper function to handle map routing logic
def handle_map_routing(coordinates):
    MAX_WAYPOINTS = 100
    if len(coordinates) > MAX_WAYPOINTS:
        st.session_state["warning_message"] = (
            f"The number of waypoints exceeds the OSRM limit of {MAX_WAYPOINTS}. Please reduce the number of locations."
        )
    else:
        osrm_url = construct_osrm_url(
            coordinates[0], coordinates[-1], coordinates[1:-1]
        )
        try:
            trip_data = get_trip_data(osrm_url)
            route_coords = [
                (lat, lon)
                for lon, lat in trip_data["trips"][0]["geometry"]["coordinates"]
            ]
            st.session_state["route_coords"] = route_coords
            st.session_state["warning_message"] = ""  # Clear any previous warnings
            st.rerun()  # Refresh the app to show the route
        except Exception as e:
            st.session_state["warning_message"] = (
                "Failed to fetch route data. Please try again."
            )

#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
def display_map(df):
    coordinates = df[["Latitude", "Longitude"]].values.tolist()
    m = create_map(df, coordinates)

    # Add route if it exists
    if "route_coords" in st.session_state and st.session_state["route_coords"]:
        folium.PolyLine(
            st.session_state["route_coords"], color="blue", weight=2.5, opacity=1
        ).add_to(m)
    folium_static(m)
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
# # Helper function to display map and handle routing
# def display_map(df, coordinates: list) -> None:
#     m = create_map(df, coordinates)

#     # Add route if it exists
#     if st.session_state["route_coords"]:
#         folium.PolyLine(
#             st.session_state["route_coords"], color="blue", weight=2.5, opacity=1
#         ).add_to(m)
#     folium_static(m)
