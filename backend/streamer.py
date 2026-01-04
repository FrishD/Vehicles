import cv2
import time

class VideoStreamer:
    def __init__(self, source=0):
        """
        source: 0 for webcam, or string for file path/RTSP url.
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {source}")
            # Fallback to dummy? Or raise error.
            # self.cap = cv2.VideoCapture(0) # Try default

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                # Loop video if file
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if ret: return frame
        return None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
