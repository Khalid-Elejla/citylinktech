from time import time
import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import tempfile

def get_ice_servers():
    """Use Twilio's TURN server or fallback to Google's STUN server."""
    # Fallback to Google's STUN server (you can add Twilio logic if needed)
    return [{"urls": ["stun:stun.l.google.com:19302"]}]

def history_page():
    @st.fragment
    def s():
        if st.button("AAAA"):
            print("AAA")
    s() 
    # Add a source selection: Webcam or File upload
    @st.fragment
    def KKK():
        source_type = st.radio("Select video source", ("Webcam", "Upload Video"))

        if source_type == "Upload Video":
            # Video file upload
            uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
            if uploaded_file is not None:
                # Save the uploaded video to a temporary file
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name

                # Use OpenCV to read the video file and display frames
                cap = cv2.VideoCapture(video_path)

                stframe = st.empty()  # Placeholder for video frames

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Display the frame using Streamlit
                    stframe.image(frame, channels="BGR")

                cap.release()
        else:
            # Webcam streaming
            def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
                # Convert the frame to an ndarray (OpenCV format)
                image = frame.to_ndarray(format="bgr24")
                
                # Just return the frame without any modifications
                return av.VideoFrame.from_ndarray(image, format="bgr24")

            # Set up the WebRTC streamer for webcam streaming
            webrtc_ctx = webrtc_streamer(
                key="video-stream",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration={
                    "iceServers": get_ice_servers(),
                    "iceTransportPolicy": "relay",
                },
                video_frame_callback=video_frame_callback,
                media_stream_constraints={"video": True, "audio": False},
            )

            st.markdown("### Live Webcam Stream")

    KKK()
# Call the history_page function to run the stream
# history_page()
