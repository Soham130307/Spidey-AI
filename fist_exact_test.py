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

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("CAMERA FAILED")
    raise SystemExit

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.55,
    min_hand_presence_confidence=0.55,
    min_tracking_confidence=0.55
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

fist_frames = 0
REQUIRED_FRAMES = 12
timestamp_ms = 0

print()
print("======================================")
print("     SPIDEY EXACT FIST TEST")
print("======================================")
print()
print("Make a fist and HOLD it.")
print("The test will print when 12 frames are reached.")
print("Press Q to quit.")
print()

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

        middle_up = False
        fist_closed = False

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

            middle_up = (
                middle_angle > 155
                and index_angle < 150
                and ring_angle < 150
                and pinky_angle < 150
            )

            fist_closed = (
                index_angle < 145
                and middle_angle < 145
                and ring_angle < 145
                and pinky_angle < 145
            )

            if fist_closed and not middle_up:

                fist_frames += 1

            else:

                fist_frames = 0

            print(
                f"FIST={fist_closed} "
                f"MIDDLE={middle_up} "
                f"FRAMES={fist_frames}/12"
            )

            if fist_frames >= REQUIRED_FRAMES:

                print()
                print("======================================")
                print("  !!! FIST TRIGGER CONFIRMED !!!")
                print("======================================")
                print()

                break

        else:

            fist_frames = 0

        cv2.imshow(
            "SPIDEY Exact Fist Test",
            frame
        )

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
