import streamlit as st
import cv2
import numpy as np
#from .detect_plates2 import run_plate_detection
from .plate_reader import plate_detector
from .web_utils.video_stream_utils import get_youtube_stream_url
from .web_utils.gate_data_utils import check_vehicle_status, load_gate_data, get_gates_names
import pandas as pd

vehicle_model = "apps/gate/models/vehicle_detector.pt"
license_plate_model = "apps/gate/models/license_plate_detector.pt"
cars_data_path="apps/gate/data/cars_data.xlsx"
GATE_DATA = 'apps/gate/gate_data.json'

# Load the cars_data Excel file once at the beginning
cars_df = pd.read_excel(cars_data_path)


def gate_page():
    # Load parking spot keys for the select box
    parking_spot_keys = get_gates_names(GATE_DATA)
    gate_name = st.selectbox('Select Gate Camera', parking_spot_keys)

    video_type, video_source, focus_area = load_gate_data(gate_name, GATE_DATA)


    if video_type == "youtube_stream":
        try:
            video_source = get_youtube_stream_url(video_source)
        except Exception as e:
            st.error(f"Error fetching YouTube stream: {e}")
            return

    # with st.expander("info"):
    #     st.write(selected_spot, video_type, video_source, parking_spots)
    
    col01, col02 = st.columns([1,1])
    with col01:
        stop_button = st.button('Stop Processing')
        if stop_button:
            st.stop()

    with col02:
        show_boxes = st.checkbox('Show Vehicle Bounding Boxes', value=False)

    col11, col12, col13 = st.columns([8, 1, 3])
    with col11:
        stframe = st.empty()

    with col13:
        st.write("plate image")
        plate_image = st.empty()  # Move plate_image creation before the loop
        st.write("plate text")
        plate_text = st.empty()
        st.write("Status")
        vehicle_status = st.empty()


    # Call the plate_detector function and display frames in real-time
    for processed_frame, clipped_license_plate,license_plate_text, fps in plate_detector(video_source, license_plate_model, vehicle_model=vehicle_model, imgsz=640, focus_area=focus_area):
        # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
        processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)


        # Check if clipped_license_plate is valid before trying to process it
        print(clipped_license_plate)
        if clipped_license_plate is not None: #and isinstance(clipped_license_plate, np.ndarray):
            clipped_license_plate = cv2.cvtColor(clipped_license_plate, cv2.COLOR_BGR2RGB)
            
            plate_image.image(clipped_license_plate, channels="RGB", use_column_width=True)
            
            plate_text.write(f'''#### {license_plate_text}''')

            status = check_vehicle_status(cars_df, license_plate_text)

            vehicle_status.write(f'''#### {status}''')


        # else:
        #     st.warning("No valid license plate detected.")

        # clipped_license_plate = cv2.cvtColor(clipped_license_plate, cv2.COLOR_BGR2RGB)

        # Display the frame in the Streamlit app
        stframe.image(processed_frame_rgb, channels="RGB")
        #plate_image.image(clipped_license_plate, channels="RGB")



    # # Run parking detection with live video feed or uploaded video
    # run_plate_detection(
    #     video_source=video_source,
    #     model_path=model_path,
    #     parking_spots=parking_spots,
    #     stframe=stframe,
    #     show_boxes=show_boxes,
    #     counter_display=counter_display
    # )
