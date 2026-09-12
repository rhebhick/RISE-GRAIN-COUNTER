import cv2
import numpy as np

def _try_mediapipe_hand_points(rgb):
    """Optional visual reference points. Does not count rice grains."""
    try:
        import mediapipe as mp
        hands = mp.solutions.hands
        drawing = mp.solutions.drawing_utils

        with hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5
        ) as detector:
            result = detector.process(rgb)

        points = []
        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                for lm in hand.landmark:
                    points.append((lm.x, lm.y))
        return points
    except Exception:
        return []


def analyze_image(rgb_image):
    """
    Provides a simple visualization:
    - OpenCV attempts to find a circular plate/pot boundary.
    - MediaPipe Hands, if installed and a hand is visible, supplies reference landmarks.
    Neither method counts individual grains.
    """
    annotated = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(annotated, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=max(30, min(rgb_image.shape[:2]) // 4),
        param1=100,
        param2=35,
        minRadius=max(10, min(rgb_image.shape[:2]) // 10),
        maxRadius=max(20, min(rgb_image.shape[:2]) // 2)
    )

    selected = None
    if circles is not None:
        circles = np.round(circles[0]).astype(int)
        # Prefer the largest detected circle as a rough plate/pot boundary.
        selected = max(circles.tolist(), key=lambda c: c[2])
        x, y, r = selected
        cv2.circle(annotated, (x, y), r, (0, 255, 0), 3)
        cv2.circle(annotated, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(
            annotated, "Detected circular boundary",
            (max(5, x-r), max(20, y-r-10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2
        )

    hand_points = _try_mediapipe_hand_points(rgb_image)
    for nx, ny in hand_points:
        px = int(nx * rgb_image.shape[1])
        py = int(ny * rgb_image.shape[0])
        cv2.circle(annotated, (px, py), 3, (255, 0, 255), -1)

    if selected is not None and hand_points:
        message = "OpenCV found a rough circular boundary and MediaPipe found hand reference landmarks. Manual measurements remain authoritative."
    elif selected is not None:
        message = "OpenCV found a rough circular boundary. MediaPipe did not find a hand reference, or MediaPipe is unavailable."
    elif hand_points:
        message = "MediaPipe found hand reference landmarks, but no reliable circular boundary was found."
    else:
        message = "No reliable automatic reference was found. Enter the physical measurements manually."

    return {
        "annotated": cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
        "plate_circle": selected,
        "hand_points": hand_points,
        "message": message,
    }
