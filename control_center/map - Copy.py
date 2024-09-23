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

# Load data from Excel
def load_data(file_path):
    return pd.read_excel(file_path, sheet_name=None)

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





# Function to create map
def create_map(df, coordinates):
    m = folium.Map(
        tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
        attr='OpenStreetMap HOT'
    )
    m.fit_bounds(coordinates)

    asterisk_columns = [col for col in df.columns if col.endswith('*')]
    tooltip_col = asterisk_columns[0] if asterisk_columns else None
    asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

    for idx, row in df.iterrows():
        popup_content = "".join(
            f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
        )
        
        icon_color = 'blue' if row.get('Status*', '') == 'Closed' else 'red'

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
    return m

# Main function for the history page
def map_page():
    st.markdown("""
        <style>
        div[data-testid="stSidebarCollapseButton"] {
            padding: 2px;  
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        /* Reduce padding and margin for the sidebar header */
        div[data-testid="stSidebarHeader"] {
            padding: 10px; /* Adjust as needed */
            margin: 0;     /* Adjust as needed */
        }

        /* Reduce padding around the logo image */
        div[data-testid="stSidebarHeader"] img[data-testid="stLogo"] {
            width: 100px;  /* Adjust width as needed */
            height: auto;  /* Maintain aspect ratio */
            margin: 0;     /* Adjust margin if needed */
        }

        /* Reduce padding around the sidebar collapse button */
        div[data-testid="stSidebarCollapseButton"] {
            padding: 2px;  /* Adjust as needed */
            margin: 0;     /* Adjust as needed */
        }

        /* Adjust button padding */
        div[data-testid="stSidebarCollapseButton"] button {
            padding: 2px;  /* Adjust as needed */
        }
            
        /* Adjust button padding */
        div[data-testid="stAppViewBlockContainer"]
        {
            padding-top: 30px; /* Adjust as needed */
            margin: 0;     /* Adjust as needed */
        }
                
    
        </style>
        
        """, unsafe_allow_html=True)


    st.markdown(
        """
        <style>
        div[data-testid="stAppViewBlockContainer"] {
        padding-top: 5px;
        padding-bottom: 5px;
        padding-right: 60px;
        padding-left: 60px;
        margin: 0;}

        .element-container iframe {
        width: 100% !important;
        height: 600px;  /* Adjust the height as needed */
        }

        
        </style>
        """, unsafe_allow_html=True)

    # Load data from Excel
    data_url = 'data/data.xlsx'
    sheets_dict = load_data(data_url)
    sheet_names = list(sheets_dict.keys())





    # Initialize session state if not already
    if 'dynamic_mode' not in st.session_state:
        st.session_state['dynamic_mode'] = False
    if 'route_coords' not in st.session_state:
        st.session_state['route_coords'] = []
    if 'warning_message' not in st.session_state:
        st.session_state['warning_message']=""  # Flag to determine if the map needs updating

    # Initialize button states and message in session state
    mystate = st.session_state
    if "btn_prsd_status" not in mystate:
        mystate.btn_prsd_status = [False] * len(sheet_names)
    # if "message" not in mystate:
    #     mystate.message = "Select a sheet to see the message here."
    if "selected_sheet_index" not in mystate:
        mystate.selected_sheet_index = 0

    unpressed_font_color = "#FFFFFF"  # White font for unpressed buttons
    pressed_font_color = "#ff4b4b"  # Red font for pressed buttons
    unpressed_border_color = "#26282E"  # Dark border for unpressed buttons
    pressed_border_color = "#ff4b4b"  # Red border for pressed buttons
    hover_font_color = "#ff4b4b"  # Red font color on hover

    def ChangeButtonColour(widget_label, prsd_status):
        # Change button font color dynamically using JavaScript
        font_color = pressed_font_color if prsd_status else unpressed_font_color
        border_color = pressed_border_color if prsd_status else unpressed_border_color

        htmlstr = f"""
            <script>
                var elements = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < elements.length; ++i) {{
                    if (elements[i].innerText == '{widget_label}') {{
                        elements[i].style.background = 'none';  // No background color
                        elements[i].style.border = 'none';  // No border
                        elements[i].style.color = '{font_color}';  // Change font color
                        elements[i].style.fontWeight = 'bold';  // Optionally, make text bold
                        elements[i].style.cursor = 'pointer';  // Pointer on hover
                        elements[i].style.borderBottom = '2px solid {border_color}';
                        elements[i].style.width = '100%';  // Full width
                        elements[i].style.padding = '0';  // Remove padding
                        elements[i].style.borderRadius = '0';  // No rounded corners

                        // Add hover effect
                        elements[i].onmouseover = function() {{
                            this.style.color = '{hover_font_color}';  // Red font color on hover
                        }};
                        elements[i].onmouseout = function() {{
                            this.style.color = '{font_color}';  // Restore original font color when not hovering
                        }};
                    }}
                }}
            </script>
        """
        components.html(htmlstr, height=0, width=0)

    def ChkBtnStatusAndAssignColour():
        # Check button statuses and assign the appropriate color
        for i in range(len(sheet_names)):
            ChangeButtonColour(sheet_names[i], mystate.btn_prsd_status[i])

    def btn_pressed_callback(i):
        # Update session state when a button is pressed
        mystate.btn_prsd_status = [False] * len(sheet_names)
        mystate.btn_prsd_status[i] = True
        mystate.selected_sheet_index = i
        # mystate.message = f'You clicked {sheet_names[i]}!'

    # Create columns for each button (sheet)
    columns = st.columns(len(sheet_names))

    for i, text in enumerate(sheet_names):
        # Create a button for each sheet name and retain its clicked state
        if columns[i].button(text, key=f"btn_{i}", on_click=btn_pressed_callback, args=(i,)):
            # The button press will trigger the callback and update the message
            pass

    # # Display the message
    # st.write(mystate.message)



    # Check if any sheet is selected
    if mystate.selected_sheet_index is not None:
        selected_sheet = sheet_names[mystate.selected_sheet_index]
        df = sheets_dict[selected_sheet]
        coordinates = df[['Latitude', 'Longitude']].values.tolist()

        if selected_sheet == "Emergency" :
                # Call the KPI calculation function
                kpis = calculate_emergency_kpis(df)

                # Display the KPIs
                st.write("## Key Performance Indicators (KPIs)")
                col11, col12, col13, col14, col15 = st.columns([1,2,1,1,1])
                col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
                col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
                col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
                col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
                col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

        elif selected_sheet == "Workforce" :
            # Call the KPI calculation function
            kpis = calculate_workforce_kpis(df)

            # Display the KPIs in Streamlit
            st.write("## Key Performance Indicators (KPIs)")
            col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
            col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
            col12.metric("Working Hours", kpis['Working Hours'])
            col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
            col14.metric("Complain Numbers", kpis['Complain Numbers'])
            col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")


            # col21, col22, col23 = st.columns([1,2,1])
            # # Display the pie chart in Streamlit
            # with col22:
            #     st.pyplot(kpis['fig'])

        # Display map
        m = create_map(df, coordinates)
        
        # Add route to the map if it exists
        if st.session_state['route_coords']:
            PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)
        
        # # Conditionally render the map based on mode
        # if st.session_state['dynamic_mode']:
        #     st_folium(m)
        # else:
        #     folium_static(m)
        
        folium_static(m)

        col31, col32, col33,col34, col35,col36 = st.columns([4,1,1,1,1,4])
        with col32:
            if st.button('🗺️',use_container_width=True):
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

                        # Force a rerun of the app to refresh the map with the new route
                        st.rerun()


        with col33:
            if st.button("🖱️",use_container_width=True):
                st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']


        with col34:
            if st.button("✨",use_container_width=True):
                pass

        with col35:
            if st.button("📊",use_container_width=True):
                pass

        if st.session_state['warning_message']:
            st.warning ("The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations.")



        # Display the DataFrame
        #st.dataframe(df, use_container_width=True)
     

    # Specify the column you want to filter on (e.g., 'Age')
    filter_column = 'Type*'  # Change this to the desired column name


        # Create Grid Options Builder
    # Create Grid Options Builder
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering only for the specified column and hide other column options
    for col in df.columns:
        if col == filter_column:
            gb.configure_column(col, filter=True,menuTabs=['filterMenuTab'])# suppressMenu=False)
        else:
            gb.configure_column(col, suppressMenu=True)  # Suppress menu for other columns

            

    # Build grid options and suppress the column selection panel
    gridOptions = gb.build()

    # Display AgGrid with custom column settings
    AgGrid(df, gridOptions=gridOptions, use_container_width=True)



    # Apply the correct button colors after rendering the buttons
    ChkBtnStatusAndAssignColour()


#####################################################################
# import streamlit as st
# import pandas as pd
# import streamlit.components.v1 as components

# # Load data from Excel
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)

# def history_page():
#     # Load data from Excel
#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     # Initialize button states in session state
#     mystate = st.session_state
#     if "btn_prsd_status" not in mystate:
#         mystate.btn_prsd_status = [False] * len(sheet_names)

#     unpressed_font_color = "#FFFFFF"  # White font for unpressed buttons
#     pressed_font_color = "#ff4b4b"  # Red font for pressed buttons
#     unpressed_border_color = "#26282E"#"#FFFFFF"  # White border for unpressed buttons
#     pressed_border_color = "#ff4b4b"  # Red border for pressed buttons
#     hover_font_color = "#ff4b4b"  # Green font color on hover

#     def ChangeButtonColour(widget_label, prsd_status):
#         # Change button font color dynamically using JavaScript
#         font_color = pressed_font_color if prsd_status else unpressed_font_color
#         border_color = pressed_border_color if prsd_status else unpressed_border_color

#         htmlstr = f"""
#             <script>
#                 var elements = window.parent.document.querySelectorAll('button');
#                 for (var i = 0; i < elements.length; ++i) {{
#                     if (elements[i].innerText == '{widget_label}') {{
#                         elements[i].style.background = 'none';  // No background color
#                         elements[i].style.border = 'none';  // No border
#                         elements[i].style.color = '{font_color}';  // Change font color
#                         elements[i].style.fontWeight = 'bold';  // Optionally, make text bold
#                         elements[i].style.cursor = 'pointer';  // Pointer on hover
#                         elements[i].style.borderBottom = '2px solid {border_color}';
#                         elements[i].style.width = '100%';  // Full width
#                         elements[i].style.padding = '0';  // Remove padding
#                         elements[i].style.borderRadius = '0';  // No rounded corners
#                         elements[i].style.gap = 'none';  // No rounded corners

#                         // Add hover effect
#                         elements[i].onmouseover = function() {{
#                             this.style.color = '{hover_font_color}';  // Green font color on hover
#                         }};
#                         elements[i].onmouseout = function() {{
#                             this.style.color = '{font_color}';  // Restore original font color when not hovering
#                         }};
#                     }}
#                 }}
#             </script>
#         """
#         components.html(htmlstr, height=0, width=0)

#     def ChkBtnStatusAndAssignColour():
#         # Check button statuses and assign the appropriate color
#         for i in range(len(sheet_names)):
#             ChangeButtonColour(sheet_names[i], mystate.btn_prsd_status[i])

#     def btn_pressed_callback(i):
#         # Update session state when a button is pressed
#         mystate.btn_prsd_status = [False] * len(sheet_names)
#         mystate.btn_prsd_status[i] = True

#     # Create columns for each button (sheet)
#     columns = st.columns(len(sheet_names))

#     for i, text in enumerate(sheet_names):
#         # Create a button for each sheet name and retain its clicked state
#         if columns[i].button(text, key=f"btn_{i}", on_click=btn_pressed_callback, args=(i,)):
#             st.write(f'You clicked {text}!')

#     # Apply the correct button colors after rendering the buttons
#     ChkBtnStatusAndAssignColour()

# # Call the function to display the history page
# history_page()

# import streamlit as st
# import pandas as pd
# import folium
# from streamlit_folium import folium_static
# from datetime import datetime
# from matplotlib import pyplot as plt
# from utils.route_utils import construct_osrm_url, get_trip_data
# from folium import PolyLine

# # Utility function to parse time
# def parse_time(t):
#     try:
#         return pd.to_datetime(t, format='%H:%M:%S').time()
#     except ValueError:
#         return pd.to_datetime(t, format='%H:%M').time()

# # Load data from Excel
# def load_data(file_path):
#     return pd.read_excel(file_path, sheet_name=None)

# # Calculate KPIs for emergency situations
# def calculate_emergency_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Validate required columns
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
#     if any(col not in df_copy.columns for col in required_columns):
#         raise ValueError("Required column is missing from the DataFrame")

#     today = datetime.today().date()

#     # Ensure time columns are correctly formatted
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate KPIs
#     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100
#     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'satisfied').mean() * 100
#     emergency_numbers = df_copy[['Latitude', 'Longitude']].nunique()

#     emergency_closure_time_str = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

#     return {
#         "Closure Percentage": closure_percentage,
#         "Emergency Closure Time": emergency_closure_time_str,
#         "Satisfaction Rate": satisfaction_rate,
#         "Emergency Numbers": emergency_numbers,
#         "Expected Emergency Alarm": "To be calculated"
#     }

# # Calculate KPIs for workforce
# def calculate_workforce_kpis(df):
#     df_copy = df.copy()
#     df_copy.columns = df_copy.columns.str.rstrip('*')

#     # Validate required columns
#     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
#     if any(col not in df_copy.columns for col in required_columns):
#         raise ValueError("Required column is missing from the DataFrame")

#     today = datetime.today().date()

#     # Ensure time columns are correctly formatted
#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

#     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
#     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

#     # Calculate KPIs
#     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
#     operation_percentage = (df_copy['Status'] == 'Active').mean() * 100
#     evaluation_rate = df_copy['Evaluation'].mean() * 100
#     complain_numbers = df_copy['Complain Today'].sum()

#     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

#     # Generate pie chart for operations
#     fig, ax = plt.subplots(figsize=(1, 1))
#     status_counts = df_copy['Operation'].value_counts()
#     ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
#     ax.axis('equal')

#     return {
#         "Operation Percentage": operation_percentage,
#         "Working Hours": working_hours_str,
#         "Evaluation Rate": evaluation_rate,
#         "Complain Numbers": complain_numbers,
#         "Expected Complains Alarm": "To be calculated",
#         "fig": fig
#     }

# # Function to create map with markers
# def create_map(df, coordinates):
#     m = folium.Map(tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png', attr='OpenStreetMap HOT')
#     m.fit_bounds(coordinates)

#     for idx, row in df.iterrows():
#         popup_content = "".join(
#             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in df.columns if col.endswith('*')
#         )
#         icon_color = 'blue' if row.get('Status*', '') == 'Closed' else 'red'
#         marker = folium.Marker(
#             location=[row['Latitude'], row['Longitude']],
#             popup=f"<b>{row['Location']}</b><br>{popup_content}",
#             icon=folium.Icon(color=icon_color)
#         )
#         marker.add_to(m)
#     return m

# # Main function for the history page
# def map_page():
#     st.markdown(
#         """
#         <style>
#         div[data-testid="stAppViewBlockContainer"] { padding: 5px 60px; margin: 0;}
#         .element-container iframe { width: 100% !important; height: 600px; }
#         </style>
#         """, unsafe_allow_html=True)

#     data_url = 'data/data.xlsx'
#     sheets_dict = load_data(data_url)
#     sheet_names = list(sheets_dict.keys())

#     st.session_state.setdefault('dynamic_mode', False)
#     st.session_state.setdefault('route_coords', [])
#     st.session_state.setdefault('warning_message', "")
#     st.session_state.setdefault('btn_prsd_status', [False] * len(sheet_names))
#     st.session_state.setdefault('selected_sheet_index', 0)

#     # Button states and dynamic UI
#     columns = st.columns(len(sheet_names))
#     for i, text in enumerate(sheet_names):
#         if columns[i].button(text):
#             st.session_state.btn_prsd_status = [False] * len(sheet_names)
#             st.session_state.btn_prsd_status[i] = True
#             st.session_state.selected_sheet_index = i

#     selected_sheet = sheet_names[st.session_state.selected_sheet_index]
#     df = sheets_dict[selected_sheet]
#     coordinates = df[['Latitude', 'Longitude']].values.tolist()

#     # Display KPIs based on the selected sheet
#     if selected_sheet == "Emergency":
#         kpis = calculate_emergency_kpis(df)
#     elif selected_sheet == "Workforce":
#         kpis = calculate_workforce_kpis(df)


#     # col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
#     # for metric, value in kpis.items():
#     #     if isinstance(value, str):
#     #         col1.metric(metric, value)
#     #     elif isinstance(value, float):
#     #         col2.metric(metric, f"{value:.2f}%")
    
#     # Create and display map
#     m = create_map(df, coordinates)
#     folium_static(m)

#     # Display route if available
#     if st.session_state['route_coords']:
#         PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)

# # import streamlit as st
# # import pandas as pd
# # import streamlit.components.v1 as components
# # import folium
# # from streamlit_folium import st_folium, folium_static
# # from datetime import datetime
# # from matplotlib import pyplot as plt
# # from utils.route_utils import construct_osrm_url, get_trip_data
# # from folium import PolyLine

# # # Load data from Excel
# # def load_data(file_path):
# #     return pd.read_excel(file_path, sheet_name=None)

# # def calculate_emergency_kpis(df):
# #     # Strip trailing '*' from column names
# #     df_copy = df.copy()
# #     df_copy.columns = df_copy.columns.str.rstrip('*')

# #     # Check if required columns exist
# #     required_columns = ['Open Time', 'Closure Time', 'Status', 'Satisfaction']
# #     for col in required_columns:
# #         if col not in df_copy.columns:
# #             raise ValueError(f"Column '{col}' is missing from the DataFrame")

# #     today = datetime.today().date()

# #     # Function to parse time whether it includes seconds or not
# #     def parse_time(t):
# #         try:
# #             return pd.to_datetime(t, format='%H:%M:%S').time()
# #         except ValueError:
# #             try:
# #                 return pd.to_datetime(t, format='%H:%M').time()
# #             except ValueError:
# #                 raise ValueError(f"Time format for '{t}' is incorrect")

# #     # Ensure 'Open Time' and 'Closure Time' are in time format
# #     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
# #     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

# #     # Combine with today's date to create datetime objects
# #     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
# #     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

# #     # Calculate the mean emergency closure time
# #     # emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
# #     emergency_closure_time = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
# #     emergency_closure_time = f"{emergency_closure_time.days} days {emergency_closure_time.seconds // 3600} hrs {(emergency_closure_time.seconds % 3600) // 60} mins"

# #     # Calculate Closure Percentage
# #     closure_percentage = (df_copy['Status'] == 'Closed').mean() * 100

# #     # Calculate Satisfaction Rate
# #     satisfaction_rate = df_copy['Satisfaction'].str.lower().apply(lambda x: x == 'sattisfied').mean() * 100

# #     # Calculate Emergency Numbers as the number of unique incidents based on Latitude and Longitude
# #     df_copy['Location'] = df_copy[['Latitude', 'Longitude']].apply(lambda x: f"{x['Latitude']},{x['Longitude']}", axis=1)
# #     emergency_numbers = df_copy['Location'].nunique()

# #     # Placeholder for Expected Emergency Alarm
# #     expected_emergency_alarm = "To be calculated based on relationships"

# #     # Return a dictionary with all the calculated KPIs
# #     return {
# #         "Closure Percentage": closure_percentage,
# #         "Emergency Closure Time": emergency_closure_time,
# #         "Satisfaction Rate": satisfaction_rate,
# #         "Emergency Numbers": emergency_numbers,
# #         "Expected Emergency Alarm": expected_emergency_alarm
# #     }

# # def calculate_workforce_kpis(df):
# #     # Strip trailing '*' from column names
# #     df_copy = df.copy(deep=False)
# #     df_copy.columns = df_copy.columns.str.rstrip('*')

# #     # Check if required columns exist
# #     required_columns = ['Open Time', 'Closure Time', 'Status', 'Evaluation', 'Complain Today']
# #     for col in required_columns:
# #         if col not in df_copy.columns:
# #             raise ValueError(f"Column '{col}' is missing from the DataFrame")

# #     today = datetime.today().date()

# #     # Function to parse time whether it includes seconds or not
# #     def parse_time(t):
# #         try:
# #             return pd.to_datetime(t, format='%H:%M:%S').time()
# #         except ValueError:
# #             try:
# #                 return pd.to_datetime(t, format='%H:%M').time()
# #             except ValueError:
# #                 raise ValueError(f"Time format for '{t}' is incorrect")

# #     # Ensure 'Open Time' and 'Closure Time' are in time format
# #     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))
# #     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: parse_time(x.time() if isinstance(x, datetime) else x))

# #     # Combine with today's date to create datetime objects
# #     df_copy['Open Time'] = df_copy['Open Time'].apply(lambda x: datetime.combine(today, x))
# #     df_copy['Closure Time'] = df_copy['Closure Time'].apply(lambda x: datetime.combine(today, x))

# #     # Calculate the average working hours
# #     working_hours = (df_copy['Closure Time'] - df_copy['Open Time']).mean()
# #     working_hours_str = f"{working_hours.days} days {working_hours.seconds // 3600} hours {(working_hours.seconds % 3600) // 60} min"

# #     # Calculate Operation Percentage (Active/Total)
# #     total_operations = len(df_copy)
# #     active_operations = (df_copy['Status'] == 'Active').sum()
# #     operation_percentage = (active_operations / total_operations) * 100

# #     # Calculate Evaluation Rate
# #     total_evaluations = df_copy['Evaluation'].sum()
# #     total_responses = len(df_copy)
# #     evaluation_rate = total_evaluations / total_responses if total_responses > 0 else 0

# #     # Calculate Complain Numbers
# #     complain_numbers = df_copy['Complain Today'].sum()

# #     # Placeholder for Expected Complaints Alarm
# #     expected_complains_alarm = "To be calculated based on relationships"



# #     # Generate Pie Chart for Operations
# #     status_counts = df_copy['Operation'].value_counts()  # Group by status and count
# #     fig, ax = plt.subplots(figsize=(1, 1))

# #     # Set figure and axes backgrounds to transparent
# #     fig.patch.set_facecolor('none')
# #     ax.set_facecolor('none')

# #     ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90,textprops={'color': 'white', 'fontsize': 4})
# #     ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# #     plt.title('Operations Status Distribution')

# #     # # Display the pie chart in Streamlit
# #     # st.pyplot(fig)

# #     # Return a dictionary with all the calculated KPIs
# #     return {
# #         "Operation Percentage": operation_percentage,
# #         "Working Hours": working_hours_str,
# #         "Evaluation Rate": evaluation_rate,
# #         "Complain Numbers": complain_numbers,
# #         "Expected Complains Alarm": expected_complains_alarm,
# #         "fig": fig,
# #     }





# # # Function to create map
# # def create_map(df, coordinates):
# #     m = folium.Map(
# #         tiles='https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png',
# #         attr='OpenStreetMap HOT'
# #     )
# #     m.fit_bounds(coordinates)

# #     asterisk_columns = [col for col in df.columns if col.endswith('*')]
# #     tooltip_col = asterisk_columns[0] if asterisk_columns else None
# #     asterisk_columns = asterisk_columns[1:] if len(asterisk_columns) > 1 else []

# #     for idx, row in df.iterrows():
# #         popup_content = "".join(
# #             f"<b>{col[:-1]}:</b> {row[col]}<br>" for col in asterisk_columns
# #         )
        
# #         icon_color = 'blue' if row.get('Status*', '') == 'Closed' else 'red'

# #         marker_id = f"marker_{idx}"
# #         marker = folium.Marker(
# #             location=[row['Latitude'], row['Longitude']],
# #             popup=f"""
# #                 <div>
# #                     <b>{row[tooltip_col]}</b><br>
# #                     {popup_content}
# #                     <br><br>
# #                     <a href="?marker_id={marker_id}" style="text-decoration:none;"></a>
# #                 </div>
# #             """,
# #             tooltip=row[tooltip_col] if tooltip_col else '',
# #             icon=folium.Icon(color=icon_color, prefix='fa', icon='lightbulb')
# #         )
# #         marker.add_to(m)
# #     return m

# # # Main function for the history page
# # def map_page():

# #     st.markdown(
# #         """
# #         <style>
# #         div[data-testid="stAppViewBlockContainer"] {
# #         padding-top: 5px;
# #         padding-bottom: 5px;
# #         padding-right: 60px;
# #         padding-left: 60px;
# #         margin: 0;}

# #         .element-container iframe {
# #         width: 100% !important;
# #         height: 600px;  /* Adjust the height as needed */
# #         }

        
# #         </style>
# #         """, unsafe_allow_html=True)

# #     # Load data from Excel
# #     data_url = 'data/data.xlsx'
# #     sheets_dict = load_data(data_url)
# #     sheet_names = list(sheets_dict.keys())





# #     # Initialize session state if not already
# #     if 'dynamic_mode' not in st.session_state:
# #         st.session_state['dynamic_mode'] = False
# #     if 'route_coords' not in st.session_state:
# #         st.session_state['route_coords'] = []
# #     if 'warning_message' not in st.session_state:
# #         st.session_state['warning_message']=""  # Flag to determine if the map needs updating

# #     # Initialize button states and message in session state
# #     mystate = st.session_state
# #     if "btn_prsd_status" not in mystate:
# #         mystate.btn_prsd_status = [False] * len(sheet_names)
# #     # if "message" not in mystate:
# #     #     mystate.message = "Select a sheet to see the message here."
# #     if "selected_sheet_index" not in mystate:
# #         mystate.selected_sheet_index = 0

# #     unpressed_font_color = "#FFFFFF"  # White font for unpressed buttons
# #     pressed_font_color = "#ff4b4b"  # Red font for pressed buttons
# #     unpressed_border_color = "#26282E"  # Dark border for unpressed buttons
# #     pressed_border_color = "#ff4b4b"  # Red border for pressed buttons
# #     hover_font_color = "#ff4b4b"  # Red font color on hover

# #     def ChangeButtonColour(widget_label, prsd_status):
# #         # Change button font color dynamically using JavaScript
# #         font_color = pressed_font_color if prsd_status else unpressed_font_color
# #         border_color = pressed_border_color if prsd_status else unpressed_border_color

# #         htmlstr = f"""
# #             <script>
# #                 var elements = window.parent.document.querySelectorAll('button');
# #                 for (var i = 0; i < elements.length; ++i) {{
# #                     if (elements[i].innerText == '{widget_label}') {{
# #                         elements[i].style.background = 'none';  // No background color
# #                         elements[i].style.border = 'none';  // No border
# #                         elements[i].style.color = '{font_color}';  // Change font color
# #                         elements[i].style.fontWeight = 'bold';  // Optionally, make text bold
# #                         elements[i].style.cursor = 'pointer';  // Pointer on hover
# #                         elements[i].style.borderBottom = '2px solid {border_color}';
# #                         elements[i].style.width = '100%';  // Full width
# #                         elements[i].style.padding = '0';  // Remove padding
# #                         elements[i].style.borderRadius = '0';  // No rounded corners

# #                         // Add hover effect
# #                         elements[i].onmouseover = function() {{
# #                             this.style.color = '{hover_font_color}';  // Red font color on hover
# #                         }};
# #                         elements[i].onmouseout = function() {{
# #                             this.style.color = '{font_color}';  // Restore original font color when not hovering
# #                         }};
# #                     }}
# #                 }}
# #             </script>
# #         """
# #         components.html(htmlstr, height=0, width=0)

# #     def ChkBtnStatusAndAssignColour():
# #         # Check button statuses and assign the appropriate color
# #         for i in range(len(sheet_names)):
# #             ChangeButtonColour(sheet_names[i], mystate.btn_prsd_status[i])

# #     def btn_pressed_callback(i):
# #         # Update session state when a button is pressed
# #         mystate.btn_prsd_status = [False] * len(sheet_names)
# #         mystate.btn_prsd_status[i] = True
# #         mystate.selected_sheet_index = i
# #         # mystate.message = f'You clicked {sheet_names[i]}!'

# #     # Create columns for each button (sheet)
# #     columns = st.columns(len(sheet_names))

# #     for i, text in enumerate(sheet_names):
# #         # Create a button for each sheet name and retain its clicked state
# #         if columns[i].button(text, key=f"btn_{i}", on_click=btn_pressed_callback, args=(i,)):
# #             # The button press will trigger the callback and update the message
# #             pass

# #     # # Display the message
# #     # st.write(mystate.message)



# #     # Check if any sheet is selected
# #     if mystate.selected_sheet_index is not None:
# #         selected_sheet = sheet_names[mystate.selected_sheet_index]
# #         df = sheets_dict[selected_sheet]
# #         coordinates = df[['Latitude', 'Longitude']].values.tolist()

# #         if selected_sheet == "Emergency" :
# #                 # Call the KPI calculation function
# #                 kpis = calculate_emergency_kpis(df)

# #                 # Display the KPIs
# #                 st.write("## Key Performance Indicators (KPIs)")
# #                 col11, col12, col13, col14, col15 = st.columns([1,2,1,1,1])
# #                 col11.metric("Closure Percentage", f"{kpis['Closure Percentage']:.2f}%")
# #                 col12.metric("Emergency Closure Time", f"{kpis['Emergency Closure Time']}")
# #                 col13.metric("Satisfaction Rate", f"{kpis['Satisfaction Rate']:.2f}%")
# #                 col14.metric("Emergency Numbers", kpis['Emergency Numbers'])
# #                 col15.write(f"Expected Emergency Alarm: {kpis['Expected Emergency Alarm']}")

# #         elif selected_sheet == "Workforce" :
# #             # Call the KPI calculation function
# #             kpis = calculate_workforce_kpis(df)

# #             # Display the KPIs in Streamlit
# #             st.write("## Key Performance Indicators (KPIs)")
# #             col11, col12, col13, col14, col15 = st.columns([1, 2, 1, 1, 1])
# #             col11.metric("Operation Percentage", f"{kpis['Operation Percentage']:.2f}%")
# #             col12.metric("Working Hours", kpis['Working Hours'])
# #             col13.metric("Evaluation Rate", f"{kpis['Evaluation Rate']:.2f}")
# #             col14.metric("Complain Numbers", kpis['Complain Numbers'])
# #             col15.write(f"Expected Complains Alarm: {kpis['Expected Complains Alarm']}")


# #             # col21, col22, col23 = st.columns([1,2,1])
# #             # # Display the pie chart in Streamlit
# #             # with col22:
# #             #     st.pyplot(kpis['fig'])

# #         # Display map
# #         m = create_map(df, coordinates)
        
# #         # Add route to the map if it exists
# #         if st.session_state['route_coords']:
# #             PolyLine(st.session_state['route_coords'], color="blue", weight=2.5, opacity=1).add_to(m)
        
# #         # # Conditionally render the map based on mode
# #         # if st.session_state['dynamic_mode']:
# #         #     st_folium(m)
# #         # else:
# #         #     folium_static(m)
        
# #         folium_static(m)

# #         col31, col32, col33,col34, col35,col36 = st.columns([4,1,1,1,1,4])
# #         with col32:
# #             if st.button('🗺️',use_container_width=True):
# #                 if len(coordinates) >= 2:
# #                     # Check if number of waypoints exceeds OSRM limit
# #                     if len(coordinates) > 100:
# #                         st.session_state['warning_message'] = "The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations."
# #                     else:
# #                         osrm_url = construct_osrm_url(coordinates[0], coordinates[-1], coordinates[1:-1])
# #                         trip_data = get_trip_data(osrm_url)


# #                         route_coords = trip_data['trips'][0]['geometry']['coordinates']
# #                         route_coords = [(lat, lon) for lon, lat in route_coords]

# #                         st.session_state['route_coords'] = route_coords
# #                         st.session_state['warning_message'] = None  # Clear warning message

# #                         # Force a rerun of the app to refresh the map with the new route
# #                         st.rerun()


# #         with col33:
# #             if st.button("🖱️",use_container_width=True):
# #                 st.session_state['dynamic_mode'] = not st.session_state['dynamic_mode']


# #         with col34:
# #             if st.button("✨",use_container_width=True):
# #                 pass

# #         with col35:
# #             if st.button("📊",use_container_width=True):
# #                 pass

# #         if st.session_state['warning_message']:
# #             st.warning ("The number of waypoints exceeds the OSRM limit of 100. Please reduce the number of locations.")



# #         # Display the DataFrame
# #         st.dataframe(df, use_container_width=True)


# #     # Apply the correct button colors after rendering the buttons
# #     ChkBtnStatusAndAssignColour()

# # # Call the function to display the history page
# # map_page()