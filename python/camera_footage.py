import cv2
from my_exceptions import NoCameraFootage

CAMERA_1_ID = 1
CAMERA_2_ID = 2
KEY_ESC = 27

def main():
    # CAP_DSHOW - DirectShow, it overwrites the standard way of Windows opening
    # camera feed with MSMF, which is incompatible with Iriun
    left_capture = cv2.VideoCapture(CAMERA_1_ID, cv2.CAP_DSHOW)
    right_capture = cv2.VideoCapture(CAMERA_2_ID, cv2.CAP_DSHOW)

    try:
        while True:
            return_value_left, left_frame_1 = left_capture.read()
            return_value_right, right_frame_1 = right_capture.read()
            if not return_value_left:
                raise NoCameraFootage()
            if not return_value_right:
                raise NoCameraFootage()

            cv2.imshow("Live camera left", left_frame_1)
            cv2.imshow("Live camera right", right_frame_1)

            if cv2.waitKey(1) & 0xFF == KEY_ESC:
                break
    finally: 
        left_capture.release()
        cv2.destroyAllWindows()
        print("All resources freed.")


if __name__ == "__main__":
    main()