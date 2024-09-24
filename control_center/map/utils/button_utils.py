import streamlit as st
import streamlit.components.v1 as components


def ChangeButtonColour(widget_label, prsd_status):

    unpressed_font_color = "#FFFFFF"  # White font for unpressed buttons
    pressed_font_color = "#ff4b4b"  # Red font for pressed buttons
    unpressed_border_color = "#26282E"  # Dark border for unpressed buttons
    pressed_border_color = "#ff4b4b"  # Red border for pressed buttons
    hover_font_color = "#ff4b4b"  # Red font color on hover

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


def render_sheet_buttons(sheet_names, mystate):

    def btn_pressed_callback(i):
        # Update session state when a button is pressed
        mystate.btn_prsd_status = [False] * len(sheet_names)
        mystate.btn_prsd_status[i] = True
        mystate.selected_sheet_index = i

    # Create columns for each button (sheet)
    columns = st.columns(len(sheet_names))

    for i, text in enumerate(sheet_names):
        # Create a button for each sheet name and retain its clicked state
        if columns[i].button(
            text, key=f"btn_{i}", on_click=btn_pressed_callback, args=(i,)
        ):
            # The button press will trigger the callback and update the message
            pass


def ChkBtnStatusAndAssignColour(sheet_names, mystate):
    # Check button statuses and assign the appropriate color
    for i in range(len(sheet_names)):
        ChangeButtonColour(sheet_names[i], mystate.btn_prsd_status[i])
