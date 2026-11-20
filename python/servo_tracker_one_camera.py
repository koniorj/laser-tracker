import serial 
import time 
import cv2
import numpy as np
import csv
import os

calib_path = os.path.join(os.path.dirname(__file__), "calib.csv")
CAMERA_1_ID = 1 
KEY_ESC = 27
KEY_SPACE = 32

class ServoTracker():
    def __init__(self, calibration_points, serial_port="COM3", baudrate=115200, wait_time=0.5):
        self.horizontal = 126.0
        self.vertical = 124.0
        self.wait_time = wait_time
        self.last_move_time = 0.0

        self.last_sent = None
        self.tracker = None

        self.coef_h, self.coef_v = self._fit_calibration(calibration_points)
    
        if serial_port:
            try:
                self.tracker = serial.Serial(serial_port, baudrate, timeout=1)
                time.sleep(2) # let's give arduino some time to reset
            except Exception as e:
                print(f"Connection with port unsuccessful ({e})")

    def _features(self, x, y):
        """Vector of features for 2nd degree polynomial [1, x, y, x^2, x*y, y^2]"""
        return np.array([1.0, x, y, x * x, x * y, y * y], dtype=np.float64)

    def _fit_calibration(self, calib_file):
        """
        Loads calibration points from a CSV file and fits a 2nd-degree 2D polynomial
        regression model using Ordinary Least Squares (OLS) to map pixel coordinates
        (x, y) to servo angles (h, v).

        Returns:
            tuple[np.ndarray, np.ndarray]: Learned polynomial coefficients (coef_h, coef_v).
        """
        hs, vs, xs, ys = [], [], [], []
        with open(calib_file, "r", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("Calibration file is empty!")
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            required = {"h", "v", "x", "y"}
            if not required.issubset(set(reader.fieldnames)):
                raise ValueError("Missing required columns (h,v,x,y)!")
            for row in reader:
                hs.append(float(row["h"]))
                vs.append(float(row["v"]))
                xs.append(float(row["x"]))
                ys.append(float(row["y"]))

        if len(hs) < 6:
            raise ValueError("Not enough calibration points. We need at least 6.")

        xs = np.array(xs)
        ys = np.array(ys)
        hs = np.array(hs)
        vs = np.array(vs)

        A = np.column_stack([np.ones_like(xs), xs, ys, xs**2, xs * ys, ys**2])

        # solve for optimal polynomial weights with Ordinary Least Squares (OLS)
        coef_h, _, _, _ = np.linalg.lstsq(A, hs, rcond=None)
        coef_v, _, _, _ = np.linalg.lstsq(A, vs, rcond=None)

        # compute Mean Absolute Error (MAE) on calibration points
        err_h = np.mean(np.abs(A @ coef_h - hs))
        err_v = np.mean(np.abs(A @ coef_v - vs))
        print(f"Calibration successful ({len(hs)}) | Avg err: H={err_h:.2f} deg, V={err_v:.2f} deg")

        return coef_h, coef_v

    def pixel_to_angles(self, camera_x, camera_y):
        feat = self._features(camera_x, camera_y)
        h = float(np.clip(np.dot(feat, self.coef_h), 90.0, 180.0))
        v = float(np.clip(np.dot(feat, self.coef_v), 90.0, 180.0))
        return h, v

    def update(self, camera_x, camera_y):
        if camera_x is None or camera_y is None:
            return self.horizontal, self.vertical

        now = time.time()
        if now - self.last_move_time < self.wait_time:
            return self.horizontal, self.vertical

        self.horizontal, self.vertical = self.pixel_to_angles(camera_x, camera_y)
        if self._send_to_hardware():
            self.last_move_time = now
        return self.horizontal, self.vertical

    def _format_command(self, h, v):
        h = int(np.clip(round(h), 90, 180))
        v = int(np.clip(round(v), 90, 180))
        return f"H{h}V{v}\n"

    def _send_to_hardware(self):
        if self.tracker is None or not self.tracker.is_open:
            return False

        h = round(self.horizontal)
        v = round(self.vertical)
        if (h, v) == self.last_sent:
            return False
        command = self._format_command(self.horizontal, self.vertical)
        self.tracker.write(command.encode('utf-8'))
        self.last_sent = (h, v)
        return True


def get_mask(frame1, frame2, kernel):
    frame_difference = cv2.absdiff(frame1, frame2)
    frame_difference = cv2.GaussianBlur(frame_difference, (5, 5), 0)

    _, mask = cv2.threshold(frame_difference, 25, 255, cv2.THRESH_BINARY)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # MORPH_ERODE, MORPH_DILATE

    return mask

def get_center_of_motion(mask, display_frame, min_area=500, max_area = 75000):
    # mask, type of detection (ignore insides of objects), method of compression
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_contour = None
    best_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)

        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            ratio = float(w/h)

            # additional filter:
            if 0.1 < ratio < 5.0:
                if area > best_area:
                    best_area = area
                    best_contour = contour

    if best_contour is not None:
        x, y, w, h = cv2.boundingRect(best_contour)
        center_x = int(x + w / 2)
        center_y = int(y + h / 2)

        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(display_frame, (center_x, center_y), 5, (0, 0, 255), -1)

        return center_x, center_y

    return None, None


def main():
    tracker = ServoTracker(calibration_points=calib_path, serial_port='COM3', wait_time=0.5)

    # CAP_DSHOW - DirectShow, it overwrites the standard way of Windows opening
    # camera feed with MSMF, which is incompatible with Iriun
    left_capture = cv2.VideoCapture(CAMERA_1_ID, cv2.CAP_DSHOW)
    left_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    left_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    is_paused = False
    _, prev_frame = left_capture.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((9,9), np.uint8)

    try:
        while True:
            ret, curr_frame = left_capture.read()
            if not ret:
                continue
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
     
            if time.time() - tracker.last_move_time >= 0.40:
                mask = get_mask(prev_gray, curr_gray, kernel)
                x, y = get_center_of_motion(mask, curr_frame)
                tracker.update(x, y)

            prev_gray = curr_gray
            cv2.imshow("Current detection", curr_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == KEY_ESC:
                break
            elif key == KEY_SPACE:
                is_paused = True

            if is_paused:
                cv2.putText(curr_frame, "PAUSED - PRESS SPACE TO CONTINUE", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.imshow("Current detection", curr_frame)

                while is_paused:
                    key_pause = cv2.waitKey(30) & 0xFF
                    if key_pause == KEY_SPACE:
                        is_paused = False
                    elif key_pause == KEY_ESC:
                        return

                left_capture.read()
                _, prev_frame = left_capture.read()
                prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
    finally: 
        left_capture.release()
        cv2.destroyAllWindows()
        if tracker.tracker is not None and tracker.tracker.is_open:
            tracker.tracker.close()
        print("All resources freed.")

if __name__ == "__main__":
    main()