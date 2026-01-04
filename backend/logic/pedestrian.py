import numpy as np
import time

class PedestrianLogic:
    def __init__(self):
        self.car_history = {} # {id: {'pos': (cx, cy), 'time': timestamp}}
        self.MIN_SPEED_THRESHOLD = 2.0 # Pixels per frame (approx, depends on FPS)

    def check_yield_violations(self, cars, pedestrians):
        """
        Checks for yield violations.
        cars: list of dicts {'id': int, 'box': [x1, y1, x2, y2], 'class': 'car'}
        pedestrians: list of dicts {'id': int, 'box': [x1, y1, x2, y2], 'class': 'person'}
        
        Returns: list of violation events.
        """
        violations = []
        current_time = time.time()
        
        # Update History & Calculate Speed
        car_speeds = {}
        for car in cars:
            cid = car['id']
            box = car['box']
            center = self.get_center(box)
            
            if cid in self.car_history:
                last_pos = self.car_history[cid]['pos']
                last_time = self.car_history[cid]['time']
                dt = current_time - last_time
                if dt > 0:
                    dist_moved = np.linalg.norm(np.array(center) - np.array(last_pos))
                    speed = dist_moved # pixels per frame roughly if assume constant fps, or dist/dt
                    # Let's use simple frame-to-frame distance for robustness against jitter
                    car_speeds[cid] = dist_moved
            else:
                car_speeds[cid] = 100.0 # Assume moving if new (or 0? Safer to assume moving to detect entry)
                # Actually, if new, we can't judge speed yet. Assume 0 to be safe? 
                # Better: Wait for next frame.
                car_speeds[cid] = 0.0
            
            self.car_history[cid] = {'pos': center, 'time': current_time}

        # Cleanup old history
        # (Optional: remove IDs not seen in X seconds)

        for ped in pedestrians:
            ped_box = ped['box']
            ped_center = self.get_center(ped_box)
            
            for car in cars:
                car_box = car['box']
                car_center = self.get_center(car_box)
                
                # Calculate distance
                distance = np.linalg.norm(np.array(ped_center) - np.array(car_center))
                
                # Threshold for "Dangerous Proximity"
                car_width = car_box[2] - car_box[0]
                threshold = car_width * 2.5 # Increased slightly for safety buffer
                
                if distance < threshold:
                    # CHECK 1: Is car moving?
                    # If car is stopped (Speed < Threshold), it is YIELDING. Not a violation.
                    speed = car_speeds.get(car['id'], 0)
                    
                    if speed < self.MIN_SPEED_THRESHOLD:
                        # Car is stopped/slow near pedestrian -> Good behavior.
                        continue

                    # CHECK 2: Is car moving TOWARDS pedestrian? (Vector math - Future)
                    # For now, speed + proximity is enough.
                    
                    violations.append({
                        'type': 'yield_violation',
                        'car_id': car.get('id'),
                        'ped_id': ped.get('id'),
                        'distance': float(distance),
                        'message': f"Car {car.get('id')} failed to yield"
                    })
                    
        return violations

    def get_center(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
