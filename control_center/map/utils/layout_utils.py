import streamlit as st

# Inject CSS for button styling and other customizations
def inject_custom_css():
    st.markdown(
                """
                <style>
                /* General adjustments for padding and margin */
                div[data-testid="stSidebarHeader"],
                div[data-testid="stSidebarCollapseButton"] {
                    padding: 10px 2px; /* Sidebar header and collapse button padding */
                    margin: 0;         /* Reset margin */
                }

                /* Logo image adjustments */
                div[data-testid="stSidebarHeader"] img[data-testid="stLogo"] {
                    width: 100px;  /* Adjust width */
                    height: auto;  /* Maintain aspect ratio */
                    margin: 0;     /* Reset margin */
                }

                /* Collapse button adjustments */
                div[data-testid="stSidebarCollapseButton"] button {
                    padding: 2px;  /* Button padding */
                }

                /* App view container padding */
                div[data-testid="stAppViewBlockContainer"] {
                    padding: 30px 60px 5px 60px; /* Top, right, bottom, left */
                    margin: 0; /* Reset margin */
                }

                /* Adjust iframe within element container */
                .element-container iframe {
                    width: 100% !important;
                    height: 600px; /* Adjust height */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )