import numpy as np
import time

class PedestrianLogic:
    def __init__(self):
        self.car_history = {} # {id: {'pos': (cx, cy), 'time': timestamp, 'first_seen': timestamp}}
        self.MIN_SPEED_THRESHOLD = 2.0 # Pixels per frame
        self.NEW_OBJECT_GRACE_PERIOD = 0.2 # Seconds before a new car's speed is considered reliable

    def check_yield_violations(self, cars, pedestrians):
        violations = []
        current_time = time.time()
        
        car_speeds = {}
        for car in cars:
            cid = car['id']
            box = car['box']
            center = self.get_center(box)
            
            if cid not in self.car_history:
                # First time seeing this car
                self.car_history[cid] = {'pos': center, 'time': current_time, 'first_seen': current_time}
                car_speeds[cid] = 0.0 # Speed is unknown on first frame
            else:
                # Car seen before, calculate speed
                last_pos = self.car_history[cid]['pos']
                last_time = self.car_history[cid]['time']
                dt = current_time - last_time

                if dt > 0.01: # Avoid division by zero
                    dist_moved = np.linalg.norm(np.array(center) - np.array(last_pos))
                    # Speed in pixels per second
                    speed = dist_moved / dt
                    car_speeds[cid] = speed
                else:
                    car_speeds[cid] = 0.0 # Not enough time passed to measure

                # Update history
                self.car_history[cid]['pos'] = center
                self.car_history[cid]['time'] = current_time

        for ped in pedestrians:
            ped_box = ped['box']
            
            for car in cars:
                car_box = car['box']
                
                # Use simple box proximity instead of center distance
                car_x1, car_y1, car_x2, car_y2 = car_box
                ped_x1, ped_y1, ped_x2, ped_y2 = ped_box
                
                # Safety bubble based on car width
                car_width = car_x2 - car_x1
                safety_margin = car_width * 2.0 # A bubble of 2x car width

                # Check if car's safety bubble horizontally overlaps with pedestrian
                is_close = (car_x2 + safety_margin > ped_x1) and (car_x1 - safety_margin < ped_x2)
                
                if is_close:
                    car_id = car['id']
                    speed = car_speeds.get(car_id, 0)
                    time_since_first_seen = current_time - self.car_history[car_id]['first_seen']

                    # Violation condition:
                    # 1. The car is moving (speed > threshold)
                    # OR
                    # 2. The car is new but appeared already inside the bubble (a static "bad parking" or sudden appearance)
                    
                    is_moving_violation = speed > self.MIN_SPEED_THRESHOLD
                    is_static_violation = time_since_first_seen < self.NEW_OBJECT_GRACE_PERIOD

                    if is_moving_violation or is_static_violation:
                        violations.append({
                            'type': 'yield_violation',
                            'car_id': car_id,
                            'pedestrian_id': ped.get('id'),
                            'message': f"Car {car_id} failed to yield to pedestrian {ped.get('id')}"
                        })

        return violations

    def get_center(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
