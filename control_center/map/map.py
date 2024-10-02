import streamlit as st
from .utils.tabs_utils import ChkBtnStatusAndAssignColour, render_sheet_tabs
from .utils.data_loader import load_data
from .utils.kpi_calculations import display_kpis
from .utils.map_utils import display_map
from .utils.layout_utils import inject_custom_css
from .utils.state_utils import initialize_session_state, display_warning
from .utils.buttons_utils import handle_buttons
from .utils.grid_utils import display_grid


# Constants
DATA_URL = "data/data.xlsx"

def map_page():
    # Load data
    sheets_dict = load_data(DATA_URL)
    sheet_names = list(sheets_dict.keys())

    # Initialize session state
    initialize_session_state(sheet_names)

    # Inject custom CSS
    inject_custom_css()

    # Render sheet tabs
    render_sheet_tabs(sheet_names, st.session_state)

    # Proceed only if a sheet is selected
    selected_sheet = sheet_names[st.session_state.selected_sheet_index]
    df = sheets_dict[selected_sheet]
    coordinates = df[["Latitude", "Longitude"]].values.tolist()

    # Display KPIs based on the selected sheet
    display_kpis(selected_sheet, df)

    # Display the map (this will be updated based on filtered coordinates)
    display_map(df, coordinates)

    # Handle button actions
    handle_buttons(coordinates)

    # Display warning if any
    display_warning()

    # Display the grid (this will update session state with filtered data)
    display_grid(df)

    # Apply custom button styles
    ChkBtnStatusAndAssignColour(sheet_names, st.session_state)
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
def map_page():
    # Load data
    sheets_dict = load_data(DATA_URL)
    sheet_names = list(sheets_dict.keys())

    # Initialize session state
    initialize_session_state(sheet_names)

    # Inject custom CSS
    inject_custom_css()

    # Render sheet tabs
    render_sheet_tabs(sheet_names, st.session_state)

    # Proceed only if a sheet is selected
    selected_sheet = sheet_names[st.session_state.selected_sheet_index]
    df = sheets_dict[selected_sheet]

    # Initialize filtered_df in session state if not present
    if 'filtered_df' not in st.session_state:
        st.session_state.filtered_df = df

    # Display KPIs based on the filtered data
    display_kpis(selected_sheet, st.session_state.filtered_df)

    # Display map with filtered data
    display_map(st.session_state.filtered_df)

    # Handle button actions
    handle_buttons(st.session_state.filtered_df[["Latitude", "Longitude"]].values.tolist())

    # Display warning if any
    display_warning()

    # Display the grid (this will update st.session_state.filtered_df when filtered)
    display_grid(df)

    # Apply custom button styles
    ChkBtnStatusAndAssignColour(sheet_names, st.session_state)

    # Add a hidden button to trigger rerun when grid is filtered
    if st.session_state.get('grid_filtered', False):
        st.button('Update', key='update_button', on_click=lambda: None)
        st.session_state.grid_filtered = False
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
# # Main function for the history page
# def map_page():

#     # Load data
#     sheets_dict = load_data(DATA_URL)
#     sheet_names = list(sheets_dict.keys())

#     # Initialize session state
#     initialize_session_state(sheet_names)

#     # Inject custom CSS
#     inject_custom_css()

#     # Render sheet tabs
#     render_sheet_tabs(sheet_names, st.session_state)

#     # Proceed only if a sheet is selected
#     selected_sheet = sheet_names[st.session_state.selected_sheet_index]
#     df = sheets_dict[selected_sheet]
#     coordinates = df[["Latitude", "Longitude"]].values.tolist()

#     # Display KPIs based on the selected sheet
#     display_kpis(selected_sheet, df)

#     # Display map
#     display_map(df, coordinates)

#     # Handle button actions
#     handle_buttons(coordinates)

#     # Display warning if any
#     display_warning()

#     # Display the grid
#     display_grid(df)

#     # Apply custom button styles
#     ChkBtnStatusAndAssignColour(sheet_names, st.session_state)
