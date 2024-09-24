import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


# Helper function to configure and display the AgGrid
def display_grid(df) -> None:
    FILTER_COLUMN = "Type*"  # Column to apply filters to

    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering for the specific column
    for col in df.columns:
        gb.configure_column(
            col, filter=(col == FILTER_COLUMN), suppressMenu=(col != FILTER_COLUMN)
        )

    gridOptions = gb.build()

    # Display the AgGrid table with custom options
    AgGrid(df, gridOptions=gridOptions, use_container_width=True)
