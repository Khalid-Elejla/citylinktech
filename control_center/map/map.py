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

# Main function for the history page
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

    # Display map
    display_map(df, coordinates)

    # Handle button actions
    handle_buttons(coordinates)

    # Display warning if any
    display_warning()

    # Display the grid
    display_grid(df)

    # Apply custom button styles
    ChkBtnStatusAndAssignColour(sheet_names, st.session_state)