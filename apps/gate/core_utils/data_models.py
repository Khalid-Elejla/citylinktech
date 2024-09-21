from typing import List
import numpy as np
from pydantic import BaseModel

class BBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int
    track_id: int = 0
    confidence: float = 0.0
    class_id: int

class FrameData(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    frame: np.ndarray
    vehicles_bbox: List[BBox]
    license_plates_bbox: List[BBox]
