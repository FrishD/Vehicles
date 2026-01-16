import numpy as np
import cv2

class PedestrianLogic:
    def __init__(self):
        # Using a simple dictionary to track cars near crosswalks
        self.cars_near_crosswalk = {}

    def check_yield_violations(self, cars, pedestrians, crosswalks):
        """
        Checks for vehicles that fail to yield to pedestrians inside a crosswalk.
        
        cars: List of detected car objects.
        pedestrians: List of detected pedestrian objects.
        crosswalks: List of detected crosswalk polygons.

        Returns: A list of violation events.
        """
        if not crosswalks or not pedestrians:
            return []

        violations = []
        crosswalk_poly = crosswalks[0] # Assuming one primary crosswalk for now

        # 1. Find all pedestrians inside the crosswalk
        peds_in_crosswalk = []
        for ped in pedestrians:
            ped_center = self._get_center(ped['box'])
            # Use Point Polygon Test to check if the pedestrian's center is inside the crosswalk
            if cv2.pointPolygonTest(crosswalk_poly, ped_center, False) >= 0:
                peds_in_crosswalk.append(ped)

        if not peds_in_crosswalk:
            return []

        # 2. Check for cars that are dangerously close to the crosswalk and moving
        for car in cars:
            car_id = car.get('id', -1)
            if car_id == -1: continue

            car_box = car['box']
            # Using the bottom center of the car's bounding box as its position
            car_pos = ((car_box[0] + car_box[2]) / 2, car_box[3])
            
            # Check if the car is within a certain distance of the crosswalk polygon
            dist_to_crosswalk = cv2.pointPolygonTest(crosswalk_poly, car_pos, True)
            
            # We are interested in cars *outside* but *near* the crosswalk
            # A negative distance means the point is outside the polygon.
            # The absolute value of the distance is the distance to the nearest edge.
            is_near_crosswalk = -100 < dist_to_crosswalk < 50 # Tunable proximity thresholds in pixels

            # To be considered "yielding", a car must be moving very slowly (close to a stop).
            # We define "not yielding" as moving with a velocity greater than a small threshold.
            is_not_yielding = car.get('velocity', 0) > 5.0 # Velocity in pixels/sec from detector.py

            if is_near_crosswalk and is_not_yielding:
                # If a car is moving near a crosswalk that has pedestrians in it, it's a potential violation.
                violations.append({
                    'type': 'yield_violation',
                    'car_id': car_id,
                    'message': f"Vehicle {car_id} failed to yield to pedestrian at crosswalk.",
                    'vehicle_id': car_id # For UI compatibility
                })

        return violations

    def _get_center(self, box):
        """Calculates the center of a bounding box."""
        x1, y1, x2, y2 = box
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))
