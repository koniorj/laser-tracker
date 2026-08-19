import cv2
import numpy as np

CAMERA_1_ID = 0
CAMERA_2_ID = 1
KEY_ESC = 27

def get_mask(frame1, frame2, kernel):
    frame_difference = cv2.absdiff(frame1, frame2)
    frame_difference = cv2.medianBlur(frame_difference, 5) 

    # input image, brightness of detected motion, treshold calculation method, color inversion,
    # local window pixel size, fixed value used for sensitivity regulation
    mask = cv2.adaptiveThreshold(frame_difference, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 3)

    mask = cv2.medianBlur(mask, 5)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1) # MORPH_ERODE, MORPH_DILATE

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
    # CAP_DSHOW - DirectShow, it overwrites the standard way of Windows opening
    # camera feed with MSMF, which is incompatible with Iriun
    left_capture = cv2.VideoCapture(CAMERA_1_ID, cv2.CAP_DSHOW)
    right_capture = cv2.VideoCapture(CAMERA_2_ID, cv2.CAP_DSHOW)

    left_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    left_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    right_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    right_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    try:
        while True:
            _, left_frame_1 = left_capture.read()
            _, left_frame_2 = left_capture.read()
            _, right_frame_1 = right_capture.read()
            _, right_frame_2 = right_capture.read()

            left1 = cv2.cvtColor(left_frame_1, cv2.COLOR_BGR2GRAY)
            left2 = cv2.cvtColor(left_frame_2, cv2.COLOR_BGR2GRAY)
            right1 = cv2.cvtColor(right_frame_1, cv2.COLOR_BGR2GRAY)
            right2 = cv2.cvtColor(right_frame_2, cv2.COLOR_BGR2GRAY)

            kernel = np.ones((16, 16), np.uint8)

            mask_left = get_mask(left2, left1, kernel)
            mask_right = get_mask(right2, right1, kernel)

            left_x, left_y = get_center_of_motion(mask_left, left_frame_2)
            right_x, right_y = get_center_of_motion(mask_right, right_frame_2)

    
            cv2.imshow("Left detection", left_frame_2)
            cv2.imshow("Right detection", right_frame_2)

            # should be changed to yield or other method
            if left_x is not None or right_x is not None:
                print(f"L: ({left_x}, {left_y})") #  | R: ({right_x}, {right_y})
            
            if cv2.waitKey(1) & 0xFF == KEY_ESC:
                break
    finally: 
        left_capture.release()
        right_capture.release()
        cv2.destroyAllWindows()
        print("All resources freed.")


if __name__ == "__main__":
    main()