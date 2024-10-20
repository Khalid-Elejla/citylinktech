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
import asyncio


def plate_detector(source, license_plate_model, vehicle_model=None, imgsz=640, focus_area=None, start_frame_id=0):
    cap = cv2.VideoCapture(source)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Check if it's a video file or stream
    is_stream = fps == 0  # Streams generally have no fps set
    
    # Set the starting frame for video files, ignore for streams
    if not is_stream:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_id)

    # Manual frame counter for streams or videos
    frame_counter = start_frame_id

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # For streams or videos, increment the frame counter manually
        current_frame_id = frame_counter
        frame_counter += 1

        # If a focus area is specified, apply masking
        if focus_area is not None:
            masked_frame = mask_frame(frame, focus_area, show=True)
        else:
            masked_frame = frame

        # Vehicle detection
        if vehicle_model is not None:
            # Detect vehicles
            vehicle_detector = YOLO(vehicle_model)
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

        # License plate detection
        license_plate_detector = YOLO(license_plate_model)
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
        if vehicle_model is not None:
            filtered_license_plates_bbox = suppress_plates_bbox(vehicles_bbox, license_plates_bbox)
        else:
            filtered_license_plates_bbox = license_plates_bbox

        # Get cropped license plates (optional)
        clipped_license_plate, track_id, confidence = clip_plate(frame, filtered_license_plates_bbox)

        # Convert the clipped license plate image to text using OCR
        if clipped_license_plate is not None:
            license_plate_text = perform_ocr_on_frames(clipped_license_plate)
        else:
            license_plate_text = None

        # Draw bounding boxes on the original frame
        # processed_frame = draw_bounding_box(frame, vehicles_bbox, filtered_license_plates_bbox, vehicle_names, license_plate_names)
        processed_frame = draw_bounding_box(frame=frame, license_plates_bbox=filtered_license_plates_bbox,license_plate_names= license_plate_names)

        # Yield the processed frame, clipped license plate, text, fps, track_id, confidence, and current frame id
        print(f"Processing frame {current_frame_id}")
        yield processed_frame, clipped_license_plate, license_plate_text, fps, track_id, confidence, current_frame_id

    cap.release()
    cv2.destroyAllWindows()