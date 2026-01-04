import cv2
import numpy as np

# Try to import easyocr, with graceful fallback if not available
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not available. LPR will return 'Unavailable'.")

# Global reader to avoid reloading model every time (Expensive!)
reader = None

def get_reader():
    global reader
    if not EASYOCR_AVAILABLE:
        return None
    if reader is None:
        print("Initializing EasyOCR Reader... (This might take a moment)")
        try:
            reader = easyocr.Reader(['en'], gpu=False)  # Use CPU for stability
        except Exception as e:
            print(f"Failed to initialize EasyOCR: {e}")
            return None
    return reader

def read_license_plate(image):
    """
    Reads text from an image crop (Vehicle/Plate).
    Returns the most confident text found.
    """
    if not EASYOCR_AVAILABLE:
        return "LPR Unavailable"
    
    try:
        r = get_reader()
        if r is None:
            return "LPR Error"
            
        # allowlist could be alphanumeric only
        results = r.readtext(image, detail=1, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # results format: ([[x,y], [x,y]...], text, confidence)
        best_text = ""
        max_conf = 0.0
        
        for (bbox, text, conf) in results:
            if conf > max_conf and len(text) > 3: # Ignore noise
                max_conf = conf
                best_text = text
        
        return best_text if best_text else "Unknown"
    except Exception as e:
        print(f"LPR Error: {e}")
        return "Error"
