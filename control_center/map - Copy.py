import streamlit as st
import folium
import pandas as pd
from streamlit_folium import folium_static, st_folium
from utils.route_utils import construct_osrm_url, get_trip_data
import os
from folium import Icon, PolyLine
from datetime import datetime, time
from matplotlib import pyplot as plt
import numpy as np



# KPI calculations for Emergency data
# def calculate_emergency_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Helper function to parse time
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     # Fix serialization issue: convert datetime columns to strings
#     df_copy['Open Time'] = df_copy['Open Time'].astype(str)
#     df_copy['Closure Time'] = df_copy['Closure Time'].astype(str)

#     emergency_closure_time = (pd.to_datetime(df_copy['Closure Time']) - pd.to_datetime(df_copy['Open Time'])).mean()
#     emergency_closure_time_str = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'satisfied').mean() * 100
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     expected_emergency_alarm = "To be calculated based on relationships"

#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time_str,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# KPI calculations for Workforce data
# def calculate_workforce_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     # Fix serialization issue: convert datetime columns to strings
#     df_copy['Open Time'] = df_copy['Open Time'].astype(str)
#     df_copy['Closure Time'] = df_copy['Closure Time'].astype(str)

#     working_hours = (pd.to_datetime(df_copy['Closure Time']) - pd.to_datetime(df_copy['Open Time'])).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     evaluation_rate = df_copy['Evaluation'].sum() / total_operations if total_operations > 0 else 0
#     complain_numbers = df_copy['Complain Today'].sum()

#     operation_counts = df_copy['Operation'].value_counts()
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.pie(operation_counts, labels=operation_counts.index, autopct='%1.1f%%', startangle=90, textprops={'color': 'black'})
#     ax.axis('equal')
#     plt.title('Operations Status Distribution')

#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complaints Alarm": "To be calculated based on relationships",
#         "fig": fig
#     }

def calculate_emergency_kpis(df):
    # Strip trailing '*' from column names
    df_copy = df.copy()
    df_copy.columns = df_copy.columns.str.rstrip('*')

    # Check if required columns exist
    required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
    for col in required_columns:
        if col not in df_copy.columns:
            raise ValueError(f"Column '{col}' is missing from the DataFrame")

    today = datetime.today().date()

    # Function to parse time whether it includes seconds or not
    def parse_time(t):
        try:
            return pd.to_datetime(t, format='%H:%M:%S').time()
        except ValueError:
            try:
                return pd.to_datetime(t, format='%H:%M').time()
            except ValueError:
                raise ValueError(f"Time format for '{t}' is incorrect")

    # Ensure 'Open Time' and 'Closure Time' are in time format
    df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
    df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

    # Combine with today's date to create datetime objects
    df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
    df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

    # Calculate the mean emergency closure time
    # emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
    emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
    emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

    # Calculate Closure Percentage
    closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100

    # Calculate Satisfaction Rate
    satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

    # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
    df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
    emergency_numbers = df_copy['Location'].nunique()

    # Placeholder for Expected Emergency Alarm
    expected_emergency_alarm = "To be calculated based on relationships"

    # Return a dictionary with all the calculated KPIs
    return {
        "Closure Percentage": closure_percentage,
        "Emergency Closure Time": emergency_closure_time,
        "Satisfaction Rate": satisfaction_rate,
        "Emergency Numbers": emergency_numbers,
        "Expected Emergency Alarm": expected_emergency_alarm
    }

def calculate_workforce_kpis(df):
    # Strip trailing '*' from column names
    df_copy = df.copy(deep=False)
    df_copy.columns = df_copy.columns.str.rstrip('*')

    # Check if required columns exist
    required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
    for col in required_columns:
        if col not in df_copy.columns:
            raise ValueError(f"Column '{col}' is missing from the DataFrame")

    today = datetime.today().date()

    # Function to parse time whether it includes seconds or not
    def parse_time(t):
        try:
            return pd.to_datetime(t, format='%H:%M:%S').time()
        except ValueError:
            try:
                return pd.to_datetime(t, format='%H:%M').time()
            except ValueError:
                raise ValueError(f"Time format for '{t}' is incorrect")

    # Ensure 'Open Time' and 'Closure Time' are in time format
    df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
    df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

    # Combine with today's date to create datetime objects
    df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
    df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

    # Calculate the average working hours
    working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
    working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

    # Calculate Operation Percentage (Active/Total)
    total_operations = len(df_copy)
    active_operations = (df_copy['Status'] == 'Active').sum()
    operation_percentage = (active_operations / total_operations) * 100

    # Calculate Evaluation Rate
    total_evaluations = df_copy['Evaluation'].sum()
    total_responses = len(df_copy)
    evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

    # Calculate Complain Numbers
    complain_numbers = df_copy['Complain Today'].sum()

    # Placeholder for Expected Complaints Alarm
    expected_complains_alarm = "To be calculated based on relationships"



    # Generate Pie Chart for Operations
    status_counts = df_copy['Operation'].value_counts()  # Group by status and count
    fig, ax = plt.subplots(figsize=(1, 1))

    # Set figure and axes backgrounds to transparent
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white', 'fontsize': 4})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Operations Status Distribution')

    # # Display the pie chart in Streamlit
    # st.pyplot(fig)

    # Return a dictionary with all the calculated KPIs
    return {
        "Operation Percentage": operation_percentage,
        "Working Hours": working_hours_str,
        "Evaluation Rate": evaluation_rate,
        "Complain Numbers": complain_numbers,
        "Expected Complains Alarm": expected_complains_alarm,
        "fig": fig,
    }


# Load data from Excel
def load_data(file_path):
    return pd.read_excel(file_path, sheet_name=None)


def calculate_zoom_level(lat_min, lat_max, lon_min, lon_max, map_width=1000, map_height=800):
        TILE_SIZE = 256
        ZOOM_MAX = 18

        lat_diff = lat_max - lat_min
        lon_diff = lon_max - lon_min

        # Approximate the number of tiles required
        lat_zoom = np.log2((TILE_SIZE * map_height) / lat_diff)
        lon_zoom = np.log2((TILE_SIZE * map_width) / lon_diff)

        # Return the minimum zoom level within bounds
        return min(max(min(lat_zoom, lon_zoom), 1), ZOOM_MAX)


# Create a Folium map
def create_map(df):
    # calculate center and zoom level
    coordinates = df[['Latitude', 'Longitude']].values.tolist()
    coordinates_np=np.array(coordinates)
    center_lat = np.mean(coordinates_np[:, 0])
    center_lon = np.mean(coordinates_np[:, 1])

    # Calculate bounding box
    lat_min, lat_max = np.min(coordinates_np[:, 0]), np.max(coordinates_np[:, 0])
    lon_min, lon_max = np.min(coordinates_np[:, 1]), np.max(coordinates_np[:, 1])

    zoom_level = calculate_zoom_level(lat_min, lat_max, lon_min, lon_max)


    m = folium.Map(
        tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap HOT',
        location=[center_lat,center_lon],
        zoom_start=zoom_level
    )
    m.fit_bounds(coordinates)


    asterisk_columns = [col for col in df.columns if col.endswith('*')]
    tooltip_col = asterisk_columns[0] if asterisk_columns else None
    asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

    for idx, row in df.iterrows():
        popup_content = "".join(
            f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
        )
        icon_color = 'blue'
        if 'Status*' in row:
            if row['Status*'] in ['Open', 'Inactive']:
                icon_color = 'red'
            elif row['Status*'] in ['Closed', 'Active']:
                icon_color = 'green'
            elif row['Status*'] in ['Ongoing']:
                icon_color = 'blue'
        
        marker_id = f"marker_{idx}"
        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"""
                <div>
                    <b>{row[tooltip_col]}</b><br>
                    {popup_content}
                    <br><br>
                    <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
                </div>
            """,
            tooltip=row[tooltip_col] if tooltip_col else '',
            icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
        )
        marker.add_to(m)
        
        # # Add marker coordinates to bounds list
        # bounds.append([row['Latitude'], row['Longitude']])
        # print(bounds)

    # bounds=[ [29.8319695215679, 31.3584769525776], [29.8699487797015, 31.3517904123072], [29.8699487797015, 31.3517904123072]]
    # # Fit the map to the bounds of all markers
    # if bounds:
    #     m.fit_bounds(bounds)

    return m
def create_map_alternative(df):
    # Calculate the center of all points
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()

    # Calculate the maximum distance from the center
    max_distance = max(
        df.apply(lambda row: ((row['Latitude'] - center_lat)**2 + 
                              (row['Longitude'] - center_lon)**2)**0.5, axis=1)
    )

    # Create the map centered on the calculated point
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # Add markers (same as before)
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Latitude']}, {row['Longitude']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Adjust zoom level based on the maximum distance
    m.fit_bounds([[center_lat - max_distance, center_lon - max_distance],
                  [center_lat + max_distance, center_lon + max_distance]])

    return m

# Main map page
def map_page():
    if 'selected_sheet' not in st.session_state:
        st.session_state['selected_sheet'] = None
        # Initialize session state if not already
    if 'dynamic_mode' not in st.session_state:
        st.session_state['dynamic_mode'] = False
    if 'route_coords' not in st.session_state:
        st.session_state['route_coords'] = []

    data_url = 'data/data.xlsx'
    sheets_dict = load_data(data_url)
    sheet_names = list(sheets_dict.keys())

    st.markdown("""
        <style>
        [class="menu-item active"]{
                border: 3px;
                
                }
.menu-item.active{
                
display:none !important;                }
        .stTabs [role="tablist"] {
            display: flex;
            justify-content: space-evenly;
            flex-wrap: wrap;
        }
        .stTabs button {
            flex-grow: 1;
            flex-basis: 0;
            text-align: center;
        }
        .element-container iframe {
        width: 100% !important;
        height: 600px;  /* Adjust the height as needed */
        }
        </style>
    """, unsafe_allow_html=True)
    
    
                
    tab_names = [f"{sheet}" for sheet in sheet_names]
    tabs = st.tabs(tab_names)

    for i, tab in enumerate(tabs):
        with tab:
            selected_sheet = sheet_names[i]

            df = sheets_dict[selected_sheet]
            # Force re-render on tab switch
            if st.session_state['selected_sheet'] != selected_sheet:
                st.session_state['selected_sheet'] = selected_sheet

            df = sheets_dict[selected_sheet]
            coordinates = df[['Latitude', 'Longitude']].values.tolist()



            _, col1, col2 = st.columns([4, 1, 1], gap="small", vertical_alignment="bottom")

            with col1:
                if st.button('🗺️', key=f"best_route{i}"):
                    if len(coordinates) >= 2:
                        # Check if number of waypoints exceeds OSRM limit
                        if len(coordinates) > 100:
                            st.session_state['warning_message'] = "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
                        else:
                            osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
                            trip_data = get_trip_data(osrm_url)

                            route_coords = trip_data['trips'][0]['geometry']['coordinates']
                            route_coords = [(lat, lon) for lon, lat in route_coords]

                            st.session_state['route_coords'] = route_coords
                            st.session_state['warning_message'] = None  # Clear warning message

            with col2:
                if st.button("🖱️",key=f"dynamic_mode{i}"):
                    st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']

            if selected_sheet == 'Emergency':
                kpis = calculate_emergency_kpis(df)
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                col1.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
                col2.metric("Emergency Closure Time", kpis['Emergency Closure Time'])
                col3.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
                col4.metric("Emergency Numbers", kpis['Emergency Numbers'])
                col5.metric("Expected Emergency Alarm", kpis['Expected Emergency Alarm'])

            elif selected_sheet == 'Workforce':
                kpis = calculate_workforce_kpis(df)
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                col1.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
                col2.metric("Working Hours", kpis['Working Hours'])
                col3.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
                col4.metric("Complain Numbers", kpis['Complain Numbers'])
                # col5.metric("Expected Complaints Alarm", kpis['Expected Complaints Alarm'])
                # st.pyplot(kpis['fig'])


            # In your map_page function, replace create_map with create_map_alternative
            # folium_map = create_map_alternative(df)
            folium_map = create_map(df)
            
            #folium_map = create_map(df)
            # st_folium(folium_map)
            # fit_bounds([[52.193636, -2.221575], [52.636878, -1.139759]])

            folium_static(folium_map)


            # Add route to the map if it exists
            if st.session_state['route_coords']:
                PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(folium_map)

            # Display the DataFrame table under the map
            st.subheader(f"Data for {selected_sheet}")
            st.dataframe(df,use_container_width=True)

# Main Streamlit app
def main():
    map_page

#####################################################################################################################
# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import folium_static
# from folium import Icon
# from datetime import datetime
# from matplotlib import pyplot as plt

# # Helper function to parse time
# def parse_time(t):
#     try:
#         return pd.to_datetime(t, format='%H:%M:%S').time()
#     except ValueError:
#         try:
#             return pd.to_datetime(t, format='%H:%M').time()
#         except ValueError:
#             raise ValueError(f"Time format for '{t}' is incorrect")

# # KPI calculations for Emergency data
# def calculate_emergency_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time_str = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'satisfied').mean() * 100
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     expected_emergency_alarm = "To be calculated based on relationships"

#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time_str,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# # KPI calculations for Workforce data
# def calculate_workforce_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     evaluation_rate = df_copy['Evaluation'].sum() / total_operations if total_operations > 0 else 0
#     complain_numbers = df_copy['Complain Today'].sum()

#     operation_counts = df_copy['Operation'].value_counts()
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.pie(operation_counts, labels=operation_counts.index, autopct='%1.1f%%', startangle=90, textprops={'color': 'black'})
#     ax.axis('equal')
#     plt.title('Operations Status Distribution')

#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complaints Alarm": "To be calculated based on relationships",
#         "fig": fig
#     }

# # Load data from Excel
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)

# # Create a Folium map
# def create_map(df):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     # Initialize bounds list
#     bounds = []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
#         icon_color = 'blue'
#         if 'Status*' in row:
#             if row['Status*'] in ['Open', 'Inactive']:
#                 icon_color = 'red'
#             elif row['Status*'] in ['Closed', 'Active']:
#                 icon_color = 'green'
#             elif row['Status*'] in ['Ongoing']:
#                 icon_color = 'blue'
        
#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)
        
#         # Add marker coordinates to bounds list
#         bounds.append([row['Latitude'], row['Longitude']])

#     # Fit the map to the bounds of all markers
#     if bounds:
#         m.fit_bounds(bounds)

#     return m

# # Main map page
# def map_page():
#     if 'selected_sheet' not in st.session_state:
#         st.session_state['selected_sheet'] = None

#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     st.markdown("""
#         <style>
#         .stTabs [role="tablist"] {
#             display: flex;
#             justify-content: space-evenly;
#             flex-wrap: wrap;
#         }
#         .stTabs button {
#             flex-grow: 1;
#             flex-basis: 0;
#             text-align: center;
#         }
#         .element-container iframe {
#         width: 100% !important;
#         height: 600px;  /* Adjust the height as needed */
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     tab_names = [f"{sheet}" for sheet in sheet_names]
#     tabs = st.tabs(tab_names)

#     for i, tab in enumerate(tabs):
#         with tab:
#             selected_sheet = sheet_names[i]

#             df = sheets_dict[selected_sheet]
#             # Force re-render on tab switch
#             print(f"session_state {st.session_state['selected_sheet']} and selected_sheet {selected_sheet}")
#             if st.session_state['selected_sheet'] != selected_sheet:
#                 st.session_state['selected_sheet'] = selected_sheet

#             df = sheets_dict[selected_sheet]

#             if selected_sheet == 'Emergency':
#                 kpis = calculate_emergency_kpis(df)
#                 col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
#                 col1.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
#                 col2.metric("Emergency Closure Time", kpis['Emergency Closure Time'])
#                 col3.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
#                 col4.metric("Emergency Numbers", kpis['Emergency Numbers'])
#                 col5.metric("Expected Emergency Alarm", kpis['Expected Emergency Alarm'])

#             elif selected_sheet == 'Workforce':
#                 kpis = calculate_workforce_kpis(df)
#                 col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
#                 col1.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
#                 col2.metric("Working Hours", kpis['Working Hours'])
#                 col3.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
#                 col4.metric("Complain Numbers", kpis['Complain Numbers'])
#                 col5.metric("Expected Complaints Alarm", kpis['Expected Complaints Alarm'])
#                 _, col22, _ = st.columns([1, 1.5, 1])
#                 # Display the pie chart in Streamlit
#                 # with col22:
#                 #     st.pyplot(kpis['fig'])

#             # Create and display the map
#             m = create_map(df)
#             folium_static(m)

#             # Display the DataFrame table under the map
#             st.subheader(f"Data for {selected_sheet}")
#             st.dataframe(df,use_container_width=True)

# # Main Streamlit app
# def main():
#     map_page
##############################################################################################################################$#
# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import folium_static
# from folium import Icon
# from datetime import datetime
# from matplotlib import pyplot as plt

# # Helper function to parse time
# def parse_time(t):
#     try:
#         return pd.to_datetime(t, format='%H:%M:%S').time()
#     except ValueError:
#         try:
#             return pd.to_datetime(t, format='%H:%M').time()
#         except ValueError:
#             raise ValueError(f"Time format for '{t}' is incorrect")

# # KPI calculations for Emergency data
# def calculate_emergency_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time_str = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'satisfied').mean() * 100
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     expected_emergency_alarm = "To be calculated based on relationships"

#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time_str,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# # KPI calculations for Workforce data
# def calculate_workforce_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, parse_time(x)))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, parse_time(x)))

#     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     evaluation_rate = df_copy['Evaluation'].sum() / total_operations if total_operations > 0 else 0
#     complain_numbers = df_copy['Complain Today'].sum()

#     operation_counts = df_copy['Operation'].value_counts()
#     fig, ax = plt.subplots(figsize=(6, 6))
#     ax.pie(operation_counts, labels=operation_counts.index, autopct='%1.1f%%', startangle=90, textprops={'color': 'black'})
#     ax.axis('equal')
#     plt.title('Operations Status Distribution')

#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complaints Alarm": "To be calculated based on relationships",
#         "fig": fig
#     }

# # Load data from Excel
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)

# # Create a Folium map
# def create_map(df):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     # Initialize bounds list
#     bounds = []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
#         icon_color = 'blue'
#         if 'Status*' in row:
#             if row['Status*'] in ['Open', 'Inactive']:
#                 icon_color = 'red'
#             elif row['Status*'] in ['Closed', 'Active']:
#                 icon_color = 'green'
#             elif row['Status*'] in ['Ongoing']:
#                 icon_color = 'blue'
        
#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)
        
#         # Add marker coordinates to bounds list
#         bounds.append([row['Latitude'], row['Longitude']])

#     # Fit the map to the bounds of all markers
#     if bounds:
#         m.fit_bounds(bounds)

#     return m

# # Main map page
# def map_page():
#     if 'selected_sheet' not in st.session_state:
#         st.session_state['selected_sheet'] = None

#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     st.markdown("""
#         <style>
#         .stTabs [role="tablist"] {
#             display: flex;
#             justify-content: space-evenly;
#             flex-wrap: wrap;
#         }
#         .stTabs button {
#             flex-grow: 1;
#             flex-basis: 0;
#             text-align: center;
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     tab_names = [f"{sheet}" for sheet in sheet_names]
#     tabs = st.tabs(tab_names)

#     for i, tab in enumerate(tabs):
#         with tab:
#             if st.session_state['selected_sheet'] != sheet_names[i]:
#                 st.session_state['selected_sheet'] = sheet_names[i]
            
#             selected_sheet = sheet_names[i]
#             df = sheets_dict[selected_sheet]

#             if selected_sheet == 'Emergency':
#                 kpis = calculate_emergency_kpis(df)
#                 col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
#                 col1.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
#                 col2.metric("Emergency Closure Time", kpis['Emergency Closure Time'])
#                 col3.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
#                 col4.metric("Emergency Numbers", kpis['Emergency Numbers'])
#                 col5.metric("Expected Emergency Alarm", kpis['Expected Emergency Alarm'])

#             elif selected_sheet == 'Workforce':
#                 kpis = calculate_workforce_kpis(df)
#                 col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
#                 col1.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
#                 col2.metric("Working Hours", kpis['Working Hours'])
#                 col3.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
#                 col4.metric("Complain Numbers", kpis['Complain Numbers'])
#                 col5.metric("Expected Complaints Alarm", kpis['Expected Complaints Alarm'])
#                 _, col22,_ = st.columns([1,1.5,1])
#                 # Display the pie chart in Streamlit
#                 with col22:
#                     st.pyplot(kpis['fig'])

#             # Create and display the map
#             m = create_map(df)

#             folium_static(m, width=1024, height=600)

#             st.dataframe(df)

# # Main page
# def main_page():
#     st.title("Main Application Page")
#     map_page()

# # Main script
# if __name__ == "__main__":
#     main_page()




# def map_page():
#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Load data from a single Excel file called "data.xlsx"
#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     # Calculate center coordinates for the map
#     coordinates = []
#     for sheet_df in sheets_dict.values():
#         coordinates += sheet_df[['Latitude', 'Longitude']].values.tolist()

#     center_coordinates = [sum(x) / len(x) for x in zip(*coordinates)]

#     # Create a Folium map using the center coordinates
#     m = create_map(pd.concat(sheets_dict.values()), [center_coordinates])


#     # Custom CSS to expand the tabs
#     st.markdown("""
#         <style>
#         .stTabs [role="tablist"] {
#             display: flex;
#             justify-content: space-evenly;
#             flex-wrap: wrap;
#         }
#         .stTabs button {
#             flex-grow: 1;
#             flex-basis: 0;
#             text-align: center;
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     # Replace dropdown menu with tabs
#     tab_names = [f"{sheet}" for sheet in sheet_names]
#     tabs = st.tabs(tab_names)

#     for i, tab in enumerate(tabs):
#         with tab:
#             # st.write(f"Showing data for {sheet_names[i]} sheet")
#             df = sheets_dict[sheet_names[i]]


#             # Display KPI metrics depending on the sheet name
#             if sheet_names[i] == 'Emergency':
#                 kpis = calculate_Emergency_kpis(df)
#                 col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
#                 col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
#                 col12.metric("Emergency Closure Time", kpis['Emergency Closure Time'])
#                 col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
#                 col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
#                 col15.metric("Expected Emergency Alarm", kpis['Expected Emergency Alarm'])

#             elif sheet_names[i] == 'Workforce':
#                 kpis = calculate_workforce_kpis(df)
#                 col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
#                 col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
#                 col12.metric("Working Hours", kpis['Working Hours'])
#                 col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
#                 col14.metric("Complain Numbers", kpis['Complain Numbers'])
#                 col15.metric("Expected Complains Alarm", kpis['Expected Complains Alarm'])
#                 # Display the pie char4
#                 st.pyplot(kpis['fig'])


#     # Display the Folium map
#     folium_static(m, width=800, height=600)

#     # Display the dataframe in the app
#     st.dataframe(df)

# # Main Page
# def main_page():
#     st.title("Main Application Page")
#     map_page()

# # Main script
# if __name__ == "__main__":
#     main_page()
#################################################################
# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os
# from datetime import datetime, time
# from matplotlib import pyplot as plt

# def calculate_Emergency_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the mean emergency closure time
#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     # Calculate Closure Percentage
#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100

#     # Calculate Satisfaction Rate
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

#     # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     # Placeholder for Expected Emergency Alarm
#     expected_emergency_alarm = "To be calculated based on relationships"

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# def calculate_workforce_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy(deep=False)
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the average working hours
#     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     # Calculate Operation Percentage (Active/Total)
#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     # Calculate Evaluation Rate
#     total_evaluations = df_copy['Evaluation'].sum()
#     total_responses = len(df_copy)
#     evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

#     # Calculate Complain Numbers
#     complain_numbers = df_copy['Complain Today'].sum()

#     # Placeholder for Expected Complaints Alarm
#     expected_complains_alarm = "To be calculated based on relationships"

#     # Generate Pie Chart for Operations
#     status_counts = df_copy['Operation'].value_counts()  # Group by status and count
#     fig, ax = plt.subplots(figsize=(1, 1))

#     # Set figure and axes backgrounds to transparent
#     fig.patch.set_facecolor('none')
#     ax.set_facecolor('none')

#     ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white', 'fontsize': 4})
#     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     plt.title('Operations Status Distribution')

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complains Alarm": expected_complains_alarm,
#         "fig": fig,
#     }


# # Load data from the specified Excel file
# @st.cache_data(show_spinner=False)
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dict

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )
#     m.fit_bounds(coordinates)

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None

#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#         if 'Status*' in row:
#             if row['Status*'] in ['Open', 'Inactive']:
#                 icon_color = 'red'
#             elif row['Status*'] in ['Closed', 'Active']:
#                 icon_color = 'green'
#             elif row['Status*'] in ['Ongoing']:
#                 icon_color = 'blue'
#         else:
#             icon_color = 'blue'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Load data from a single Excel file called "data.xlsx"
#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     # Use tabs to select the sheet
#     tab_dict = {sheet: st.tab(sheet) for sheet in sheet_names}
    
#     # Iterate over the tabs
#     for sheet_name, tab in tab_dict.items():
#         with tab:
#             df = sheets_dict[sheet_name]
#             st.write(f"**{sheet_name} Sheet Data**")
#             st.dataframe(df)

#             kpis = {}
#             if sheet_name == 'Emergency KPIs':
#                 kpis = calculate_Emergency_kpis(df)
#             elif sheet_name == 'Workforce KPIs':
#                 kpis = calculate_workforce_kpis(df)

#             # Display the KPIs
#             st.write("### KPIs")
#             st.write(f"- Closure Percentage: {kpis.get('Closure Percentage', 'N/A')}%")
#             st.write(f"- Emergency Closure Time: {kpis.get('Emergency Closure Time', 'N/A')}")
#             st.write(f"- Satisfaction Rate: {kpis.get('Satisfaction Rate', 'N/A')}%")
#             st.write(f"- Emergency Numbers: {kpis.get('Emergency Numbers', 'N/A')}")
#             st.write(f"- Expected Emergency Alarm: {kpis.get('Expected Emergency Alarm', 'N/A')}")
#             st.write(f"- Operation Percentage: {kpis.get('Operation Percentage', 'N/A')}%")
#             st.write(f"- Working Hours: {kpis.get('Working Hours', 'N/A')}")
#             st.write(f"- Evaluation Rate: {kpis.get('Evaluation Rate', 'N/A')}")
#             st.write(f"- Complain Numbers: {kpis.get('Complain Numbers', 'N/A')}")
#             st.write(f"- Expected Complains Alarm: {kpis.get('Expected Complains Alarm', 'N/A')}")
            
#             # Plot the pie chart for operations
#             fig = kpis.get('fig')
#             if fig:
#                 st.pyplot(fig)
            
#             # Create and display the map
#             coordinates = [[row['Latitude'], row['Longitude']] for idx, row in df.iterrows()]
#             if coordinates:
#                 m = create_map(df, coordinates)
#                 folium_static(m)


# if __name__ == '__main__':
#     st.set_page_config(page_title='GIS KPIs and Map Viewer', layout="wide")
#     st.sidebar.title('Navigation')
    
#     app_mode = st.sidebar.selectbox('Choose the app mode', ['Map Viewer'])
    
#     if app_mode == 'Map Viewer':
#         map_page()


# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os
# from datetime import datetime, time
# from matplotlib import pyplot as plt



# def calculate_Emergency_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",df_copy.columns)
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the mean emergency closure time
#     # emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     # Calculate Closure Percentage
#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100

#     # Calculate Satisfaction Rate
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

#     # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     # Placeholder for Expected Emergency Alarm
#     expected_emergency_alarm = "To be calculated based on relationships"

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# def calculate_workforce_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy(deep=False)
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the average working hours
#     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     # Calculate Operation Percentage (Active/Total)
#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     # Calculate Evaluation Rate
#     total_evaluations = df_copy['Evaluation'].sum()
#     total_responses = len(df_copy)
#     evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

#     # Calculate Complain Numbers
#     complain_numbers = df_copy['Complain Today'].sum()

#     # Placeholder for Expected Complaints Alarm
#     expected_complains_alarm = "To be calculated based on relationships"



#     # Generate Pie Chart for Operations
#     status_counts = df_copy['Operation'].value_counts()  # Group by status and count
#     fig, ax = plt.subplots(figsize=(1, 1))

#     # Set figure and axes backgrounds to transparent
#     fig.patch.set_facecolor('none')
#     ax.set_facecolor('none')

#     ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white', 'fontsize': 4})
#     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     plt.title('Operations Status Distribution')

#     # # Display the pie chart in Streamlit
#     # st.pyplot(fig)

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complains Alarm": expected_complains_alarm,
#         "fig": fig,
#     }


# # Load data from the specified Excel file
# @st.cache_data(show_spinner=False)
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dict

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )
#     m.fit_bounds(coordinates)

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None

#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#         if 'Status*' in row:
#             if row['Status*'] in ['Open', 'Inactive']:
#                 icon_color = 'red'
#             elif row['Status*'] in ['Closed', 'Active']:
#                 icon_color = 'green'
#             elif row['Status*'] in ['Ongoing']:
#                 icon_color = 'blue'
#         else:
#             icon_color = 'blue'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Load data from a single Excel file called "data.xlsx"
#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     # Use a single dropdown menu to select the sheet
#     selected_sheet = st.selectbox('Select Sheet', sheet_names)

#     df = sheets_dict[selected_sheet]
#     print(df.columns)
#     coordinates = df[['Latitude', 'Longitude']].values.tolist()

#     # Check the selected sheet and calculate KPIs accordingly
#     if selected_sheet == "Emergency":
#         kpis = calculate_Emergency_kpis(df)
#         st.write("## Key Performance Indicators (KPIs)")
#         col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
#         col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
#         col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
#         col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
#         col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
#         col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

#     elif selected_sheet == "Workforce":
#         kpis = calculate_workforce_kpis(df)
#         st.write("## Key Performance Indicators (KPIs)")
#         col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
#         col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
#         col12.metric("Working Hours", kpis['Working Hours'])
#         col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
#         col14.metric("Complain Numbers", kpis['Complain Numbers'])
#         col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")

#         col21, col22, col23 = st.columns([1, 2, 1])
#         with col22:
#             st.pyplot(kpis['fig'])

#     # Create the map with markers
#     m = create_map(df, coordinates)

#     # Add route to the map if it exists
#     if st.session_state['route_coords']:
#         PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

#     # Conditionally render the map based on mode
#     if st.session_state['dynamic_mode']:
#         st_data = st_folium(m, height=500, width=1040)
#     else:
#         st_data = folium_static(m, height=500, width=1040)

#     # Handle marker clicks in dynamic mode
#     if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
#         st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

#     # Display data table with collapsible view
#     with st.expander(f'{selected_sheet} Table', expanded=True):
#         st.dataframe(df, width=950, height=300)

#     # Display warning message in the sidebar if it exists
#     if 'warning_message' in st.session_state and st.session_state['warning_message']:
#         st.sidebar.warning(st.session_state['warning_message'])

# # Run the map page
# map_page()
#########################################################



# import streamlit as st
# import folium
# import pandas as pd
# from streamlit_folium import st_folium, folium_static
# from folium import PolyLine
# from utils.route_utils import construct_osrm_url, get_trip_data
# import os
# from datetime import datetime, time
# from matplotlib import pyplot as plt

# def calculate_Emergency_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open Time' and 'Closure Time' are in time format
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the mean emergency closure time
#     # emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     # Calculate Closure Percentage
#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100

#     # Calculate Satisfaction Rate
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

#     # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
#     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
#     emergency_numbers = df_copy['Location'].nunique()

#     # Placeholder for Expected Emergency Alarm
#     expected_emergency_alarm = "To be calculated based on relationships"

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": expected_emergency_alarm
#     }

# def calculate_workforce_kpis(df):
#     # Strip trailing '*' from column names
#     df_copy = df.copy(deep=False)
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Check if required columns exist
#     required_columns = ['Open-Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     for col in required_columns:
#         if col not in df_copy.columns:
#             raise ValueError(f"Column '{col}' is missing from the DataFrame")

#     today = datetime.today().date()

#     # Function to parse time whether it includes seconds or not
#     def parse_time(t):
#         try:
#             return pd.to_datetime(t, format='%H:%M:%S').time()
#         except ValueError:
#             try:
#                 return pd.to_datetime(t, format='%H:%M').time()
#             except ValueError:
#                 raise ValueError(f"Time format for '{t}' is incorrect")

#     # Ensure 'Open-Time' and 'Closure Time' are in time format
#     df_copy['Open-Time'] = df_copy['Open-Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     # Combine with today's date to create datetime objects
#     df_copy['Open-Time'] = df_copy['Open-Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate the average working hours
#     working_hours = (df_copy['Closure Time'] - df_copy['Open-Time']).mean()
#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     # Calculate Operation Percentage (Active/Total)
#     total_operations = len(df_copy)
#     active_operations = (df_copy['Status'] == 'Active').sum()
#     operation_percentage = (active_operations / total_operations) * 100

#     # Calculate Evaluation Rate
#     total_evaluations = df_copy['Evaluation'].sum()
#     total_responses = len(df_copy)
#     evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

#     # Calculate Complain Numbers
#     complain_numbers = df_copy['Complain Today'].sum()

#     # Placeholder for Expected Complaints Alarm
#     expected_complains_alarm = "To be calculated based on relationships"



#     # Generate Pie Chart for Operations
#     status_counts = df_copy['Operation'].value_counts()  # Group by status and count
#     fig, ax = plt.subplots(figsize=(1, 1))

#     # Set figure and axes backgrounds to transparent
#     fig.patch.set_facecolor('none')
#     ax.set_facecolor('none')

#     ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white', 'fontsize': 4})
#     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     plt.title('Operations Status Distribution')

#     # # Display the pie chart in Streamlit
#     # st.pyplot(fig)

#     # Return a dictionary with all the calculated KPIs
#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complains Alarm": expected_complains_alarm,
#         "fig": fig,
#     }





# # Load data from Excel, including multiple sheets
# def load_data(data_url):
#     return pd.read_excel(data_url, sheet_name=None)  # Load all sheets into a dict

# # Cache the creation of the map with all markers
# @st.cache_data(show_spinner=False)
# def create_map(df, coordinates):
#     m = folium.Map(
#         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
#         attr='OpenStreetMap HOT'
#     )
#     m.fit_bounds(coordinates)

#     asterisk_columns = [col for col in df.columns if col.endswith('*')]
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAA",df.columns)
#     tooltip_col = asterisk_columns[0] if asterisk_columns else None
#     print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",tooltip_col)
#     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
#         )
        
#         if 'Status*' in row:
#             icon_color = 'blue' if row['Status*'] == 'Closed' else 'red'    
#         else:
#             icon_color = 'blue'

#         marker_id = f"marker_{idx}"
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"""
#                 <div>
#                     <b>{row[tooltip_col]}</b><br>
#                     {popup_content}
#                     <br><br>
#                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
#                 </div>
#             """,
#             tooltip=row[tooltip_col] if tooltip_col else '',
#             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
#         )
#         marker.add_to(m)

#     return m

# def map_page():
#     # List files in the data folder
#     data_folder = 'data'
#     files = [f for f in os.listdir(data_folder) if f.endswith('.xlsx') and not f.startswith('~$')]
#     file_options = [os.path.splitext(f)[0] for f in files]  # Remove file extension

#     # Initialize session state if not already
#     if 'dynamic_mode' not in st.session_state:
#         st.session_state['dynamic_mode'] = False
#     if 'route_coords' not in st.session_state:
#         st.session_state['route_coords'] = []

#     # Columns layout
#     col1, col2, col3, col4, col5, col6 = st.columns([3, 7, 6,4, 1, 1], gap="small", vertical_alignment="bottom")

#     with col1:
#         st.write('Select System')

#     with col2:
#         selected_file = st.selectbox('Select System', file_options, label_visibility="collapsed")

#     # Check if a file has been selected
#     if selected_file:
#         data_url = os.path.join(data_folder, f"{selected_file}.xlsx")
#         sheets_dict = load_data(data_url)
#         sheet_names = list(sheets_dict.keys())

#         with col3:
#             selected_sheet = st.selectbox('Select Sheet', sheet_names)

#         df = sheets_dict[selected_sheet]
#         coordinates = df[['Latitude', 'Longitude']].values.tolist()

#         # Extract the file name without extension for the header
#         file_name = selected_file.capitalize()

#         with col5:
#             if st.button('🗺️'):
#                 if len(coordinates) >= 2:
#                     # Check if number of waypoints exceeds OSRM limit
#                     if len(coordinates) > 100:
#                         st.session_state['warning_message'] = "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
#                     else:
#                         osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
#                         trip_data = get_trip_data(osrm_url)

#                         route_coords = trip_data['trips'][0]['geometry']['coordinates']
#                         route_coords = [(lat, lon) for lon, lat in route_coords]

#                         st.session_state['route_coords'] = route_coords
#                         st.session_state['warning_message'] = None  # Clear warning message

#         with col6:
#             if st.button("🖱️"):
#                 st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']


#         if selected_sheet == "Emergency" :
#                 # Call the KPI calculation function
#                 kpis = calculate_Emergency_kpis(df)

#                 # Display the KPIs
#                 st.write("## Key Performance Indicators (KPIs)")
#                 col11, col12, col13, col14, col15 = st.columns([1,2,1,1,1])
#                 col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
#                 col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
#                 col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
#                 col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
#                 col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

#         elif selected_sheet == "Workforce" :
#             # Call the KPI calculation function
#             kpis = calculate_workforce_kpis(df)

#             # Display the KPIs in Streamlit
#             st.write("## Key Performance Indicators (KPIs)")
#             col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
#             col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
#             col12.metric("Working Hours", kpis['Working Hours'])
#             col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
#             col14.metric("Complain Numbers", kpis['Complain Numbers'])
#             col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")


#             col21, col22, col23 = st.columns([1,2,1])
#             # # Display the pie chart in Streamlit
#             with col22:
#                 st.pyplot(kpis['fig'])

#         # Create the map with markers
#         m = create_map(df, coordinates)

#         # Add route to the map if it exists
#         if st.session_state['route_coords']:
#             PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

#         # Conditionally render the map based on mode
#         if st.session_state['dynamic_mode']:
#             st_data = st_folium(m, height=500, width=1040)
#         else:
#             st_data = folium_static(m, height=500, width=1040)

#         # Handle marker clicks in dynamic mode
#         if st.session_state['dynamic_mode'] and st_data.get("last_object_clicked_popup") is not None:
#             st.session_state['selected_marker'] = st_data["last_object_clicked_popup"]

#         # Display data table with collapsible view
#         with st.expander(f'{file_name} - {selected_sheet} Table', expanded=True):
#             st.dataframe(df, width=950, height=300)

#         # Display warning message in the sidebar if it exists
#         if 'warning_message' in st.session_state and st.session_state['warning_message']:
#             st.sidebar.warning(st.session_state['warning_message'])