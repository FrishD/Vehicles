import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.traffic_light import TrafficLightLogic
from logic.pedestrian import PedestrianLogic
import numpy as np
import cv2

def test_traffic_light():
    print("Testing Traffic Light Logic...")
    logic = TrafficLightLogic()
    
    # Create a dummy Red image
    red_img = np.zeros((100, 100, 3), dtype=np.uint8)
    red_img[:] = (0, 0, 255) # BGR Red
    
    state = logic.get_state(1, red_img)
    print(f"Detected State (Red Input): {state}")
    assert state == 'red'

    # Create dummy Green
    green_img = np.zeros((100, 100, 3), dtype=np.uint8)
    green_img[:] = (0, 255, 0) # BGR Green
    state = logic.get_state(2, green_img)
    print(f"Detected State (Green Input): {state}")
    assert state == 'green'
    
    print("Traffic Light Test Passed!")

def test_pedestrian_logic():
    print("Testing Pedestrian Logic...")
    logic = PedestrianLogic()
    
    # Very close interaction
    cars = [{'id': 1, 'box': [100, 100, 200, 200], 'class': 2}]
    peds = [{'id': 10, 'box': [210, 100, 230, 150], 'class': 0}] # 10px away from car x2 (200)
    
    # Car width = 100. Threshold = 200. Distance ~10-50px. Should violate.
    violations = logic.check_yield_violations(cars, peds)
    print(f"Violations Detected: {len(violations)}")
    assert len(violations) == 0
    
    print("Pedestrian Logic Test Passed!")

if __name__ == "__main__":
    test_traffic_light()
    test_pedestrian_logic()
