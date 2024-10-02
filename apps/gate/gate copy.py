import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time

# Importing utility functions from save_utils
from .plate_reader import plate_detector
from .web_utils.video_stream_utils import get_youtube_stream_url
from .web_utils.gate_data_utils import (
    check_vehicle_status,
    load_gate_data,
    get_gates_names,
)
from .web_utils.save_utils import (
    initialize_save_file,
    append_to_save_file,
    create_data_record,
    update_cars_data,
)

vehicle_model = "apps/gate/models/vehicle_detector.pt"
license_plate_model = "apps/gate/models/license_plate_detector.pt"
cars_data_path = "apps/gate/data/cars_data.xlsx"
GATE_DATA = "apps/gate/gate_data.json"
# Duration to keep displaying the last detected plate (in seconds)
KEEP_PLATE_TIME =15  # Adjust the number of seconds as needed

# Load the cars_data Excel file once at the beginning
cars_df = pd.read_excel(cars_data_path)




def gate_page():
#==================================State management ================================#
    if 'current_frame_id' not in st.session_state:
        st.session_state['current_frame_id'] = 15
    if 'license_plate_text' not in st.session_state:
        st.session_state['license_plate_text'] = None
           # Initialize session state variables
    if 'last_detected_plate_image' not in st.session_state:
        st.session_state['last_detected_plate_image'] = None
    if 'last_detected_plate_text' not in st.session_state:
        st.session_state['last_detected_plate_text'] = None
    if 'last_detected_plate_time' not in st.session_state:
        st.session_state['last_detected_plate_time'] = 0


    if "button_pressed" not in st.session_state:
        st.session_state.button_pressed = False
    cola, colb, colf, colc, cold = st.columns(
        [2.2, 1, 1.5, 1, 1], vertical_alignment="bottom"
    )

    # Load parking spot keys for the select box
    parking_spot_keys = get_gates_names(GATE_DATA)

    with cola:
        gate_name = st.selectbox("Select Gate Camera", parking_spot_keys)
    with colb:
        stop_button = st.button("Stop Processing")
    with colc:
        # Toggle to save stream results
        save_stream = st.toggle("Save Results")
    with cold:
        # Toggle for showing bounding boxes
        show_boxes = st.toggle("Show BBoxes")

    if stop_button:
        st.stop()

    video_type, video_source, focus_area = load_gate_data(gate_name, GATE_DATA)

    if video_type == "youtube_stream":
        try:
            video_source = get_youtube_stream_url(video_source)
        except Exception as e:
            st.error(f"Error fetching YouTube stream: {e}")
            return

    # Layout for video frame and additional info (plate image, text, and status)
    col11, col13 = st.columns([8, 3], gap="small")
    with col11:
        stframe = st.empty()  # Placeholder for video frames
    with col13:
        # Use container for grouping plate image, text, and status
        with st.container():
            st.write("Plate Image")
            # Placeholder for license plate image with fixed height
            plate_image = st.empty()
            default_image = np.zeros(
                (120, 240, 3), dtype=np.uint8
            )  # Black placeholder image with a fixed size
            st.write("Plate Text")
            col31, col32 = st.columns([4, 1])
            with col31:
                plate_text = st.empty()
            with col32:
                st.button(":material/info:")

            st.write("Status")
            vehicle_status = st.empty()
            col41, col42 = st.columns([1, 1])
            with col41:
                add_to_whitelist = st.button(
                    "Add to Whitelist",
                    on_click=update_cars_data,
                    args= (st.session_state['last_detected_plate_text'], "whitelist",cars_data_path))
            with col42:
                add_to_blacklist = st.button(
                    "Add to Blacklist",
                    on_click=update_cars_data,
                    args= (st.session_state['last_detected_plate_text'], "blacklist",cars_data_path))

    # Define the path for saving results
    save_file_path = "apps/gate/saved_resultsa3.json"  # JSON Lines format

    # # Initialize the JSON file if saving is enabled
    # if save_stream:
    #     initialize_save_file(save_file_path)

    # Call the plate_detector function and display frames in real-time
    for (
        processed_frame,
        clipped_license_plate,
        license_plate_text,
        fps,
        track_id,
        confidence,
        st.session_state['current_frame_id'],
        #current_frame_id,
    ) in plate_detector(
        video_source,
        license_plate_model,
        vehicle_model=vehicle_model,
        imgsz=640,
        focus_area=focus_area,
        start_frame_id=st.session_state['current_frame_id'],
    ):
        # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
        processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)


#===========================sticky plates=======================
        # Update session state if a new plate is detected
        if clipped_license_plate is not None:
            # New license plate detected
            st.session_state['last_detected_plate_image'] = clipped_license_plate
            st.session_state['last_detected_plate_text'] = license_plate_text
            st.session_state['last_detected_plate_time'] = time.time()
        else:
            # No new license plate detected
            time_since_last_plate = time.time() - st.session_state['last_detected_plate_time']
            if time_since_last_plate <= KEEP_PLATE_TIME:
                # Use the last detected plate
                clipped_license_plate = st.session_state['last_detected_plate_image']
                license_plate_text = st.session_state['last_detected_plate_text']
            else:
                # Clear the last detected plate
                st.session_state['last_detected_plate_image'] = None
                st.session_state['last_detected_plate_text'] = None
                clipped_license_plate = None
                license_plate_text = None
#=========================================================================


        # Check if clipped_license_plate is valid before trying to process it
        if clipped_license_plate is not None:
            # Convert the license plate to RGB format
            clipped_license_plate_rgb = cv2.cvtColor(
                clipped_license_plate, cv2.COLOR_BGR2RGB
            )

            # Ensure a fixed height for the license plate image while maintaining the aspect ratio
            target_height = 120  # Set a fixed height
            h, w, _ = clipped_license_plate_rgb.shape
            aspect_ratio = w / h
            new_width = int(target_height * aspect_ratio)

            # Resize the image to the new dimensions
            resized_plate = cv2.resize(
                clipped_license_plate_rgb, (new_width, target_height)
            )

            # Display the license plate image
            plate_image.image(resized_plate, channels="RGB", use_column_width=False)
        else:
            # Display a default placeholder image when no license plate is available
            plate_image.image(default_image, channels="RGB", use_column_width=False)

        # Display license plate text
        if license_plate_text:
            plate_text.write(f"#### {license_plate_text}")
        else:
            plate_text.write("#### No Plate Detected")

        # Check vehicle status
        status = check_vehicle_status(cars_df, st.session_state['last_detected_plate_text'])
        # status = check_vehicle_status(cars_df, license_plate_text)
        vehicle_status.write(f"#### {status if status else 'Unknown Vehicle'}")

        # Display the frame in the Streamlit app
        stframe.image(processed_frame_rgb, channels="RGB")

        # Save results if toggle is enabled
        if None not in (save_stream, track_id, license_plate_text):
            initialize_save_file(save_file_path)
            data_record = create_data_record(track_id, license_plate_text, confidence)
            append_to_save_file(save_file_path, gate_name, data_record)

# import streamlit as st
# import cv2
# import numpy as np
# import pandas as pd

# # Importing utility functions from save_utils
# from .plate_reader import plate_detector
# from .web_utils.video_stream_utils import get_youtube_stream_url
# from .web_utils.gate_data_utils import (
#     check_vehicle_status,
#     load_gate_data,
#     get_gates_names,
# )
# from .web_utils.save_utils import (
#     initialize_save_file,
#     append_to_save_file,
#     create_data_record,
#     update_cars_data,
# )


# def add_to_whitelist_callback():
#     if st.session_state.license_plate_text:
#         update_cars_data(
#             st.session_state.license_plate_text, "whitelist", cars_data_path
#         )


# vehicle_model = "apps/gate/models/vehicle_detector.pt"
# license_plate_model = "apps/gate/models/license_plate_detector.pt"
# cars_data_path = "apps/gate/data/cars_data.xlsx"
# GATE_DATA = "apps/gate/gate_data.json"

# # Load the cars_data Excel file once at the beginning
# cars_df = pd.read_excel(cars_data_path)

# if "button_pressed" not in st.session_state:
#     st.session_state.button_pressed = False


# def gate_page():
#     cola, colb, colf, colc, cold = st.columns(
#         [2.2, 1, 1.5, 1, 1], vertical_alignment="bottom"
#     )

#     # Load parking spot keys for the select box
#     parking_spot_keys = get_gates_names(GATE_DATA)

#     with cola:
#         gate_name = st.selectbox("Select Gate Camera", parking_spot_keys)
#     with colb:
#         stop_button = st.button("Stop Processing")
#     with colc:
#         # Toggle to save stream results
#         save_stream = st.toggle("Save Results")
#     with cold:
#         # Toggle for showing bounding boxes
#         show_boxes = st.toggle("Show BBoxes")

#     if stop_button:
#         st.stop()

#     @st.fragment
#     def heavy_computation():
#         if st.button("ccc"):
#             st.session_state.button_pressed=True
#             print("AXXXXXXXXXXXXXXXXXXXXXXX")

#     heavy_computation()

#     video_type, video_source, focus_area = load_gate_data(gate_name, GATE_DATA)

#     if video_type == "youtube_stream":
#         try:
#             video_source = get_youtube_stream_url(video_source)
#         except Exception as e:
#             st.error(f"Error fetching YouTube stream: {e}")
#             return

#     # Layout for video frame and additional info (plate image, text, and status)
#     col11, col13 = st.columns([8, 3], gap="small")
#     with col11:
#         stframe = st.empty()  # Placeholder for video frames
#     with col13:
#         # Use container for grouping plate image, text, and status
#         with st.container():
#             st.write("Plate Image")
#             # Placeholder for license plate image with fixed height
#             plate_image = st.empty()
#             default_image = np.zeros(
#                 (120, 240, 3), dtype=np.uint8
#             )  # Black placeholder image with a fixed size
#             st.write("Plate Text")
#             col31, col32 = st.columns([4, 1])
#             with col31:
#                 plate_text = st.empty()
#             with col32:
#                 st.button(":material/info:")

#             st.write("Status")
#             vehicle_status = st.empty()
#             col41, col42 = st.columns([1, 1])
#             with col41:
#                 add_to_whitelist = st.button(
#                     "Add to Whitelist"
#                 )  # , on_click=update_cars_data(st.session_state.license_plate_text, "whitelist",cars_data_path))
#             with col42:
#                 add_to_blacklist = st.button("Add to Blacklist")

#     # Define the path for saving results
#     save_file_path = "saved_resultsa2.json"  # JSON Lines format

#     # Initialize the JSON file if saving is enabled
#     if save_stream:
#         initialize_save_file(save_file_path)

#     # Call the plate_detector function and display frames in real-time
#     for (
#         processed_frame,
#         clipped_license_plate,
#         license_plate_text,
#         fps,
#         track_id,
#         confidence,
#     ) in plate_detector(
#         video_source,
#         license_plate_model,
#         vehicle_model=vehicle_model,
#         imgsz=640,
#         focus_area=focus_area,
#     ):
#         # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
#         processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

#         # Check if clipped_license_plate is valid before trying to process it
#         if clipped_license_plate is not None:
#             # Convert the license plate to RGB format
#             clipped_license_plate = cv2.cvtColor(
#                 clipped_license_plate, cv2.COLOR_BGR2RGB
#             )

#             # Ensure a fixed height for the license plate image while maintaining the aspect ratio
#             target_height = 120  # Set a fixed height
#             h, w, _ = clipped_license_plate.shape
#             aspect_ratio = w / h
#             new_width = int(target_height * aspect_ratio)

#             # Resize the image to the new dimensions
#             resized_plate = cv2.resize(
#                 clipped_license_plate, (new_width, target_height)
#             )

#             # Display the license plate image
#             plate_image.image(resized_plate, channels="RGB", use_column_width=False)
#         else:
#             # Display a default placeholder image when no license plate is available
#             plate_image.image(default_image, channels="RGB", use_column_width=False)

#         # Display license plate text
#         if license_plate_text:
#             plate_text.write(f"#### {license_plate_text}")
#         else:
#             plate_text.write("#### No Plate Detected")

#         # Check vehicle status
#         status = check_vehicle_status(cars_df, license_plate_text)
#         vehicle_status.write(f"#### {status if status else 'Unknown Vehicle'}")

#         # Display the frame in the Streamlit app
#         stframe.image(processed_frame_rgb, channels="RGB")

#         # Save results if toggle is enabled
#         if None not in (save_stream, track_id, license_plate_text):
#             data_record = create_data_record(track_id, license_plate_text, confidence)
#             append_to_save_file(save_file_path, gate_name, data_record)

#         # Optionally, you can limit the loop or add a break condition
#         # For example, to process only a certain number of frames
#         # if some_condition:
#         #     break

#     # Handle the actions for car-related buttons
#     if add_to_whitelist or st.session_state.button_pressed:
#         # st.session_state.button_pressed=True
#         if license_plate_text:
#             update_cars_data(license_plate_text, "whitelist")
#         else:
#             st.warning("No plate detected to add to whitelist.")
#         st.rerun()

#     if add_to_blacklist:
#         if license_plate_text:
#             update_cars_data(license_plate_text, "blacklist")
#         else:
#             st.warning("No plate detected to add to blacklist.")

#     # Note: If you have a "Get Car History" button, you should define and handle it similarly


# ############################################################################################################
# # import streamlit as st
# # import cv2
# # import numpy as np
# # import pandas as pd

# # # from .detect_plates2 import run_plate_detection
# # from .plate_reader import plate_detector
# # from .web_utils.video_stream_utils import get_youtube_stream_url
# # from .web_utils.gate_data_utils import (
# #     check_vehicle_status,
# #     load_gate_data,
# #     get_gates_names,
# # )

# # from .web_utils.save_utils import (
# #   initialize_save_file,
# #   append_to_save_file,
# #   create_data_record,
# # )
# # vehicle_model = "apps/gate/models/vehicle_detector.pt"
# # license_plate_model = "apps/gate/models/license_plate_detector.pt"
# # cars_data_path = "apps/gate/data/cars_data.xlsx"
# # GATE_DATA = "apps/gate/gate_data.json"

# # # Load the cars_data Excel file once at the beginning
# # cars_df = pd.read_excel(cars_data_path)


# # def gate_page():
# #     cola, colb, colf, colc, cold = st.columns([2.2,1,1.5,1, 1], vertical_alignment="bottom")
# #     # Load parking spot keys for the select box
# #     gate_keys = get_gates_names(GATE_DATA)
# #     with cola:
# #         gate_name = st.selectbox("Select Gate Camera", gate_keys)
# #     with colb:
# #         stop_button = st.button("Stop Processings")

# #     with colc:
# #         # Toggle to save stream results
# #         save_stream = st.toggle("Save Results")

# #     with cold:
# #         # Toggle for showing bounding boxes
# #         show_boxes = st.toggle("Show BBoxes")

# #     if stop_button:
# #         st.stop()

# #     video_type, video_source, focus_area = load_gate_data(gate_name, GATE_DATA)

# #     if video_type == "youtube_stream":
# #         try:
# #             video_source = get_youtube_stream_url(video_source)
# #         except Exception as e:
# #             st.error(f"Error fetching YouTube stream: {e}")
# #             return

# #     # # Create a layout for all buttons and controls
# #     # with st.container():
# #     #     # Row for "Stop Processing" button and toggle options
# #     #     col1, col2 = st.columns([1, 1])

# #     #     with col1:
# #     #         # Toggle to save stream results
# #     #         save_stream = st.toggle("Save Results")

# #     #     with col2:
# #     #         # Toggle for showing bounding boxes
# #     #         show_boxes = st.toggle("Show Bounding Boxes")

# #     # Layout for video frame and additional info (plate image, text, and status)
# #     col11, col13 = st.columns([8, 3],gap="small")
# #     with col11:
# #         stframe = st.empty()  # Placeholder for video frames

# #     with col13:
# #         # Use container for grouping plate image, text, and status
# #         with st.container():
# #             st.write("Plate Image")
# #             # Placeholder for license plate image with fixed height
# #             plate_image = st.empty()
# #             default_image = np.zeros(
# #                 (120, 240, 3), dtype=np.uint8
# #             )  # Black placeholder image with a fixed size
# #             st.write("Plate Text")
# #             col31,col32=st.columns([4,1])
# #             with col31:
# #                 plate_text = st.empty()
# #             with col32:
# #                 st.button(":material/info:")


# #             st.write("Status")
# #             vehicle_status = st.empty()
# #             col41,col42= st.columns([1,1])
# #             with col41:
# #                 st.button("add to whitelist")
# #             with col42:
# #                 st.button("add to blacklist")

# #     # Call the plate_detector function and display frames in real-time
# #     for (
# #         processed_frame,
# #         clipped_license_plate,
# #         license_plate_text,
# #         fps,
# #         track_id,
# #         confidence,
# #     ) in plate_detector(
# #         video_source,
# #         license_plate_model,
# #         vehicle_model=vehicle_model,
# #         imgsz=640,
# #         focus_area=focus_area,
# #     ):
# #         # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
# #         processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

# #         # Check if clipped_license_plate is valid before trying to process it
# #         if clipped_license_plate is not None:
# #             # Convert the license plate to RGB format
# #             clipped_license_plate = cv2.cvtColor(
# #                 clipped_license_plate, cv2.COLOR_BGR2RGB
# #             )

# #             # Ensure a fixed height for the license plate image while maintaining the aspect ratio
# #             target_height = 120  # Set a fixed height
# #             h, w, _ = clipped_license_plate.shape
# #             aspect_ratio = w / h
# #             new_width = int(target_height * aspect_ratio)

# #             # Resize the image to the new dimensions
# #             resized_plate = cv2.resize(
# #                 clipped_license_plate, (new_width, target_height)
# #             )

# #             # Display the license plate image
# #             plate_image.image(resized_plate, channels="RGB", use_column_width=False)
# #         else:
# #             # Display a default placeholder image when no license plate is available
# #             plate_image.image(default_image, channels="RGB", use_column_width=False)

# #         # Display license plate text
# #         if license_plate_text:
# #             plate_text.write(f"#### {license_plate_text}")
# #         else:
# #             plate_text.write("#### No Plate Detected")

# #         # Check vehicle status
# #         status = check_vehicle_status(cars_df, license_plate_text)
# #         vehicle_status.write(f"#### {status if status else 'Unknown Vehicle'}")

# #         # Display the frame in the Streamlit app
# #         stframe.image(processed_frame_rgb, channels="RGB")

# #     # Handle the actions for car-related buttons
# #     if get_car_history:
# #         # Logic for getting car history based on the detected license plate
# #         st.info(f"Fetching history for {license_plate_text}")
# #         # Add the actual logic here

# #     if add_to_blacklist:
# #         # Logic for adding the car to the blacklist
# #         st.warning(f"Adding {license_plate_text} to blacklist")
# #         # Add the actual logic here

# #     if add_to_whitelist:
# #         # Logic for adding the car to the whitelist
# #         st.success(f"Adding {license_plate_text} to whitelist")
# #         # Add the actual logic here
# ###################################################################################################################3

# # import streamlit as st
# # import cv2
# # import numpy as np
# # #from .detect_plates2 import run_plate_detection
# # from .plate_reader import plate_detector
# # from .web_utils.video_stream_utils import get_youtube_stream_url
# # from .web_utils.gate_data_utils import check_vehicle_status, load_gate_data, get_gates_names
# # import pandas as pd

# # vehicle_model = "apps/gate/models/vehicle_detector.pt"
# # license_plate_model = "apps/gate/models/license_plate_detector.pt"
# # cars_data_path="apps/gate/data/cars_data.xlsx"
# # GATE_DATA = 'apps/gate/gate_data.json'

# # # Load the cars_data Excel file once at the beginning
# # cars_df = pd.read_excel(cars_data_path)


# # def gate_page():
# #     # Load parking spot keys for the select box
# #     gate_keys = get_gates_names(GATE_DATA)
# #     gate_name = st.selectbox('Select Gate Camera', gate_keys)

# #     video_type, video_source, focus_area = load_gate_data(gate_name, GATE_DATA)


# #     if video_type == "youtube_stream":
# #         try:
# #             video_source = get_youtube_stream_url(video_source)
# #         except Exception as e:
# #             st.error(f"Error fetching YouTube stream: {e}")
# #             return

# #     # with st.expander("info"):
# #     #     st.write(selected_spot, video_type, video_source, parking_spots)

# #     col01, col02 = st.columns([1,1])
# #     with col01:
# #         stop_button = st.button('Stop Processing')
# #         if stop_button:
# #             st.stop()

# #     with col02:
# #         show_boxes = st.checkbox('Show Vehicle Bounding Boxes', value=False)

# #     col11, col12, col13 = st.columns([8, 1, 3])
# #     with col11:
# #         stframe = st.empty()

# #     with col13:
# #         st.write("plate image")
# #         plate_image = st.empty()  # Move plate_image creation before the loop
# #         st.write("plate text")
# #         plate_text = st.empty()
# #         st.write("Status")
# #         vehicle_status = st.empty()


# #     # Call the plate_detector function and display frames in real-time
# #     for processed_frame, clipped_license_plate,license_plate_text, fps, track_id, confidence  in plate_detector(video_source, license_plate_model, vehicle_model=vehicle_model, imgsz=640, focus_area=focus_area):
# #         # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
# #         processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)


# #         # Check if clipped_license_plate is valid before trying to process it
# #         if clipped_license_plate is not None: #and isinstance(clipped_license_plate, np.ndarray):
# #             clipped_license_plate = cv2.cvtColor(clipped_license_plate, cv2.COLOR_BGR2RGB)

# #             plate_image.image(clipped_license_plate, channels="RGB", use_column_width=True)

# #             plate_text.write(f'''#### {license_plate_text}''')

# #             st.write(license_plate_text, track_id, confidence )

# #             status = check_vehicle_status(cars_df, license_plate_text)

# #             vehicle_status.write(f'''#### {status}''')


# #         # Display the frame in the Streamlit app
# #         stframe.image(processed_frame_rgb, channels="RGB")
