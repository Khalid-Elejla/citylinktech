import cv2
import numpy as np
from typing import List
from .data_models import BBox


def mask_frame(frame: np.ndarray, focus_areas: List[List[List[int]]], show=None) -> np.ndarray:
    # Create a blank mask of the same height and width as the frame
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
    # Fill each polygon (focus area) on the mask
    for polygon in focus_areas:
        polygon_np = np.array(polygon, dtype=np.int32)
        cv2.fillPoly(mask, [polygon_np], 255)

        if show is not None:
            cv2.polylines(frame, [polygon_np], isClosed=True, color=(0, 255, 0), thickness=2)


    # Apply the mask to the frame
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    return masked_frame


def clip_plate(frame: np.ndarray, license_plates_bbox: List[BBox]) -> np.ndarray:
    if license_plates_bbox != []:
        highest_confidence_bbox = max(license_plates_bbox, key=lambda license_plates_bbox: license_plates_bbox.confidence)
        clipped_frame = frame[highest_confidence_bbox.y1:highest_confidence_bbox.y2, highest_confidence_bbox.x1:highest_confidence_bbox.x2]
        track_id = highest_confidence_bbox.track_id
        confidence = highest_confidence_bbox.confidence
    else:
        clipped_frame, track_id, confidence= [None,None,None]
        
    return clipped_frame, track_id, confidence

# def clip_plate(frame: np.ndarray, license_plates_bbox: List[BBox]) -> np.ndarray:
#     if license_plates_bbox != []:
#         highest_confidence_bbox = max(license_plates_bbox, key=lambda license_plates_bbox: license_plates_bbox.confidence)
#         clipped_frame = frame[highest_confidence_bbox.y1:highest_confidence_bbox.y2, highest_confidence_bbox.x1:highest_confidence_bbox.x2]
#     else:
#         clipped_frame = None
#     return clipped_frame


def draw_bounding_box(frame: np.ndarray,  license_plates_bbox: List[BBox],license_plate_names: List[str], 
                      vehicles_bbox: List[BBox]=None, vehicle_names: List[str]=None, ) -> np.ndarray:
    if vehicles_bbox is not None:
        for bbox in vehicles_bbox:
            cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 1)
            cv2.putText(frame, f"{vehicle_names[bbox.class_id]} {bbox.track_id} {bbox.confidence:.2f}", 
                        (bbox.x1, bbox.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for bbox in license_plates_bbox:
        cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (255, 0, 0), 2)
        cv2.putText(frame, f"{license_plate_names[bbox.class_id]} {bbox.track_id} {bbox.confidence:.2f}", 
                    (bbox.x1, bbox.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    return frame

def clip_frame(frame: np.ndarray, license_plates_bbox: List[BBox]) -> List[np.ndarray]:
    clipped_frames = []
    for bbox in license_plates_bbox:
        clipped_frame = frame[bbox.y1:bbox.y2, bbox.x1:bbox.x2]
        clipped_frames.append(clipped_frame)
    return clipped_frames