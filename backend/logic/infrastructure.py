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

    def detect_infrastructure(self, frame, objects_to_mask=[]):
        """
        Detects both STOP LINES and CROSSWALKS using a combination of AI Segmentation and Bird's-Eye View (BEV) analysis.
        """
        h, w = frame.shape[:2]
        
        # AI-based masking to focus on relevant areas
        if self.seg_model:
            results = self.seg_model(frame, verbose=False)
            ai_mask = np.zeros((h, w), dtype=np.uint8)
            if results and results[0].masks is not None:
                for mask in results[0].masks.data:
                    m = mask.cpu().numpy().astype(np.uint8) * 255
                    m = cv2.resize(m, (w, h))
                    ai_mask = cv2.bitwise_or(ai_mask, m)
        else:
            ai_mask = np.ones((h, w), dtype=np.uint8) * 255

        # Image preprocessing
        roi_y_start = int(h * 0.25)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 140])
        upper_white = np.array([180, 80, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Apply masks
        final_mask = cv2.bitwise_and(white_mask, ai_mask)
        for obj in objects_to_mask:
            x1, y1, x2, y2 = obj['box']
            cv2.rectangle(final_mask, (int(x1), int(y1)), (int(x2), int(y2)), 0, -1)
        final_mask[:roi_y_start, :] = 0

        # BEV Transformation and Line Detection
        bev_mask = self.pm.to_bev(final_mask)
        lines = cv2.HoughLinesP(bev_mask, 1, np.pi/180, threshold=25, minLineLength=30, maxLineGap=20)
        
        if lines is None:
            return [], []

        # Process lines to find candidates for stop lines and crosswalks
        candidates = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if angle < 15 or angle > 165: # Horizontal lines in BEV
                candidates.append({'pts': [x1, y1, x2, y2], 'y_center': (y1 + y2) / 2, 'length': np.sqrt((x2 - x1)**2 + (y2 - y1)**2)})

        stop_lines = self._detect_stop_lines_from_candidates(candidates)
        crosswalks = self._detect_crosswalks_from_candidates(candidates)
            
        return stop_lines, crosswalks

    def _detect_stop_lines_from_candidates(self, candidates):
        if not candidates:
            return []

        # Stop lines are typically the longest single horizontal lines
        candidates.sort(key=lambda x: x['length'], reverse=True)
        
        # Assume top 2 longest lines are potential stop lines
        stop_line_cands = candidates[:2]

        stop_lines = []
        for cand in stop_line_cands:
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

    def _detect_crosswalks_from_candidates(self, candidates):
        if len(candidates) < 3:
            return []

        # Group lines by vertical proximity in BEV
        candidates.sort(key=lambda c: c['y_center'])
        groups = []
        current_group = [candidates[0]]
        for i in range(1, len(candidates)):
            if abs(candidates[i]['y_center'] - current_group[-1]['y_center']) < 15: # y_dist_threshold
                current_group.append(candidates[i])
            else:
                if len(current_group) >= 3: # min_lines_for_crosswalk
                    groups.append(current_group)
                current_group = [candidates[i]]
        if len(current_group) >= 3:
            groups.append(current_group)

        if not groups:
            return []

        # Find the largest group to designate as the crosswalk
        largest_group = max(groups, key=len)

        # Get the bounding polygon of the crosswalk in BEV
        min_x = min(min(line['pts'][0], line['pts'][2]) for line in largest_group)
        max_x = max(max(line['pts'][0], line['pts'][2]) for line in largest_group)
        min_y = min(line['y_center'] for line in largest_group)
        max_y = max(line['y_center'] for line in largest_group)

        # Map back to original perspective
        p1 = self.pm.map_point_from_bev(min_x, min_y)
        p2 = self.pm.map_point_from_bev(max_x, min_y)
        p3 = self.pm.map_point_from_bev(max_x, max_y)
        p4 = self.pm.map_point_from_bev(min_x, max_y)

        crosswalk_poly = np.array([p1, p2, p3, p4], dtype=np.int32)
        return [crosswalk_poly]
