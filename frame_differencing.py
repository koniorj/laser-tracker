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

            kernel = np.array((16,16), dtype=np.uint8)

            mask_left = get_mask(left2, left1, kernel)
            mask_right = get_mask(right2, right1, kernel)
            

            if cv2.waitKey(1) & 0xFF == KEY_ESC:
                break
    finally: 
        left_capture.release()
        right_capture.release()
        cv2.destroyAllWindows()
        print("All resources freed.")


if __name__ == "__main__":
    main()