import streamlit as st
import streamlit.components.v1 as components

def render_sheet_buttons(sheet_names, mystate):
    if "btn_prsd_status" not in mystate:
        mystate.btn_prsd_status = [False] * len(sheet_names)
    if "selected_sheet_index" not in mystate:
        mystate.selected_sheet_index = 0

    def btn_pressed_callback(i):
        mystate.btn_prsd_status = [False] * len(sheet_names)
        mystate.btn_prsd_status[i] = True
        mystate.selected_sheet_index = i

    columns = st.columns(len(sheet_names))

    for i, text in enumerate(sheet_names):
        if columns[i].button(text, key=f"btn_{i}", on_click=btn_pressed_callback, args=(i,)):
            pass

    check_btn_colors(sheet_names, mystate)

def check_btn_colors(sheet_names, mystate):
    pressed_color = "#ff4b4b"
    unpressed_color = "#FFFFFF"

    for i, text in enumerate(sheet_names):
        button_style = f"background-color: {pressed_color if mystate.btn_prsd_status[i] else unpressed_color};"
        components.html(f'<button style="{button_style}">{text}</button>', height=30)
