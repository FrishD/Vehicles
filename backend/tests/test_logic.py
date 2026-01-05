import numpy as np
import pytest
import cv2

# Add backend to path to enable local imports
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from logic.traffic_light import TrafficLightLogic
from logic.pedestrian import PedestrianLogic
from logic.infrastructure import InfrastructureLogic

def xtest_tl_logic():
    print("Testing Traffic Light Logic...")
    logic = TrafficLightLogic()
    # Mock some data
    logic.record_vehicle_stop(1, 400, 500, 1920, 1080)
    
    # Assert that the association is made
    is_assoc = logic.is_associated(1, 410, 510, 1920, 1080)
    assert is_assoc == True, "Failed to associate stop with TL"
    
    is_assoc_far = logic.is_associated(1, 800, 800, 1920, 1080)
    assert is_assoc_far == False, "Associated too far from TL"

def test_pedestrian_logic():
    print("Testing Pedestrian Logic...")
    logic = PedestrianLogic()

    # Mock a crosswalk polygon
    crosswalk_poly = np.array([[200, 200], [400, 200], [400, 300], [200, 300]], dtype=np.int32)

    # Test case 1: Car is moving near a crosswalk with a pedestrian in it (Violation)
    cars = [{'id': 1, 'box': [100, 240, 180, 280], 'velocity': 20}]
    peds = [{'id': 10, 'box': [250, 240, 270, 280]}]
    violations = logic.check_yield_violations(cars, peds, [crosswalk_poly])
    assert len(violations) > 0, "Failed to detect yield violation"

    # Test case 2: Car is stopped near a crosswalk with a pedestrian in it (No Violation)
    cars = [{'id': 2, 'box': [100, 240, 180, 280], 'velocity': 5}]
    violations = logic.check_yield_violations(cars, peds, [crosswalk_poly])
    assert len(violations) == 0, "Incorrectly flagged a stopped car as a violation"

    # Test case 3: Car is moving, but no pedestrian in the crosswalk (No Violation)
    cars = [{'id': 3, 'box': [100, 240, 180, 280], 'velocity': 20}]
    peds_outside = [{'id': 11, 'box': [500, 500, 520, 540]}]
    violations = logic.check_yield_violations(cars, peds_outside, [crosswalk_poly])
    assert len(violations) == 0, "Incorrectly flagged a violation when no pedestrian was in the crosswalk"

if __name__ == '__main__':
    pytest.main()
