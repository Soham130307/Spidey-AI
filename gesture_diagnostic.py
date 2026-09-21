import os
import math
import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "hand_landmarker.task"
)

def angle(a, b, c):

    ba = (
        a.x - b.x,
        a.y - b.y
    )

    bc = (
        c.x - b.x,
        c.y - b.y
    )

    dot = (
        ba[0] * bc[0]
        +
        ba[1] * bc[1]
    )

    mag_ba = math.sqrt(
        ba[0] ** 2 +
        ba[1] ** 2
    )

    mag_bc = math.sqrt(
        bc[0] ** 2 +
        bc[1] ** 2
    )

    if mag_ba == 0 or mag_bc == 0:
        return 0

    cosine = dot / (mag_ba * mag_bc)

    cosine = max(
        -1.0,
        min(1.0, cosine)
    )

    return math.degrees(
        math.acos(cosine)
    )

print()
print("============================================")
print("       SPIDEY FIST DIAGNOSTIC")
print("============================================")
print()
print("Make a NORMAL CLOSED FIST in front of camera.")
print("Hold it for 3 seconds.")
print("Press Q to quit.")
print()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("[ERROR] Could not open webcam.")
    raise SystemExit

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.55,
    min_hand_presence_confidence=0.55,
    min_tracking_confidence=0.55
)

timestamp_ms = 0

with vision.HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = cap.read()

        if not success:
            continue

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp_ms += 33

        results = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        if results.hand_landmarks:

            hand = results.hand_landmarks[0]

            index_angle = angle(
                hand[5],
                hand[6],
                hand[8]
            )

            middle_angle = angle(
                hand[9],
                hand[10],
                hand[12]
            )

            ring_angle = angle(
                hand[13],
                hand[14],
                hand[16]
            )

            pinky_angle = angle(
                hand[17],
                hand[18],
                hand[20]
            )

            # Original angle-based fist test
            angle_fist = (
                index_angle < 145
                and middle_angle < 145
                and ring_angle < 145
                and pinky_angle < 145
            )

            # Fingertip vs PIP test
            index_curled = hand[8].y > hand[6].y
            middle_curled = hand[12].y > hand[10].y
            ring_curled = hand[16].y > hand[14].y
            pinky_curled = hand[20].y > hand[18].y

            position_fist = (
                index_curled
                and middle_curled
                and ring_curled
                and pinky_curled
            )

            print(
                f"I={index_angle:6.1f}  "
                f"M={middle_angle:6.1f}  "
                f"R={ring_angle:6.1f}  "
                f"P={pinky_angle:6.1f}  "
                f"| ANGLE_FIST={angle_fist}  "
                f"| POSITION_FIST={position_fist}"
            )

        else:

            print("NO HAND DETECTED")

        cv2.imshow(
            "SPIDEY Fist Diagnostic",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()

print()
print("Diagnostic finished.")
