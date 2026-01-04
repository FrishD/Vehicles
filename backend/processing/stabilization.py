from ultralytics import YOLO
import cv2
import numpy as np

class ObjectTracker:
    def __init__(self, model_path='yolov8n.pt'):
        # We load the model here for tracking capabilities
        self.model = YOLO(model_path)

    def track(self, frame):
        """
        Run YOLOv8 tracking on the frame.
        Returns the result object which contains boxes, ids, and classes.
        """
        # conf=0.15 to detect smaller objects (e.g. traffic lights)
        results = self.model.track(frame, persist=True, conf=0.15, verbose=False)
        return results[0]

class GMC:
    """
    Global Motion Compensation using Sparse Optical Flow (Lucas-Kanade).
    Estimates the movement of the CAMERA (Tx, Ty) between frames.
    """
    def __init__(self):
        self.prev_gray = None
        self.prev_pts = None
        self.frame_shape = None
        # ShiTomasi corner detection params
        self.feature_params = dict(maxCorners=200, qualityLevel=0.01, minDistance=30, blockSize=3)
        # LK Optical Flow params
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def apply(self, frame):
        """
        Calculates shift (dx, dy) from previous frame.
        Returns: (dx, dy) tuple.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        shift = (0, 0)

        # Check if frame size changed - reset if so
        if self.frame_shape is not None and gray.shape != self.frame_shape:
            print("Frame size changed, resetting GMC")
            self.prev_gray = None
            self.prev_pts = None

        self.frame_shape = gray.shape

        if self.prev_gray is not None:
            # Ensure we have valid points to track
            if self.prev_pts is None or len(self.prev_pts) < 10:
                self.prev_pts = cv2.goodFeaturesToTrack(self.prev_gray, mask=None, **self.feature_params)

            # Only proceed if we have valid points
            if self.prev_pts is not None and len(self.prev_pts) >= 10:
                try:
                    # Calculate optical flow
                    p1, st, err = cv2.calcOpticalFlowPyrLK(
                        self.prev_gray, gray, self.prev_pts, None, **self.lk_params
                    )

                    # Select good points (status 1)
                    if p1 is not None and st is not None:
                        good_new = p1[st==1]
                        good_old = self.prev_pts[st==1]

                        # Calculate average shift only if we have enough good points
                        if len(good_new) > 5:
                            shifts = good_new - good_old
                            dx = np.median(shifts[:, 0])  # Use median instead of mean for robustness
                            dy = np.median(shifts[:, 1])
                            shift = (dx, dy)

                        # Keep only good points for next iteration
                        self.prev_pts = good_new.reshape(-1, 1, 2)
                    else:
                        # Reset points if tracking failed
                        self.prev_pts = None

                except cv2.error as e:
                    print(f"GMC optical flow error: {e}")
                    # Reset on error
                    self.prev_pts = None
                    shift = (0, 0)

        # Update for next frame
        self.prev_gray = gray.copy()

        # Detect fresh points if we don't have enough
        if self.prev_pts is None or len(self.prev_pts) < 50:
            new_pts = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            if new_pts is not None:
                self.prev_pts = new_pts

        return shift