import pytest
import os
from servo_tracker_one_camera import ServoTracker

calib_path = os.path.join(os.path.dirname(__file__), "test_calib_wrong.csv")

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        ServoTracker(calibration_points="smth.csv", serial_port=None)

def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")

    with pytest.raises(Exception):
        ServoTracker(calibration_points=str(empty_file), serial_port=None)

def test_incorrect_csv_format():
    with pytest.raises(ValueError):
        ServoTracker(calibration_points=calib_path, serial_port=None)
