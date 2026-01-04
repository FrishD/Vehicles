import cv2
import numpy as np
from .perspective_utils import PerspectiveManager
from ultralytics import YOLO
import os

class InfrastructureLogic:
    def __init__(self, frame_size=(1920, 1080)):
        # Initialize Perspective Manager
        self.pm = PerspectiveManager(frame_size)
        self.frame_size = frame_size
        self.bev_lines = [] 
        
        # Load Segmentation Model
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'road_seg.pt')
        if os.path.exists(model_path):
            self.seg_model = YOLO(model_path)
            print(f"Loaded Segmentation Model: {model_path}")
        else:
            self.seg_model = None
            print("Warning: Segmentation model not found, falling back to heuristics.")

    def detect_crosswalks(self, frame, objects_to_mask=[]):
        """
        DETECTS STOP LINES using AI Segmentation + BEV.
        """
        h, w = frame.shape[:2]
        
        if self.seg_model:
            # 1. AI SEGMENTATION
            # Use segment model to find 'road' or 'markings' if classes are known.
            # Base yolov8n-seg has COCO classes. Road is not COCO, but we can look for contrast.
            # If we had a specialized model, we would filter by class.
            # For now, let's use the segmentation results to refine our white filter.
            results = self.seg_model(frame, verbose=False)
            ai_mask = np.zeros((h, w), dtype=np.uint8)
            
            if results and results[0].masks is not None:
                # If specialized, we'd pick class 'stop_line'. 
                # Since this is base model, we use it to focus on all segmented segments
                for mask in results[0].masks.data:
                    m = mask.cpu().numpy().astype(np.uint8) * 255
                    m = cv2.resize(m, (w, h))
                    ai_mask = cv2.bitwise_or(ai_mask, m)
        else:
            ai_mask = np.ones((h, w), dtype=np.uint8) * 255

        # 2. Search ROI
        roi_y_start = int(h * 0.25)
        roi_y_end = int(h * 0.95)
        
        # 3. White Filter (AI-Refined)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 140]) 
        upper = np.array([180, 80, 255]) 
        mask_white = cv2.inRange(hsv, lower, upper)
        
        # Combine AI Mask with White Filter
        mask_white = cv2.bitwise_and(mask_white, ai_mask)
        
        # Mask out vehicles
        for obj in objects_to_mask:
            x1, y1, x2, y2 = obj['box']
            cv2.rectangle(mask_white, (int(x1), int(y1)), (int(x2), int(y2)), 0, -1)

        mask_white[:roi_y_start, :] = 0
        mask_white[roi_y_end:, :] = 0

        # 4. BEV Transformation
        bev_mask = self.pm.to_bev(mask_white)
        
        # 5. Line Detection on BEV
        lines = cv2.HoughLinesP(
            bev_mask, 
            1, 
            np.pi/180, 
            threshold=25,
            minLineLength=30,
            maxLineGap=20
        )
        
        if lines is None: return []
        
        candidates = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx*dx + dy*dy)
            angle = abs(np.degrees(np.arctan2(dy, dx)))
            
            # In BEV, stop lines should be almost exactly horizontal (0 or 180 degrees)
            if angle < 15 or angle > 165:
                candidates.append({
                    'pts': [x1, y1, x2, y2],
                    'length': length
                })

        if not candidates: return []
        candidates.sort(key=lambda x: x['length'], reverse=True)
        
        stop_lines = []
        for cand in candidates[:2]: # Top 2 lines
            bx1, by1, bx2, by2 = cand['pts']
            p1 = self.pm.map_point_from_bev(bx1, by1)
            p2 = self.pm.map_point_from_bev(bx2, by2)
            
            pts = np.array([
                [int(p1[0]), int(p1[1]-4)],
                [int(p2[0]), int(p2[1]-4)],
                [int(p2[0]), int(p2[1]+4)],
                [int(p1[0]), int(p1[1]+4)]
            ], dtype=np.int32)
            stop_lines.append(pts)
            
        return stop_lines

