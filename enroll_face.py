import cv2
import time
from face_security import FaceSecurity


security = FaceSecurity()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    raise SystemExit


print()
print("========================================")
print("       SPIDEY FACE ENROLLMENT")
print("========================================")
print()
print("Look at the camera.")
print("Keep only your face visible.")
print("Press Q to cancel.")
print()


# Give webcam time to stabilize
for _ in range(15):
    cap.read()
    time.sleep(0.05)


embeddings = []
last_capture = 0

while len(embeddings) < 8:

    success, frame = cap.read()

    if not success:
        continue

    frame = cv2.flip(frame, 1)

    faces = security._detect(frame)

    # Draw detected faces
    if faces is not None and len(faces) > 0:
        for face in faces:
            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

        status = f"FACE DETECTED  |  SAMPLE {len(embeddings)}/8"

        # Capture only every 0.8 seconds
        if time.time() - last_capture >= 0.8:

            feature = security.enroll(frame)

            if feature is not None:

                embeddings.append(feature)
                last_capture = time.time()

                print(
                    f"Face sample {len(embeddings)}/8 captured."
                )

    else:

        status = "NO FACE DETECTED"

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0) if faces is not None and len(faces) > 0 else (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        "Press Q to cancel",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SPIDEY Face Enrollment",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        print("Enrollment cancelled.")
        cap.release()
        cv2.destroyAllWindows()
        raise SystemExit


cap.release()
cv2.destroyAllWindows()


if len(embeddings) >= 8:

    security.save_profile(embeddings)

    print()
    print("========================================")
    print("FACE ENROLLMENT SUCCESSFUL")
    print("========================================")
    print()
    print("8 face samples saved.")
    print("Fist lock security is now enabled.")
    print()

else:

    print("Face enrollment failed.")


