import cv2
import numpy as np

class ImageEnhancer:
    def __init__(self):
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def apply_gamma_correction(self, image, gamma=1.2):
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(image, table)

    def enhance_visibility(self, frame):
        """
        Apply CLAHE to L-channel of LAB color space to improve contrast (fog/rain/glare).
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_enhanced = self.clahe.apply(l)
        lab_merged = cv2.merge((l_enhanced, a, b))
        return cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR)

    def preprocess(self, frame):
        # Apply enhancements
        frame = self.enhance_visibility(frame)
        # Optional: Gamma correction if needed explicitly, but CLAHE often suffices for local contrast
        return frame
