import cv2

CAMERA_1_ID = 1
KEY_ESC = 27
WINDOW = "Laser spot"

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
    capture = cv2.VideoCapture(CAMERA_1_ID, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WINDOW, on_mouse)

    printed_shape = False
    try:
        while True:
            ret, frame = capture.read()
            if not ret:
                continue

            if not printed_shape:
                print("frame.shape (h, w, c):", frame.shape)
                printed_shape = True

            lx, ly = find_laser_spot(frame)
            if lx is not None:
                cv2.circle(frame, (int(round(lx)), int(round(ly))), 8, (0, 255, 0), 2)
                cv2.putText(frame, f"{lx:.1f}, {ly:.1f}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow(WINDOW, frame)
            if cv2.waitKey(1) & 0xFF == KEY_ESC:
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()