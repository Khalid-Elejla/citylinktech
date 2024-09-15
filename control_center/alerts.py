import streamlit as st
import extra_streamlit_components as stx
import pandas as pd

# Load data from Excel
def load_data(file_path):
    return pd.read_excel(file_path, sheet_name=None)

def alerts_page():
    data_url = 'data/data.xlsx'
    sheets_dict = load_data(data_url)
    sheet_names = list(sheets_dict.keys())

    def button_style():
        if st.session_state.button_clicked:
            return "background-color: green; color: white;"
        else:
            return "background-color: blue; color: white;"
    st.markdown(
        """
        <style>
        .element-container:has(style){
        }
        #button-after {
            display: none;
        }
        .element-container:has(#button-after) {
            display: none;
        }
        .element-container:has(#button-after) + div button {
            background-color: None;
            border:None;
            background:None
            button_style
            }
        
        [data-testid="baseButton-secondary"] {
            width: 100%;
            border:None;
        } 
        </style>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(len(sheet_names))

    # Loop through the list of texts and create a button for each item in its respective column
    for i, text in enumerate(sheet_names):
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if columns[i].button(text):
            st.markdown(
                        """
                        <style>
                        [data-testid="baseButton-secondary"] {
                            width: 100%;
                            border:10px;
                            </style>
                        """
                        )
        

            
            st.write(f'You clicked {text}!')



    # st.markdown(
    #     """
    #     <style>
    #     .element-container:has(style){
    #     }
    #     #button-after {
    #         display: none;
    #     }
    #     .element-container:has(#button-after) {
    #         display: none;
    #     }
    #     .element-container:has(#button-after) + div button {
    #         background-color: None;
    #         border:None;
    #         background:None
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
    # # st.button("button1")

    # st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    # st.button("My Button")
    # st.button("button2")
# import streamlit as st
# import extra_streamlit_components as stx

# def alerts_page():
#     # Insert the CSS that will target the element following the span with the id="target-div"
#     st.markdown("""
#     <style>
#         .element-container:has(#target-div) + div.menu-item {
#             /* APPLY YOUR STYLING HERE */
#             background-color: #f0f0f0;
#             border: 1px solid #333;
#             padding: 10px;
#         }
#     </style>
#     """, unsafe_allow_html=True)

#     # Insert the marker (span with a unique ID) before the component
#     st.markdown('<span id="target-div"></span>', unsafe_allow_html=True)

#     # Insert the Streamlit components that correspond to the HTML structure you're trying to style
#     st.markdown('<div class="menu-item"><div style="font-weight: normal; font-style: bold; border: 10px;"></div></div>', unsafe_allow_html=True)



#     # Render the tab bar
#     with st.container():
#         chosen_id = stx.tab_bar(data=[
#             stx.TabBarItemData(id=1, title="ToDo", description=""),
#             stx.TabBarItemData(id=2, title="Done", description=""),
#             stx.TabBarItemData(id=3, title="Overdue", description=""),
#         ], default=1)


# import streamlit as st
# import extra_streamlit_components as stx

# def alerts_page():

#     st.markdown("""
# <style>.element-container:has(#button-after) + div button {
#                 border : None;
#                 color: #000;
#  /* APPLY YOUR STYLING HERE */
#  }</style>""", unsafe_allow_html=True)
    
#     st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
#     st.button('My Button')


    # chosen_id = stx.tab_bar(data=[
    #     stx.TabBarItemData(id=1, title="ToDo", description=""),
    #     stx.TabBarItemData(id=2, title="Done", description=""),
    #     stx.TabBarItemData(id=3, title="Overdue", description=""),
    # ], default=1)
#     st.info(f"{chosen_id=}")
