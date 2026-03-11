# eye_use_reference.py  -- corrected global usage and small robustness fixes
import cv2, mediapipe as mp, pyautogui, time, numpy as np
from utils_actions import enqueue

# Use CAP_DSHOW on Windows for more reliable camera access
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.6)
screen_w, screen_h = pyautogui.size()
EMA_ALPHA = 0.18
_sm = [None]            # use a mutable container so we can modify without global keyword
BLINK_DEBOUNCE = 0.6
last_blink = 0

def eye_ratio(landmarks, top_idx, bottom_idx, left_idx, right_idx, w, h):
    top = np.array([landmarks[top_idx].x*w, landmarks[top_idx].y*h])
    bottom = np.array([landmarks[bottom_idx].x*w, landmarks[bottom_idx].y*h])
    left = np.array([landmarks[left_idx].x*w, landmarks[left_idx].y*h])
    right = np.array([landmarks[right_idx].x*w, landmarks[right_idx].y*h])
    vert = np.linalg.norm(top - bottom)
    hor = np.linalg.norm(left - right) + 1e-6
    return vert / hor

print("Eye control running. Press q to quit.")
while True:
    ret, frame = cam.read()
    if not ret:
        print("Camera frame not read; check webcam.")
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = face_mesh.process(rgb)
    if res.multi_face_landmarks:
        lm = res.multi_face_landmarks[0].landmark
        try:
            # use iris point (475 is stable)
            iris = lm[475]
            cx = int(iris.x * w); cy = int(iris.y * h)
            screen_x = screen_w * iris.x
            screen_y = screen_h * iris.y

            # smooth with module-level _sm (mutable container)
            if _sm[0] is None:
                _sm[0] = (screen_x, screen_y)
            else:
                _sm[0] = (EMA_ALPHA * screen_x + (1-EMA_ALPHA) * _sm[0][0],
                          EMA_ALPHA * screen_y + (1-EMA_ALPHA) * _sm[0][1])

            # move cursor via action queue
            enqueue(pyautogui.moveTo, int(_sm[0][0]), int(_sm[0][1]), _pause=False)

            # draw iris position for visual feedback
            cv2.circle(frame, (cx, cy), 3, (0,255,0), -1)

            # blink detection (left and right eye ratios)
            left_ratio = eye_ratio(lm, 159, 145, 33, 133, w, h)
            right_ratio = eye_ratio(lm, 386, 374, 362, 263, w, h)
            avg_ratio = (left_ratio + right_ratio) / 2.0

            now = time.time()
            # threshold tuned for most webcams; tune in later step if needed
            if avg_ratio < 0.18 and (now - last_blink) > BLINK_DEBOUNCE:
                enqueue(pyautogui.click)
                last_blink = now
                cv2.putText(frame, "Blink Click", (40,40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0),2)
        except Exception:
            pass

    cv2.imshow('Eye Controlled Mouse - press q to quit', frame)
    if cv2.waitKey(1) & 0xFF in (ord('q'),27):
        break

cam.release()
cv2.destroyAllWindows()
