import cv2
import numpy as np
import time

class TrafficLightStateMachine:
    def __init__(self, tl_id):
        self.id = tl_id
        self.state = 'unknown' # current state
        self.last_state_change = time.time()
        self.history = [] # Buffer of last detected raw states
        self.HISTORY_SIZE = 5
        
        # BEHAVIORAL ASSOCIATION: 
        # Grid-based heatmap (40x40) to learn where cars stop during red
        self.GRID_SIZE = 40
        self.stop_heatmap = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=np.float32)

    def record_stop(self, x, y, w, h):
        """Records a vehicle stop at normalized coordinates x, y."""
        grid_x = int(np.clip(x * self.GRID_SIZE, 0, self.GRID_SIZE - 1))
        grid_y = int(np.clip(y * self.GRID_SIZE, 0, self.GRID_SIZE - 1))
        
        # Increment heatmap with a small Gaussian-like spread
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = grid_x + dx, grid_y + dy
                if 0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE:
                    weight = 1.0 if (dx == 0 and dy == 0) else 0.5
                    self.stop_heatmap[ny, nx] += weight

    def get_association_score(self, x, y):
        """Returns the association score for normalized coords x, y."""
        grid_x = int(np.clip(x * self.GRID_SIZE, 0, self.GRID_SIZE - 1))
        grid_y = int(np.clip(y * self.GRID_SIZE, 0, self.GRID_SIZE - 1))
        return self.stop_heatmap[grid_y, grid_x]

    def update(self, raw_state):
        """
        Updates the state machine with a new raw detection.
        Enforces valid transitions and temporal consistency.
        Reset to unknown if no update for > 2 seconds (Stale Data Protection).
        """
        now = time.time()
        
        # Stale check
        if raw_state == 'unknown':
             if now - self.last_state_change > 2.0:
                 self.state = 'unknown'
                 return self.state
        
        self.history.append(raw_state)
        if len(self.history) > self.HISTORY_SIZE:
            self.history.pop(0)

        # Get most frequent state in history (Voting)
        # Filter out 'unknown' if possible
        valid_states = [s for s in self.history if s != 'unknown']
        if not valid_states:
            return self.state
            
        dominant_state = max(set(valid_states), key=valid_states.count)
        
        # State Machine Logic
        if self.state != dominant_state and self.state == 'unknown':
             self.state = dominant_state
             self.last_state_change = time.time()
        elif self.state == 'green':
            if dominant_state == 'yellow' or dominant_state == 'red':
                 if valid_states.count(dominant_state) >= 3:
                     self.state = dominant_state
                     self.last_state_change = time.time()
        elif self.state == 'yellow':
            if dominant_state == 'red':
                if valid_states.count('red') >= 2:
                    self.state = 'red'
                    self.last_state_change = time.time()
            elif dominant_state == 'green':
                 if valid_states.count('green') >= 4:
                     self.state = 'green'
                     self.last_state_change = time.time()
        elif self.state == 'red':
            if dominant_state == 'green':
                 if valid_states.count('green') >= 3:
                     self.state = 'green'
                     self.last_state_change = time.time()
        
        return self.state

class TrafficLightLogic:
    def __init__(self):
        self.state_machines = {} # Map id -> TrafficLightStateMachine

    def get_state(self, tl_id, image_crop):
        if tl_id not in self.state_machines:
            self.state_machines[tl_id] = TrafficLightStateMachine(tl_id)
            
        raw_state = self.detect_raw_color(image_crop)
        final_state = self.state_machines[tl_id].update(raw_state)
        return final_state

    def record_vehicle_stop(self, tl_id, x, y, frame_w, frame_h):
        """Learns that a car stopped at (x,y) while this light was red."""
        if tl_id in self.state_machines:
            norm_x = x / frame_w
            norm_y = y / frame_h
            self.state_machines[tl_id].record_stop(norm_x, norm_y, frame_w, frame_h)

    def is_associated(self, tl_id, x, y, frame_w, frame_h):
        """Checks if a car at (x,y) is likely in a lane controlled by tl_id."""
        if tl_id not in self.state_machines:
            return False
            
        norm_x = x / frame_w
        norm_y = y / frame_h
        score = self.state_machines[tl_id].get_association_score(norm_x, norm_y)
        
        # Threshold: At least one strong stopping event (weight 1.0)
        return score >= 1.0

    def detect_raw_color(self, image_crop):
        """
        Detects color using HSV + Brightness weighting + Circularity Check.
        Focuses on the brightest parts of the image (the active light).
        """
        if image_crop is None or image_crop.size == 0:
            return 'unknown'

        # 1. CLAHE Normalization (Enhance contrast in varying light)
        lab = cv2.cvtColor(image_crop, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_crop = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        hsv = cv2.cvtColor(enhanced_crop, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        max_v = np.max(v)
        if max_v < 70: # Lowered from 100
            return 'unknown'
            
        _, bright_mask = cv2.threshold(v, max_v * 0.6, 255, cv2.THRESH_BINARY) # Lowered from 0.7
        
        # Color Ranges
        lower_red1, upper_red1 = np.array([0, 40]), np.array([10, 255]) # Lowered saturation
        lower_red2, upper_red2 = np.array([165, 40]), np.array([180, 255])
        lower_yellow, upper_yellow = np.array([12, 40]), np.array([38, 255])
        lower_green, upper_green = np.array([39, 40]), np.array([100, 255])

        hs_img = cv2.merge((h, s))
        
        masks = {
            'red': cv2.add(cv2.inRange(hs_img, lower_red1, upper_red1), 
                           cv2.inRange(hs_img, lower_red2, upper_red2)),
            'yellow': cv2.inRange(hs_img, lower_yellow, upper_yellow),
            'green': cv2.inRange(hs_img, lower_green, upper_green)
        }

        counts = {'red': 0, 'yellow': 0, 'green': 0}
        
        # 2. Circularity Check (Filter glare/reflections)
        for color, mask in masks.items():
            # Only consider bright pixels of this color
            combined_mask = cv2.bitwise_and(mask, bright_mask)
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < 3: continue # Lowered from 5
                
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0: continue
                
                # Circularity = 4 * pi * Area / Perimeter^2
                circularity = (4 * np.pi * area) / (perimeter * perimeter)
                
                # Reflections/Glare are usually elongated
                # Traffic lights are circular
                if circularity > 0.35: # Lowered from 0.6 to be very lenient
                    counts[color] += area
        
        total_bright_pixels = sum(counts.values())
        if total_bright_pixels == 0:
            # Fallback: if no circular blobs found, try just checking raw mask density
            # but only if the crop is small (consistent with a traffic light)
            rw, rh = image_crop.shape[:2]
            if rw < 100 and rh < 100: # Typical traffic light crop
                # Find best color purely by count
                for color, mask in masks.items():
                    counts[color] = cv2.countNonZero(cv2.bitwise_and(mask, bright_mask))
                
                best_color = max(counts, key=counts.get)
                if counts[best_color] > 4: # Min evidence
                    return best_color
            return 'unknown'

        # Find best color
        best_color = max(counts, key=counts.get)
        
        # Threshold: At least 20% of the bright area must be the specific color
        if counts[best_color] > 5: # Min pixel count
            return best_color
            
        return 'unknown'
