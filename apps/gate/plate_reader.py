# app/main.py

import os
from apps.gate.core_utils.ocr_utils import perform_ocr_on_frames
import cv2
import numpy as np
import argparse
from datetime import datetime
from typing import List
from ultralytics import YOLO
from .core_utils.data_models import BBox
from .core_utils.image_utils import clip_plate, mask_frame, draw_bounding_box
from .core_utils.bbox_utils import suppress_plates_bbox


def plate_detector(source, license_plate_model, vehicle_model=None, imgsz=640, focus_area=None):
    cap = cv2.VideoCapture(source)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # if not out.isOpened():
    #     print("Error: Could not open video writer.")
    #     cap.release()
    #     exit()


    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        

        if focus_area is not None:
            masked_frame=mask_frame(frame, focus_area, show=True)
        else:
            masked_frame=frame

        # Vehicle detection
        if vehicle_model is not None:
            # Detect vehicles
            vehicle_detector=YOLO(vehicle_model)
            vehicle_results = vehicle_detector.track(masked_frame, imgsz=imgsz, persist=True, tracker="bytetrack.yaml")

            vehicles_bbox = [
                BBox(
                    x1=int(bbox[0]), 
                    y1=int(bbox[1]), 
                    x2=int(bbox[2]), 
                    y2=int(bbox[3]), 
                    track_id=int(bbox[4]) if len(bbox) > 6 else 0,
                    confidence=float(bbox[5]) if len(bbox) > 6 else float(bbox[4]), 
                    class_id=int(bbox[6]) if len(bbox) > 6 else float(bbox[5])
                )
                for bbox in vehicle_results[0].boxes.data.tolist()
            ]

            vehicle_names = vehicle_results[0].names

            # Mask the frame based on vehicle bounding boxes
            # masked_frame = mask_frame(frame, vehicles_bbox)
        


        # Detect license plates in the masked frame
        license_plate_detector=YOLO(license_plate_model)
        license_plate_results = license_plate_detector.track(masked_frame, persist=True, tracker="bytetrack.yaml")
        
        license_plates_bbox = [
            BBox(
                x1=int(bbox[0]), 
                y1=int(bbox[1]), 
                x2=int(bbox[2]), 
                y2=int(bbox[3]), 
                track_id=int(bbox[4]) if len(bbox) > 6 else 0,
                confidence=float(bbox[5]) if len(bbox) > 6 else float(bbox[4]), 
                class_id=int(bbox[6]) if len(bbox) > 6 else float(bbox[5])
            )
            for bbox in license_plate_results[0].boxes.data.tolist()
        ]
        
        license_plate_names = license_plate_results[0].names

        # Filter license plate bounding boxes based on vehicle bounding boxes
        filtered_license_plates_bbox = suppress_plates_bbox(vehicles_bbox, license_plates_bbox)

        # get cropped license plates (optional)
        clipped_license_plate=clip_plate(frame, filtered_license_plates_bbox)

        # convert image to text
        if clipped_license_plate is not None:
            license_plate_text= perform_ocr_on_frames(clipped_license_plate)
        else:
            license_plate_text=None

        # Draw bounding boxes on the original frame
        processed_frame = draw_bounding_box(frame, vehicles_bbox, filtered_license_plates_bbox, vehicle_names, license_plate_names)


        # Yield the processed frame to the caller
        yield processed_frame,clipped_license_plate,license_plate_text, fps

        # Write the processed frame to the output video
        # out.write(processed_frame)
        # cv2.imshow('Frame', processed_frame)
        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    # out.release()
    # cv2.destroyAllWindows()



def parse_args():
    parser = argparse.ArgumentParser(description='Vehicle and License Plate Detection')

    parser.add_argument('-i', '--input', type=str, required=True, help='Path to input video file')
    parser.add_argument('-vm', '--vehicle_model', type=str, required=True, help='Path to vehicle detection model')
    parser.add_argument('-lm', '--license_plate_model', type=str, required=True, help='Path to license plate detection model')
    parser.add_argument('-s', '--imgsz', type=int, default=640, help='Image size for detection')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to save the output video')

    return parser.parse_args()

def main():

    # def run_parking_detection(video_source: Union[str, int], model_path: str, parking_spots: list, stframe, show_boxes: bool, counter_display):

    args = parse_args()

    video_path = args.input
    vehicle_detector = YOLO(args.vehicle_model)
    license_plate_detector = YOLO(args.license_plate_model)
    imgsz = args.imgsz
    output_path = args.output

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("Error: Could not open video writer.")
        cap.release()
        exit()


    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # Detect vehicles
        vehicle_results = vehicle_detector.track(frame, imgsz=imgsz, persist=True, tracker="bytetrack.yaml")

        vehicles_bbox = [
            BBox(
                x1=int(bbox[0]), 
                y1=int(bbox[1]), 
                x2=int(bbox[2]), 
                y2=int(bbox[3]), 
                track_id=int(bbox[4]) if len(bbox) > 6 else 0,
                confidence=float(bbox[5]) if len(bbox) > 6 else float(bbox[4]), 
                class_id=int(bbox[6]) if len(bbox) > 6 else float(bbox[5])
            )
            for bbox in vehicle_results[0].boxes.data.tolist()
        ]

        vehicle_names = vehicle_results[0].names

        # Mask the frame based on vehicle bounding boxes
        masked_frame = mask_frame(frame, vehicles_bbox)
        
        # Detect license plates in the masked frame
        license_plate_results = license_plate_detector.track(masked_frame, persist=True, tracker="bytetrack.yaml")
        
        license_plates_bbox = [
            BBox(
                x1=int(bbox[0]), 
                y1=int(bbox[1]), 
                x2=int(bbox[2]), 
                y2=int(bbox[3]), 
                track_id=int(bbox[4]) if len(bbox) > 6 else 0,
                confidence=float(bbox[5]) if len(bbox) > 6 else float(bbox[4]), 
                class_id=int(bbox[6]) if len(bbox) > 6 else float(bbox[5])
            )
            for bbox in license_plate_results[0].boxes.data.tolist()
        ]
        
        license_plate_names = license_plate_results[0].names

        # Filter license plate bounding boxes based on vehicle bounding boxes
        filtered_license_plates_bbox = suppress_plates_bbox(vehicles_bbox, license_plates_bbox)

        # Save cropped license plates (optional)
        #save_clipped_frames(frame, filtered_license_plates_bbox, 'cropped_license_plates')

        # Draw bounding boxes on the original frame
        processed_frame = draw_bounding_box(frame, vehicles_bbox, filtered_license_plates_bbox, vehicle_names, license_plate_names)

        # Write the processed frame to the output video
        out.write(processed_frame)
        cv2.imshow('Frame', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()











# def run_parking_detection(video_source: Union[str, int], model_path: str, parking_spots: list, stframe, show_boxes: bool, counter_display):
#     model = YOLO(model_path)
#     cap = cv2.VideoCapture(video_source)
    
#     if not cap.isOpened():
#         stframe.text("Error: Could not open video source.")
#         print("Error: Could not open video source.")
#         return

#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = cap.get(cv2.CAP_PROP_FPS) if isinstance(video_source, str) else 30
#     output_path = 'output5.mp4' if isinstance(video_source, str) else None

#     if output_path:
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
#         if not out.isOpened():
#             stframe.text("Error: Could not open video writer.")
#             return

#     vehicle_names = ["person","car", "van", "bus", "truck", "heavy truck", "bicycle", "motorcycle"]

#     total_spots = len(parking_spots)
    
#     # New variables for frame skipping
#     frame_count = 0
#     process_every_n_frames = 300  # Process every 5th frame, adjust as needed
#     last_bboxes = []  # Store the last processed bounding boxes

#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             print("Failed to read frame from video source.")
#             break

#         frame_count += 1

#         # Process only every nth frame
#         if frame_count == 1 or frame_count % process_every_n_frames == 0:
#             results = model.track(frame)
#             if results:
#                 last_bboxes = [BBox(
#                     x1=int(box.xyxy[0].tolist()[0]),
#                     y1=int(box.xyxy[0].tolist()[1]),
#                     x2=int(box.xyxy[0].tolist()[2]),
#                     y2=int(box.xyxy[0].tolist()[3]),
#                     track_id=int(box.id) if box.id is not None else 0,
#                     confidence=box.conf.item(),
#                     class_id=int(box.cls.item())
#                 ) for r in results for box in r.boxes]
#             print("AAAAAAAAAAAAAAAAAAAAAAAA")

#         # Use the last processed bboxes for drawing and checking parking vacancy
#         if show_boxes:
#             frame = draw_bounding_box(frame, last_bboxes, vehicle_names)

#         frame, available_spots = check_parking_vacancy(frame, last_bboxes, parking_spots)

#         counter_display.markdown(
#             f"""
#             <div style="text-align: center; font-size: 20px; font-weight: bold;">
#             <div style="text-align: center; font-size: 30px; font-weight: bold;">
#                 Available Spots:<br>{available_spots}<br><br>
#                 Total Spots:<br>{total_spots}
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         if output_path:
#             out.write(frame)

#         stframe.image(frame, channels="BGR")

#     cap.release()
#     if output_path:
#         out.release()
#         stframe.text(f"Saved output video to {output_path}")
