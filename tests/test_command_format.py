import pytest
import os
from servo_tracker_one_camera import ServoTracker

calib_path = os.path.join(os.path.dirname(__file__), "test_calib.csv")

@pytest.mark.parametrize("h, v, expected", [
    (120.4444, 30.11, "H120V90\n"),
    (126.0, 124.0, "H126V124\n"),
    (125.6, 139.4, "H126V139\n"),
    (90.0, 180.0, "H90V180\n"),
    (89.0, 89.0, "H90V90\n")
])
def test_command_format(h, v, expected):
    """Checks if float parameters are rounded, converted to the correct range - [90, 180] 
    and formatted as H(deg)V(deg).
    """
    tracker = ServoTracker(calibration_points=calib_path, serial_port=None)
    command = tracker._format_command(h, v)
    assert command == expected
