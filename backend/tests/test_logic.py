import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock TrafficLightLogic since its dependency (GMC) might not be available in test env
from unittest.mock import MagicMock
sys.modules['logic.traffic_light'] = MagicMock()

from logic.pedestrian import PedestrianLogic

@pytest.fixture
def pedestrian_logic():
    """Fixture to initialize PedestrianLogic."""
    return PedestrianLogic()

def test_no_violation_when_far_apart(pedestrian_logic):
    """
    Test that no violation is detected when cars and pedestrians are far from each other.
    """
    cars = [{'id': 1, 'box': [100, 100, 150, 150]}]
    pedestrians = [{'id': 101, 'box': [300, 300, 320, 350]}]
    
    violations = pedestrian_logic.check_yield_violations(cars, pedestrians)
    
    assert len(violations) == 0, "Should be no violations when objects are far apart"

def test_violation_when_car_too_close_to_pedestrian(pedestrian_logic):
    """
    Test that a violation is detected when a car is dangerously close to a pedestrian.
    A car's front (right edge, x2) is intersecting the pedestrian's safety bubble.
    """
    # Car is at x=100-150. Pedestrian is at x=160.
    # Car width = 50. Safety margin is 2 * width = 100.
    # Car's front (150) + margin (100) = 250.
    # Pedestrian's box starts at 160. 160 is inside [150, 250], so it's a violation.
    cars = [{'id': 2, 'box': [100, 100, 150, 150]}]
    pedestrians = [{'id': 102, 'box': [160, 100, 180, 150]}]
    
    violations = pedestrian_logic.check_yield_violations(cars, pedestrians)
    
    assert len(violations) == 1, "A violation should be detected when a car is too close"
    assert violations[0]['car_id'] == 2
    assert violations[0]['pedestrian_id'] == 102

def test_no_violation_when_car_is_behind_pedestrian(pedestrian_logic):
    """
    Test no violation when car is safely behind the pedestrian (moving in same direction).
    """
    # Car is at x=100-150. Pedestrian is way ahead at x=300.
    cars = [{'id': 3, 'box': [100, 100, 150, 150]}]
    pedestrians = [{'id': 103, 'box': [300, 100, 320, 150]}]

    violations = pedestrian_logic.check_yield_violations(cars, pedestrians)

    assert len(violations) == 0, "No violation if car is far behind the pedestrian"

def test_no_objects(pedestrian_logic):
    """
    Test that the function handles empty lists of objects gracefully.
    """
    assert len(pedestrian_logic.check_yield_violations([], [])) == 0
    assert len(pedestrian_logic.check_yield_violations([{'id': 1, 'box': [0,0,1,1]}], [])) == 0
    assert len(pedestrian_logic.check_yield_violations([], [{'id': 101, 'box': [0,0,1,1]}])) == 0
