import cv2
import numpy as np
import os


class FaceSecurity:

    def __init__(self):

        base = os.path.dirname(os.path.abspath(__file__))
        models = os.path.join(base, "models")

        detector_model = os.path.join(
            models,
            "face_detection_yunet_2023mar.onnx"
        )

        recognizer_model = os.path.join(
            models,
            "face_recognition_sface_2021dec.onnx"
        )

        self.profile_file = os.path.join(
            models,
            "spidey_face_profile.npy"
        )

        if not os.path.exists(detector_model):
            raise FileNotFoundError(
                "YuNet face detection model missing."
            )

        if not os.path.exists(recognizer_model):
            raise FileNotFoundError(
                "SFace face recognition model missing."
            )

        self.detector = cv2.FaceDetectorYN.create(
            detector_model,
            "",
            (320, 240),
            0.85,
            0.3,
            5000
        )

        self.recognizer = cv2.FaceRecognizerSF.create(
            recognizer_model,
            ""
        )

        self.profile = None

        if os.path.exists(self.profile_file):
            try:
                self.profile = np.load(
                    self.profile_file
                )
            except Exception:
                self.profile = None


    def _detect(self, frame):

        h, w = frame.shape[:2]

        self.detector.setInputSize(
            (w, h)
        )

        _, faces = self.detector.detect(
            frame
        )

        if faces is None:
            return []

        return faces


    def _embedding(self, frame, face):

        aligned = self.recognizer.alignCrop(
            frame,
            face
        )

        feature = self.recognizer.feature(
            aligned
        )

        return feature


    def save_profile(self, embeddings):

        profile = np.mean(
            np.vstack(embeddings),
            axis=0
        ).astype(np.float32)

        norm = np.linalg.norm(profile)

        if norm > 0:
            profile /= norm

        np.save(
            self.profile_file,
            profile
        )

        self.profile = profile


    def is_authorized(self, frame):

        if self.profile is None:
            return False

        faces = self._detect(frame)

        if faces is None or len(faces) == 0:
            return False

        # Use the largest detected face
        face = max(
            faces,
            key=lambda f: f[2] * f[3]
        )

        try:

            feature = self._embedding(
                frame,
                face
            )

            score = self.recognizer.match(
                self.profile,
                feature,
                cv2.FaceRecognizerSF_FR_COSINE
            )

            return score >= 0.40

        except Exception:
            return False


    def enroll(self, frame):

        faces = self._detect(frame)

        if faces is None or len(faces) == 0:
            return None

        face = max(
            faces,
            key=lambda f: f[2] * f[3]
        )

        try:
            return self._embedding(
                frame,
                face
            )
        except Exception:
            return None

