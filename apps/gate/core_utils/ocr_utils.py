import easyocr
from typing import List
import numpy as np

def perform_ocr_on_frames(clipped_frame: np.ndarray) -> List[str]:
    # Instantiate the EasyOCR reader for English and Arabic
    reader = easyocr.Reader(['en'])#, 'ar'])

    
    # Perform OCR on each clipped frame
    result = reader.readtext(clipped_frame, detail=0)  # detail=0 returns only the text
    recognized_text = ' '.join(result)  # Join multiple detected text lines
    print("recognized_text:",recognized_text)
    return recognized_text
