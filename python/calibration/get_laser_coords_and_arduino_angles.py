import cv2
import serial
import time
import csv
import os

CAMERA_1_ID = 1
KEY_ESC = 27
KEY_SPACE = 32
WINDOW = "Laser spot"

PORT = "COM3"
BAUD = 115200
FILE = "calib.csv"

def find_laser_spot(frame, threshold=240, min_area=3):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    if not contours:
        return None, None
    best = max(contours, key=cv2.contourArea)
    m = cv2.moments(best)
    if m["m00"] == 0:
        return None, None
    return m["m10"] / m["m00"], m["m01"] / m["m00"]

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"click: x={x}, y={y}")

def main():
    ser = None
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.05)
        time.sleep(2)
        ser.write(b"x0\n")
    except Exception as e:
        print(f"WARNING: Did not connect to port {PORT} ({e}).")

    capture = cv2.VideoCapture(CAMERA_1_ID, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WINDOW, on_mouse)

    is_new = not os.path.exists(FILE)
    out = open(FILE, "a", newline="")
    writer = csv.writer(out)
    if is_new:
        writer.writerow(["h", "v", "x", "y"])

    angles = None
    step = 2

    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                continue

            if ser is not None and ser.in_waiting:
                line = ser.readline().decode(errors="ignore").strip()
                parts = line.split(",")
                if len(parts) == 2:
                    try:
                        angles = (int(parts[0]), int(parts[1]))
                    except ValueError:
                        pass

            lx, ly = find_laser_spot(frame)
            if lx is not None:
                cv2.circle(frame, (int(round(lx)), int(round(ly))), 8, (0, 255, 0), 2)
                cv2.putText(frame, f"spot: {lx:.1f}, {ly:.1f}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f"angles: {angles} | step: {step}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow(WINDOW, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == KEY_ESC:
                break
            elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                step = int(chr(key))
            elif key in [ord('w'), ord('a'), ord('s'), ord('d')] and ser is not None:
                ser.write(f"{chr(key)}{step}\n".encode())
            elif key == ord('l') and ser is not None:
                ser.write(b"l0\n")
            elif key == KEY_SPACE:
                if angles is not None and lx is not None:
                    writer.writerow([angles[0], angles[1], round(lx, 2), round(ly, 2)])
                    out.flush()
                    print(f"SAVED: H={angles[0]}, V={angles[1]}, X={lx:.1f}, Y={ly:.1f}")
                else:
                    print(f"Did not save! angles={angles}, spot=({lx}, {ly})")
    finally:
        out.close()
        if ser is not None:
            ser.close()
        capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()