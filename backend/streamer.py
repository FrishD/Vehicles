import cv2
import time

class VideoStreamer:
    def __init__(self, source=0):
        """
        source: 0 for webcam, or string for file path/RTSP url.
        """
        self.source = source
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {source}")

    def get_frame(self):
        if not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            print("End of video stream. Looping...")
            # Attempt to loop
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                print(f"Failed to loop video stream: {self.source}")
                return None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
