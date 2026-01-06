import numpy as np

class SpeedLogic:
    def __init__(self, perspective_manager, pixels_per_meter=20):
        """
        Initializes the speed logic module.

        Args:
            perspective_manager: An instance of PerspectiveManager for BEV transformations.
            pixels_per_meter: Calibration value. The number of pixels in the BEV that correspond to one meter.
                              This needs to be calibrated for a specific camera setup.
        """
        self.pm = perspective_manager
        self.pixels_per_meter = pixels_per_meter

    def calculate_speed_kph(self, car_id, vehicle_history, dt):
        """
        Calculates the speed of a single vehicle in km/h.

        Args:
            car_id: The ID of the car to calculate speed for.
            vehicle_history: A dictionary containing the history of vehicle positions.
                             Example: {car_id: {'last_pos': (x,y), 'prev_pos': (x,y), ...}}
            dt: Delta time since the last frame in seconds.

        Returns:
            The calculated speed in km/h, or None if speed cannot be calculated.
        """
        if dt == 0 or car_id not in vehicle_history:
            return None

        history = vehicle_history[car_id]
        # We need at least two points in history to calculate speed.
        # The detector should provide 'last_pos' and 'prev_pos'.
        if 'last_pos' not in history or 'prev_pos' not in history:
            return None

        # Get current and previous positions from the vehicle's history
        p1_img = history['prev_pos']
        p2_img = history['last_pos']

        # Map points to Bird's-Eye View
        p1_bev = self.pm.map_point_to_bev(p1_img[0], p1_img[1])
        p2_bev = self.pm.map_point_to_bev(p2_img[0], p2_img[1])

        if p1_bev is None or p2_bev is None:
            return None

        # Calculate distance in BEV (pixels)
        dist_pixels = np.sqrt((p2_bev[0] - p1_bev[0])**2 + (p2_bev[1] - p1_bev[1])**2)

        # Convert to meters
        dist_meters = dist_pixels / self.pixels_per_meter

        # Calculate speed in m/s
        speed_ms = dist_meters / dt

        # Convert to km/h
        speed_kph = speed_ms * 3.6

        return speed_kph

    def check_speeding_violations(self, cars, speed_limit_kph=40):
        """
        Checks for cars exceeding a given speed limit.

        Args:
            cars: A list of car objects. Each car object is a dictionary
                  that must contain a 'speed_kph' key.
            speed_limit_kph: The speed limit in km/h.

        Returns:
            A list of speeding violation events.
        """
        violations = []
        for car in cars:
            if 'speed_kph' in car and car['speed_kph'] is not None:
                if car['speed_kph'] > speed_limit_kph:
                    violations.append({
                        'type': 'speeding_violation',
                        'car_id': car['id'],
                        'speed': round(car['speed_kph'], 2),
                        'limit': speed_limit_kph,
                        'message': f"Vehicle {car['id']} exceeded speed limit. Speed: {car['speed_kph']:.2f} km/h.",
                        'vehicle_id': car['id'] # For UI compatibility
                    })
        return violations
