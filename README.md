# Laser-Tracker

Main idea: we point a laser to an object moving within the range of our cameras, with focus on minimizing latency and maximizing precision.

We will be using Python for core computational tasks, such as computer vision, coordinate calculation and communication with Arduino.
Arduino will be used for physical control of the laser gimbal (the code will be written in C++).

---

#### Architecture

Hardware:

- two smartphone cameras (configured as high-FPS USB/IP webcams with Iriun)
- Arduino Uno
- actuators: two MG90S metal-gear micro servos mounted on a Pan-Tilt bracket
- low-power 5V laser diode

Software:

- Python: OpenCV (video feeds, real-time object detenction), NumPy (mathematical operations), PySerial (communication with microcontroller)
- C++: receives pre-calculated target angles from Python, directs the hardware with minimal latency

---

#### Initial solution - one camera & frame differencing

Our preliminary version is realized by using one camera, which is set in a fixed place in reference to the servomechanisms.
To map 2D image pixel coordinates $(x, y)$ directly to target servo angles $(H, V)$, we used **2D Polynomial Regression (2nd degree)** fitted via Ordinary Least Squares (OLS):

$$H(x, y) = w_0 + w_1 x + w_2 y + w_3 x^2 + w_4 xy + w_5 y^2$$
$$V(x, y) = v_0 + v_1 x + v_2 y + v_3 x^2 + v_4 xy + v_5 y^2$$

To be more precise:

- we first collected ground-truth pairs of pixel coordinates $(x, y)$ and known servo angles $(H, V)$ across the camera's field of view using the `get_laser_coords_and_arduino_angles` script (created with the help of Claude) and saved them into `calib.csv`,
- we then fitted the polynomial model at startup in `ServoTracker._fit_calibration()` by constructing a feature matrix $[1, x, y, x^2, xy, y^2]$ and solving for the optimal weight vectors $\mathbf{w}$ and $\mathbf{v}$ via `numpy.linalg.lstsq`,
- during real-time tracking (`servo_tracker.py`), moving objects are detected via frame differencing (`cv2.absdiff`), morphological filtering, and contour area/ratio filtering; to avoid self-tracking after the laser moves, the background reference frame (`prev_gray`) is refreshed once the servos settle,
- finally, the target's center coordinates $(x, y)$ are converted into servo angles $(H, V)$ via dot product (`pixel_to_angles`) and sent over serial communication (`H<angle>V<angle>`) to the Arduino controller at fixed time intervals (`wait_time`).

---

#### Target solution - two cameras & MOG2 background subtraction

In progress.
