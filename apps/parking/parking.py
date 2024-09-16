import streamlit as st
import tempfile
import json
import cv2  # OpenCV for capturing live video
from .detect_parking import run_parking_detection
from pytube import YouTube  # Import pytube to handle YouTube streams

DEMO_VIDEO = 'new.mp4'
PARKING_SPOTS_FILE = 'apps/parking/parking_spots.json'

def get_youtube_stream_url(youtube_url):
    """Fetch the YouTube stream URL using pytube."""
    yt = YouTube(youtube_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    return stream.url

def load_parking_spot_data(video_key):
    """Load the parking spots and video source for the selected parking spot."""
    with open(PARKING_SPOTS_FILE, 'r') as file:
        data = json.load(file)
    parking_data = data.get(video_key, {})
    video_type = parking_data.get('type', DEMO_VIDEO)
    video_source = parking_data.get('video_source', DEMO_VIDEO)
    coordinates = parking_data.get('coordinates', [])
    return video_type, video_source, [list(map(tuple, spots)) for spots in coordinates]

def load_parking_spot_keys():
    """Load all available keys from the parking spots JSON."""
    with open(PARKING_SPOTS_FILE, 'r') as file:
        data = json.load(file)
    return list(data.keys())

def parking_page():
    # Load parking spot keys for the select box
    parking_spot_keys = load_parking_spot_keys()
    selected_spot = st.selectbox('Select Parking Spot', parking_spot_keys)


    video_type, video_source, parking_spots = load_parking_spot_data(selected_spot)


    if video_type=="youtube_stream":
        try:
            video_source = get_youtube_stream_url(video_source)
        except Exception as e:
            st.error(f"Error fetching YouTube stream: {e}")
            return
        

    with st.expander("info"):
        st.write(selected_spot, video_type, video_source, parking_spots)

    model_path = "apps/parking/models/vehicle_detector.pt"
    
    # Option for live webcam streaming
    use_webcam = st.sidebar.checkbox('Use Webcam for Live Streaming')
    
    # Handle file uploader
    video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])
    
    # Determine the video source based on user selection
    # if use_webcam:
    #     video_source = 0  # Webcam video source (0 is typically the default camera)
    # elif video_file_buffer:
    #     tfflie = tempfile.NamedTemporaryFile(delete=False)
    #     tfflie.write(video_file_buffer.read())
    #     video_source = tfflie.name  # Use uploaded video as source
    # else:
    #     video_source, parking_spots = load_parking_spot_data(selected_spot)  # Use selected parking spot video
    
    stop_button = st.sidebar.button('Stop Processing')
    if stop_button:
        st.stop()

    show_boxes = st.checkbox('Show Vehicle Bounding Boxes', value=False)

    col1, col2, col3 = st.columns([8, 1, 3])
    with col1:
        stframe = st.empty()

    with col3:
        counter_display = st.empty()

    # Run parking detection with live video feed or uploaded video
    run_parking_detection(
        video_source=video_source,
        model_path=model_path,
        parking_spots=parking_spots,
        stframe=stframe,
        show_boxes=show_boxes,
        counter_display=counter_display
    )


# import streamlit as st
# import tempfile
# import json
# from .detect_parking import run_parking_detection

# DEMO_VIDEO = 'new.mp4'
# PARKING_SPOTS_FILE = 'apps/parking/parking_spots.json'

# def load_parking_spot_data(video_key):
#     """Load the parking spots and video source for the selected parking spot."""
#     with open(PARKING_SPOTS_FILE, 'r') as file:
#         data = json.load(file)
#     parking_data = data.get(video_key, {})
#     video_source = parking_data.get('video_source', DEMO_VIDEO)
#     coordinates = parking_data.get('coordinates', [])
#     return video_source, [list(map(tuple, spots)) for spots in coordinates]

# def load_parking_spot_keys():
#     """Load all available keys from the parking spots JSON."""
#     with open(PARKING_SPOTS_FILE, 'r') as file:
#         data = json.load(file)
#     return list(data.keys())

# def parking_page():
#     # Load parking spot keys for the select box
#     parking_spot_keys = load_parking_spot_keys()
    
    
#     selected_spot = st.selectbox('Select Parking Spot', parking_spot_keys)
#     st.write(selected_spot)
    
#     # use_webcam = st.sidebar.button('Use Webcam')
#     # video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

#     video_source, parking_spots = load_parking_spot_data(str(selected_spot))
#     st.write(video_source, parking_spots)

#     model_path = "apps/parking/models/vehicle_detector.pt"
#     # parking_spots = []
#     # video_source = None

#     # if use_webcam:
#     #     video_source = 0  # Webcam video source
#     #     video_source, parking_spots = load_parking_spot_data(str(video_source))
#     # elif video_file_buffer:
#     tfflie = tempfile.NamedTemporaryFile(delete=False)
#     tfflie.write(video_file_buffer.read())
#     # video_source = tfflie.name  # Use uploaded video as source
#     # _, parking_spots = load_parking_spot_data(video_file_buffer.name)
#     # else:
#         # # Use the selected parking spot data
#         # video_source, parking_spots = load_parking_spot_data(selected_spot)

#     stop_button = st.sidebar.button('Stop Processing')
#     if stop_button:
#         st.stop()

#     show_boxes = st.checkbox('Show Vehicle Bounding Boxes', value=False)
    
#     col1, col2, col3 = st.columns([8, 1, 3])
#     with col1:
#         stframe = st.empty()

#     with col3:
#         counter_display = st.empty()

#     run_parking_detection(
#         video_source=video_source,
#         model_path=model_path,
#         parking_spots=parking_spots,
#         stframe=stframe,
#         show_boxes=show_boxes,
#         counter_display=counter_display
#     )

    # st.success('Processing complete')

###########################################################################
# import streamlit as st
# import tempfile
# import json
# from .detect_parking import run_parking_detection

# DEMO_VIDEO = 'new.mp4'
# PARKING_SPOTS_FILE = 'apps/parking/parking_spots.json'

# def load_parking_spots(video_filename):
#     with open(PARKING_SPOTS_FILE, 'r') as file:
#         data = json.load(file)
#     return [list(map(tuple, spots)) for spots in data.get(video_filename, [])]

# def parking_page():
#     use_webcam = st.sidebar.button('Use Webcam')
#     video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

#     model_path = "apps/parking/models/vehicle_detector.pt"
#     parking_spots = []
#     video_source = None

#     if use_webcam:
#         video_source = 0
#         parking_spots = load_parking_spots(str(video_source))
#         print(parking_spots)
#     elif video_file_buffer:
#         tfflie = tempfile.NamedTemporaryFile(delete=False)
#         tfflie.write(video_file_buffer.read())
#         video_source = tfflie.name
#         parking_spots = load_parking_spots(video_file_buffer.name)
#     else:
#         video_source = DEMO_VIDEO
#         parking_spots = load_parking_spots(DEMO_VIDEO)

#     stop_button = st.sidebar.button('Stop Processing')
#     if stop_button:
#         st.stop()

#     show_boxes = st.sidebar.checkbox('Show Vehicle Bounding Boxes', value=False)
    
#     col1, col2, col3 = st.columns([8, 1, 3])
#     with col1:
#         stframe = st.empty()

#     with col3:
#         counter_display = st.empty()

#     run_parking_detection(
#         video_source=video_source,
#         model_path=model_path,
#         parking_spots=parking_spots,
#         stframe=stframe,
#         show_boxes=show_boxes,
#         counter_display=counter_display
#     )

#     st.success('Processing complete')

################################################################################
# import streamlit as st
# import tempfile
# import json
# from .detect_parking import run_parking_detection

# DEMO_VIDEO = 'new.mp4'
# PARKING_SPOTS_FILE = 'apps/parking/parking_spots.json'

# def load_parking_spots(video_filename):
#     with open(PARKING_SPOTS_FILE, 'r') as file:
#         data = json.load(file)
#     return [list(map(tuple, spots)) for spots in data.get(video_filename, [])]

# def parking_page():
#     use_webcam = st.sidebar.button('Use Webcam')
#     video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

#     model_path = "apps/parking/models/vehicle_detector.pt"
#     parking_spots = []
#     video_source = None

#     if use_webcam:
#         video_source = 0
#         parking_spots = load_parking_spots(str(video_source))
#         print(parking_spots)
#     elif video_file_buffer:
#         tfflie = tempfile.NamedTemporaryFile(delete=False)
#         tfflie.write(video_file_buffer.read())
#         video_source = tfflie.name
#         parking_spots = load_parking_spots(video_file_buffer.name)
#     else:
#         video_source = DEMO_VIDEO
#         parking_spots = load_parking_spots(DEMO_VIDEO)

#     stop_button = st.sidebar.button('Stop Processing')
#     if stop_button:
#         st.stop()

#     show_boxes = st.sidebar.checkbox('Show Vehicle Bounding Boxes', value=False)
    
#     col1, col2, col3 = st.columns([8, 1, 3])
#     with col1:
#         stframe = st.empty()

#     with col3:
#         counter_display = st.empty()

#     run_parking_detection(
#         video_source=video_source,
#         model_path=model_path,
#         parking_spots=parking_spots,
#         stframe=stframe,
#         show_boxes=show_boxes,
#         counter_display=counter_display
#     )

#     st.success('Processing complete')

# # def parking_page():
# #     use_webcam = st.sidebar.button('Use Webcam')
# #     video_file_buffer = st.sidebar.file_uploader("Upload a video", type=["mp4", "mov", 'avi', 'asf', 'm4v'])

# #     model_path = "apps/parking/models/vehicle_detector.pt"
# #     parking_spots = []
# #     video_source = None

# #     if use_webcam:
# #         video_source = 0
# #         parking_spots = load_parking_spots(str(video_source))
# #         print(parking_spots)
# #     elif video_file_buffer:
# #         tfflie = tempfile.NamedTemporaryFile(delete=False)
# #         tfflie.write(video_file_buffer.read())
# #         video_source = tfflie.name
# #         parking_spots = load_parking_spots(video_file_buffer.name)
# #     else:
# #         video_source = DEMO_VIDEO
# #         parking_spots = load_parking_spots(DEMO_VIDEO)

# #     stop_button = st.sidebar.button('Stop Processing')
# #     if stop_button:
# #         st.stop()

# #     show_boxes = st.sidebar.checkbox('Show Vehicle Bounding Boxes', value=False)
    
# #     col1, col2, col3 = st.columns([8, 1, 1], gap="small", vertical_alignment="bottom")
# #     with col1:
# #         stframe = st.empty()

# #     with col3:
# #         st.write("YES")

# #     run_parking_detection(
# #         video_source=video_source,
# #         model_path=model_path,
# #         parking_spots=parking_spots,
# #         stframe=stframe,
# #         show_boxes=show_boxes
# #     )

# #     st.success('Processing complete')