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
            # Using gpu=False for broader compatibility, can be set to True if a CUDA-enabled GPU is available
            reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            print(f"Failed to initialize EasyOCR: {e}")
            return None
    return reader

def preprocess_for_ocr(image):
    """
    Applies a series of preprocessing steps to an image to enhance OCR accuracy.
    """
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Noise Reduction using Bilateral Filter
    # This is effective at removing noise while preserving edges
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # 3. Adaptive Thresholding
    # This can handle varying lighting conditions better than a simple global threshold
    thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    return thresh

def read_license_plate(image):
    """
    Reads text from an image crop (Vehicle/Plate) after preprocessing.
    Returns the most confident text found.
    """
    if not EASYOCR_AVAILABLE:
        return "LPR Unavailable"
    
    try:
        r = get_reader()
        if r is None:
            return "LPR Error"

        # Preprocess the image for better OCR results
        preprocessed_image = preprocess_for_ocr(image)
            
        # allowlist for characters typically found on license plates
        results = r.readtext(preprocessed_image, detail=1, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-')
        
        # Filter results based on confidence and basic heuristics
        # (e.g., length, character composition)
        best_text = ""
        max_conf = 0.0
        
        for (bbox, text, conf) in results:
            # Clean up common OCR errors if necessary (e.g., 'O' vs '0')
            # For now, we'll keep it simple
            if conf > max_conf and len(text) >= 4: # A reasonable minimum length for a plate
                max_conf = conf
                best_text = text.strip().replace(" ", "") # Remove whitespace
        
        return best_text if best_text else "Unknown"
    except Exception as e:
        print(f"LPR Error during processing: {e}")
        return "Error"
