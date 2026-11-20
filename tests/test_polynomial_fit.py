import csv
import pytest
from servo_tracker_one_camera import ServoTracker

@pytest.mark.parametrize("camera_x, camera_y, expected_h, expected_v", [
    (200.0, 200.0, 110.0, 120.0),
    (600.0, 400.0, 130.0, 130.0),
    (1000.0, 600.0, 150.0, 140.0),
])
def test_polynomial_fit(tmp_path, camera_x, camera_y, expected_h, expected_v):
    """Verifies that polynomial regression recovers a known 
    mapping and predicts angles within tolerance."""

    calib = tmp_path / "synth_calib.csv"
    with open(calib, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["h", "v", "x", "y"])
        for x in [100.0, 500.0, 900.0]:
            for y in [100.0, 400.0, 700.0]:
                writer.writerow([100.0 + 0.05 * x, 110.0 + 0.05 * y, x, y])

    tracker = ServoTracker(calibration_points=str(calib), serial_port=None)
    h, v = tracker.pixel_to_angles(camera_x, camera_y)

    assert h == pytest.approx(expected_h, abs=1e-3)
    assert v == pytest.approx(expected_v, abs=1e-3)