import pytest
import os
from servo_tracker_one_camera import ServoTracker

calib_path = os.path.join(os.path.dirname(__file__), "test_calib.csv")

@pytest.mark.parametrize("camera_x, camera_y", [
    (-10, -10),
    (2000, 2000),
    (100, 100),
    (0, -1000),
    (0, 0),
    (5000, -5000),
    (10, 10)
])
def test_servo_limits(camera_x, camera_y):
    """
    Verifies that pixel-to-angle conversion ensures that angles fall within safe
    hardware range [90.0, 180.0] deg even for extreme or out-of-frame pixel
    coordinates.
    """
    tracker = ServoTracker(calibration_points=calib_path, serial_port=None)
    h, v = tracker.pixel_to_angles(camera_x, camera_y)
    assert 90.0 <= h <= 180.0
    assert 90.0 <= v <= 180.0