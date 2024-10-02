from typing import List, Dict
from .data_models import BBox

def suppress_plates_bbox(vehicles_bbox: List[BBox], license_plates_bbox: List[BBox]) -> List[BBox]:
    vehicle_boxes_map: Dict[int, BBox] = {}  # Map to store the highest confidence license plate bbox for each vehicle

    for plate_bbox in license_plates_bbox:
        for vehicle_bbox in vehicles_bbox:
            if (plate_bbox.x1 >= vehicle_bbox.x1 and plate_bbox.y1 >= vehicle_bbox.y1 and
                plate_bbox.x2 <= vehicle_bbox.x2 and plate_bbox.y2 <= vehicle_bbox.y2):
                if vehicle_bbox.track_id not in vehicle_boxes_map or plate_bbox.confidence > vehicle_boxes_map[vehicle_bbox.track_id].confidence:
                    vehicle_boxes_map[vehicle_bbox.track_id] = plate_bbox

    return list(vehicle_boxes_map.values())