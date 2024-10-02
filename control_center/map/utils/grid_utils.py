import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import pandas as pd

def display_grid(df) -> None:
    FILTER_COLUMN = "Type*"  # Column to apply filters to

    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering for the specific column
    for col in df.columns:
        gb.configure_column(
            col, filter=(col == FILTER_COLUMN), suppressMenu=(col != FILTER_COLUMN)
        )

    gridOptions = gb.build()

    # Capture the grid response (including filtered data)
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED,  # Return filtered data only
        update_mode=GridUpdateMode.MODEL_CHANGED,  # Trigger on any model change
        use_container_width=True
    )

    # Extract the filtered rows from grid response
    filtered_df = pd.DataFrame(grid_response["data"])

    # Update session state only if filtered data changes
    if not filtered_df.empty:
        st.session_state["filtered_coordinates"] = filtered_df[["Latitude", "Longitude"]].values.tolist()
    else:
        # Reset to full data coordinates if no filter is applied
        st.session_state["filtered_coordinates"] = df[["Latitude", "Longitude"]].values.tolist()

    # Trigger a rerender by updating the query params (this avoids deprecated st.experimental_rerun)
    st.query_params

#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
def display_grid(df):
    FILTER_COLUMN = "Type*"  # Column to apply filters to

    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering for the specific column
    for col in df.columns:
        gb.configure_column(
            col, filter=(col == FILTER_COLUMN), suppressMenu=(col != FILTER_COLUMN)
        )

    # Add our custom JavaScript callback
    gb.configure_grid_options(onFilterChanged=js_filter_changed)

    gridOptions = gb.build()

    # Display the AgGrid table with custom options
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        use_container_width=True,
        update_mode='MODEL_CHANGED',
        allow_unsafe_jscode=True  # Needed for our custom callback
    )

    # Update filtered_df in session state
    if grid_response['data'] is not None:
        st.session_state.filtered_df = pd.DataFrame(grid_response['data'])
        st.session_state.grid_filtered = True

# Custom JavaScript callback
js_filter_changed = """
function(e) {
    const filteredData = e.api.getModel().getRow(0);
    if (filteredData) {
        const rows = e.api.getModel().rowsToDisplay.map(row => row.data);
        streamlit.setComponentValue(rows);
    }
}
"""
#CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
# # Helper function to configure and display the AgGrid
# def display_grid(df) -> None:
#     FILTER_COLUMN = "Type*"  # Column to apply filters to

#     gb = GridOptionsBuilder.from_dataframe(df)

#     # Enable filtering for the specific column
#     for col in df.columns:
#         gb.configure_column(
#             col, filter=(col == FILTER_COLUMN), suppressMenu=(col != FILTER_COLUMN)
#         )

#     gridOptions = gb.build()

#     # Display the AgGrid table with custom options
#     AgGrid(df, gridOptions=gridOptions, use_container_width=True)
