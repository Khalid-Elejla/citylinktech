import os
from datetime import datetime
import cv2
from typing import List
import numpy as np
from .data_models import BBox

def save_clipped_frames(frame: np.ndarray, license_plates_bbox: List[BBox], output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    print("Saving frames...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    for i, bbox in enumerate(license_plates_bbox):
        clipped_frame = frame[bbox.y1:bbox.y2, bbox.x1:bbox.x2]
        output_path = os.path.join(output_dir, f"clipped_frame_{timestamp}_{i}.jpg")
        cv2.imwrite(output_path, clipped_frame)
        print(f"Saved frame {i} to {output_path}")