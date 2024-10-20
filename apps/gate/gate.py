import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time
import random

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
  search_car_history,
)

vehicle_model = "apps/gate/models/vehicle_detector.pt"
license_plate_model = "apps/gate/models/license_plate_detector.pt"
cars_data_path = "apps/gate/data/cars_data.xlsx"
GATE_DATA = "apps/gate/data/gate_data.json"
# Duration to keep displaying the last detected plate (in seconds)
KEEP_PLATE_TIME = 15  # Adjust the number of seconds as needed

# Load the cars_data Excel file once at the beginning
cars_df = pd.read_excel(cars_data_path)


def gate_page():
  # ============================ State Management ================================ #
  if 'current_frame_id' not in st.session_state:
      st.session_state['current_frame_id'] = 70
  if 'license_plate_text' not in st.session_state:
      st.session_state['license_plate_text'] = None
  if 'last_detected_plate_image' not in st.session_state:
      st.session_state['last_detected_plate_image'] = None
  if 'last_detected_plate_text' not in st.session_state:
      st.session_state['last_detected_plate_text'] = None
  if 'last_detected_plate_time' not in st.session_state:
      st.session_state['last_detected_plate_time'] = 0

  # Layout for controls
  cola, colb, colc, cold, cole = st.columns(
      [2.2, 1, 1.5, 1, 1], vertical_alignment="bottom"
  )

  # Load parking spot keys for the select box
  parking_spot_keys = get_gates_names(GATE_DATA)

  with cola:
      gate_name = st.selectbox("Select Gate Camera", parking_spot_keys)
  with colb:
      stop_button = st.button("Stop Processing")
  with cold :
      # Toggle to save stream results
    #   save_stream = st.checkbox("Save Results")
      save_stream = st.toggle("Save Results")

  with cole:
      # Toggle for showing bounding boxes
      # show_boxes = st.checkbox("Show BBoxes")
      show_boxes = st.toggle("Show BBoxes")
  with cole:
      # Optional additional control
      pass

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
  col_video, col_info = st.columns([8, 3], gap="small")
  with col_video:
      stframe = st.empty()  # Placeholder for video frames
  with col_info:
      # Use container for grouping plate image, text, and status
      with st.container():
          st.write("Plate Image")
          # Placeholder for license plate image with fixed height
          plate_image = st.empty()
          default_image = np.zeros(
              (80, 240, 3), dtype=np.uint8
          )  # Black placeholder image with a fixed size
          st.write("Plate Text")
          col31, col32 = st.columns([4, 1])
          with col31:
                plate_text = st.empty()
          with col32:
                info_button=st.empty()
        #   plate_text = st.empty()
          st.write("Status")
          vehicle_status = st.empty()

          # Placeholders for buttons
          button_col1, button_col2 = st.columns([1, 1])
          with button_col1:
              add_whitelist = st.empty()
          with button_col2:
              add_blacklist = st.empty()

  # Define the path for saving results
  save_file_path = "apps/gate/saved_resultsa3.json"  # JSON Lines format

  # Initialize the JSON file if saving is enabled
  if save_stream:
      initialize_save_file(save_file_path)

  # Call the plate_detector function and display frames in real-time
  for (
      processed_frame,
      clipped_license_plate,
      license_plate_text,
      fps,
      track_id,
      confidence,
      st.session_state['current_frame_id'],
  ) in plate_detector(
      video_source,
      license_plate_model,
      #vehicle_model=vehicle_model,
      imgsz=640,
      focus_area=focus_area,
      start_frame_id=st.session_state['current_frame_id'],
  ):
      # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
      processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

      # =========================== sticky plates ========================
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
      # ========================================================================

      # Check if clipped_license_plate is valid before trying to process it
      if clipped_license_plate is not None:
          # Convert the license plate to RGB format
          clipped_license_plate_rgb = cv2.cvtColor(
              clipped_license_plate, cv2.COLOR_BGR2RGB
          )

          # Ensure a fixed height for the license plate image while maintaining the aspect ratio
          target_height = 80  # Set a fixed height
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
      vehicle_status.write(f"#### {status if status else 'Unknown Vehicle'}")

      # Display the frame in the Streamlit app
      stframe.image(processed_frame_rgb, channels="RGB")

      # Update buttons based on the latest plate text
      if st.session_state.get('last_detected_plate_text'):
          # Generate a unique key using license_plate_text and track_id
          unique_identifier = f"{st.session_state['last_detected_plate_text']}_{track_id}_{int(time.time())}_{random.randint(0,9999)}"

          # Enable buttons with unique keys

          with col32:
              info_button.button(
                ":material/info:",
                on_click=search_car_history,
                args=(st.session_state['last_detected_plate_text'],save_file_path),
                key=f"info-{unique_identifier}"
              )
          with button_col1:
              add_whitelist.button(
                  "Add to Whitelist",
                  on_click=update_cars_data,
                  args=(
                      st.session_state['last_detected_plate_text'],
                      "whitelist",
                      cars_data_path
                  ),
                  key=f"whitelist-{unique_identifier}"
              )
          with button_col2:
              add_blacklist.button(
                  "Add to Blacklist",
                  on_click=update_cars_data,
                  args=(
                      st.session_state['last_detected_plate_text'],
                      "blacklist",
                      cars_data_path
                  ),
                  key=f"blacklist-{unique_identifier}"
              )
      else:
          # Generate a unique key to prevent duplication in disabled buttons
          disabled_key_whitelist = f"disabled-whitelist-{int(time.time())}_{random.randint(0,9999)}"
          disabled_key_blacklist = f"disabled-blacklist-{int(time.time())}_{random.randint(0,9999)}"
          
          # Disable buttons with unique keys
          with button_col1:
              add_whitelist.button(
                  "Add to Whitelist",
                  disabled=True,
                  key=disabled_key_whitelist
              )
          with button_col2:
              add_blacklist.button(
                  "Add to Blacklist",
                  disabled=True,
                  key=disabled_key_blacklist
              )

      # Save results if toggle is enabled
      if save_stream and None not in (track_id, license_plate_text):
          data_record = create_data_record(track_id, license_plate_text, confidence)
          append_to_save_file(save_file_path, gate_name, data_record)

      # Add a small delay to allow Streamlit to re-render
      time.sleep(0.01)

      # Optionally, you could add a condition to break the loop based on some state
      if stop_button:
          break
      
#======================================================================================================================
# import streamlit as st
# import cv2
# import numpy as np
# import pandas as pd
# import time

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

# vehicle_model = "apps/gate/models/vehicle_detector.pt"
# license_plate_model = "apps/gate/models/license_plate_detector.pt"
# cars_data_path = "apps/gate/data/cars_data.xlsx"
# GATE_DATA = "apps/gate/data/gate_data.json"
# # Duration to keep displaying the last detected plate (in seconds)
# KEEP_PLATE_TIME =15  # Adjust the number of seconds as needed

# # Load the cars_data Excel file once at the beginning
# cars_df = pd.read_excel(cars_data_path)




# def gate_page():
# #==================================State management ================================#
#     if 'current_frame_id' not in st.session_state:
#         st.session_state['current_frame_id'] = 70
#     if 'license_plate_text' not in st.session_state:
#         st.session_state['license_plate_text'] = None
#            # Initialize session state variables
#     if 'last_detected_plate_image' not in st.session_state:
#         st.session_state['last_detected_plate_image'] = None
#     if 'last_detected_plate_text' not in st.session_state:
#         st.session_state['last_detected_plate_text'] = None
#     if 'last_detected_plate_time' not in st.session_state:
#         st.session_state['last_detected_plate_time'] = 0


#     # if "button_pressed" not in st.session_state:
#     #     st.session_state.button_pressed = False
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
#                 (80, 240, 3), dtype=np.uint8
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
#             # with col41:
#                 # add_to_whitelist = st.button(
#                 #     "Add to Whitelist",
#                 #     on_click=update_cars_data,
#                 #     # args= (st.session_state['last_detected_plate_text'], "whitelist",cars_data_path))
#                 #     args= (license_plate_text, "whitelist",cars_data_path))
#             # with col42:
#             #     add_to_blacklist = st.button(
#             #         "Add to Blacklist",
#             #         on_click=update_cars_data,
#             #         args= (license_plate_text, "blacklist",cars_data_path))

#             with col41:
#                 if st.session_state.get('last_detected_plate_text'):
#                     st.button(
#                         "Add to Whitelist",
#                         on_click=update_cars_data,
#                         args=(st.session_state['last_detected_plate_text'], "whitelist", cars_data_path)
#                     )
#                 else:
#                     st.button("Add to Whitelist", disabled=True)

#             with col42:
#                 if st.session_state.get('last_detected_plate_text'):
#                     st.button(
#                         "Add to Blacklist",
#                         on_click=update_cars_data,
#                         args=(st.session_state['last_detected_plate_text'], "blacklist", cars_data_path)
#                     )
#                 else:
#                     st.button("Add to Blacklist", disabled=True)
#     # Define the path for saving results
#     save_file_path = "apps/gate/saved_resultsa3.json"  # JSON Lines format

#     # # Initialize the JSON file if saving is enabled
#     # if save_stream:
#     #     initialize_save_file(save_file_path)

#     # Call the plate_detector function and display frames in real-time
#     for (
#         processed_frame,
#         clipped_license_plate,
#         license_plate_text,
#         fps,
#         track_id,
#         confidence,
#         st.session_state['current_frame_id'],
#         #current_frame_id,
#     ) in plate_detector(
#         video_source,
#         license_plate_model,
#         vehicle_model=vehicle_model,
#         imgsz=640,
#         focus_area=focus_area,
#         start_frame_id=st.session_state['current_frame_id'],
#     ):
#         # Convert the frame to RGB format (Streamlit expects RGB, while OpenCV uses BGR)
#         processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)


# #===========================sticky plates=======================
#         # Update session state if a new plate is detected
#         if clipped_license_plate is not None:
#             # New license plate detected
#             st.session_state['last_detected_plate_image'] = clipped_license_plate
#             st.session_state['last_detected_plate_text'] = license_plate_text
#             st.session_state['last_detected_plate_time'] = time.time()
#         else:
#             # No new license plate detected
#             time_since_last_plate = time.time() - st.session_state['last_detected_plate_time']
#             if time_since_last_plate <= KEEP_PLATE_TIME:
#                 # Use the last detected plate
#                 clipped_license_plate = st.session_state['last_detected_plate_image']
#                 license_plate_text = st.session_state['last_detected_plate_text']
#             else:
#                 # Clear the last detected plate
#                 st.session_state['last_detected_plate_image'] = None
#                 st.session_state['last_detected_plate_text'] = None
#                 clipped_license_plate = None
#                 license_plate_text = None
# #=========================================================================


#         # Check if clipped_license_plate is valid before trying to process it
#         if clipped_license_plate is not None:
#             # Convert the license plate to RGB format
#             clipped_license_plate_rgb = cv2.cvtColor(
#                 clipped_license_plate, cv2.COLOR_BGR2RGB
#             )

#             # Ensure a fixed height for the license plate image while maintaining the aspect ratio
#             target_height = 80  # Set a fixed height
#             h, w, _ = clipped_license_plate_rgb.shape
#             aspect_ratio = w / h
#             new_width = int(target_height * aspect_ratio)

#             # Resize the image to the new dimensions
#             resized_plate = cv2.resize(
#                 clipped_license_plate_rgb, (new_width, target_height)
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
#         status = check_vehicle_status(cars_df, st.session_state['last_detected_plate_text'])
#         # status = check_vehicle_status(cars_df, license_plate_text)
#         vehicle_status.write(f"#### {status if status else 'Unknown Vehicle'}")

#         # Display the frame in the Streamlit app
#         stframe.image(processed_frame_rgb, channels="RGB")

#         # Save results if toggle is enabled
#         if None not in (save_stream, track_id, license_plate_text):
#             initialize_save_file(save_file_path)
#             data_record = create_data_record(track_id, license_plate_text, confidence)
#             append_to_save_file(save_file_path, gate_name, data_record)