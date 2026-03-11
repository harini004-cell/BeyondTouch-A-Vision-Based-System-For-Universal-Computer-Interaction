# hand_controller.py
# Final hand controller based on your v2 rules (peace-to-move + thumb-open stop + accurate clicks)
import cv2, mediapipe as mp, pyautogui, time, math, random
from utils_actions import enqueue
import util

# Use CAP_DSHOW for Windows stability
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

# ----- TUNABLE CONSTANTS -----
EMA_ALPHA = 0.18                  # smoothing factor (0.12..0.28)
CLICK_PX_THRESHOLD = 50           # threshold for thumb-index px (tune)
THUMB_OPEN_PX = 90                # palm->thumb distance to consider "open" thumb
SNAPSHOT_PX_THRESHOLD = 35        # proximity for screenshot
CONFIRM_FRAMES = 1                # frames to confirm a gesture
CLICK_COOLDOWN = 0.38
DOUBLE_CLICK_WINDOW = 0.60
# -----------------------------

# state
_smoothed = None
_confirm = {"left":0, "right":0, "double":0, "screenshot":0, "move":0}
_last_left = 0
_last_right = 0
_last_double = 0
_last_move_state = False

def is_finger_up(landmarks, tip_idx, pip_idx):
    try:
        return landmarks[tip_idx][1] < landmarks[pip_idx][1]
    except:
        return False

def thumb_is_open(landmarks, frame_w, frame_h):
    palm = landmarks[9]  # approximated palm center
    thumb_tip = landmarks[4]
    dist = util.pixel_distance(palm, thumb_tip, frame_w, frame_h)
    return dist > THUMB_OPEN_PX, int(dist)

def smooth_and_move(tx, ty):
    global _smoothed
    if _smoothed is None:
        _smoothed = (tx, ty)
    else:
        sx = EMA_ALPHA * tx + (1 - EMA_ALPHA) * _smoothed[0]
        sy = EMA_ALPHA * ty + (1 - EMA_ALPHA) * _smoothed[1]
        _smoothed = (sx, sy)
    enqueue(pyautogui.moveTo, int(_smoothed[0]), int(_smoothed[1]), _pause=False)

def detect_gestures_and_act(frame, lm_list, processed):
    global _confirm, _last_left, _last_right, _last_double, _last_move_state

    h, w, _ = frame.shape
    if len(lm_list) < 21:
        cv2.putText(frame, "No hand detected", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
        _last_move_state = False
        return

    # finger up detection
    idx_up = is_finger_up(lm_list, 8, 6)
    mid_up = is_finger_up(lm_list, 12, 10)
    ring_up = is_finger_up(lm_list, 16, 14)
    pinky_up = is_finger_up(lm_list, 20, 18)
    thumb_open, thumb_px = thumb_is_open(lm_list, w, h)

    thumb_index_px = util.pixel_distance(lm_list[4], lm_list[8], w, h)
    ang_idx = util.get_angle(lm_list[5], lm_list[6], lm_list[8])
    ang_mid = util.get_angle(lm_list[9], lm_list[10], lm_list[12])

    # overlays for debugging & tuning
    status_line = f"thumb_idx_px:{int(thumb_index_px)} thumb_open_px:{thumb_px}  ang_idx:{int(ang_idx)} ang_mid:{int(ang_mid)}"
    cv2.putText(frame, status_line, (10,24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
    fingers_line = f"I:{'U' if idx_up else '-'} M:{'U' if mid_up else '-'} R:{'U' if ring_up else '-'} P:{'U' if pinky_up else '-'} ThumbOpen:{'Y' if thumb_open else 'N'}"
    cv2.putText(frame, fingers_line, (10,46), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,255,180), 1)

    # peace gesture (index+middle up; ring+pinky down)
    peace = idx_up and mid_up and (not ring_up) and (not pinky_up)
    if peace:
        if not thumb_open:
            # move cursor mapped from index fingertip landmark
            idx_obj = processed.multi_hand_landmarks[0].landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
            screen_x = idx_obj.x * screen_w
            screen_y = idx_obj.y * screen_h
            smooth_and_move(screen_x, screen_y)
            _last_move_state = True
            cv2.putText(frame, "MOVE (peace + thumb closed)", (10,74), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
            # reset click confirms while moving
            _confirm = {k:0 for k in _confirm}
            return
        else:
            # peace + thumb open -> hold (do nothing), but allow clicks if made
            cv2.putText(frame, "HOLD (peace + thumb open)", (10,74), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180,180,255), 2)
            # continue to allow click gestures

    now = time.time()

    # LEFT CLICK
    left_condition = (ang_idx < 50) and (ang_mid > 90) and (thumb_index_px > CLICK_PX_THRESHOLD)
    if left_condition:
        _confirm["left"] += 1
    else:
        _confirm["left"] = 0
    if _confirm["left"] >= CONFIRM_FRAMES and (now - _last_left) > CLICK_COOLDOWN:
        enqueue(pyautogui.click)
        _last_left = now
        _confirm["left"] = 0
        cv2.putText(frame, "Left Click", (10,104), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        return

    # RIGHT CLICK
    right_condition = (ang_mid < 50) and (ang_idx > 90) and (thumb_index_px > CLICK_PX_THRESHOLD)
    if right_condition:
        _confirm["right"] += 1
    else:
        _confirm["right"] = 0
    if _confirm["right"] >= CONFIRM_FRAMES and (now - _last_right) > CLICK_COOLDOWN:
        enqueue(pyautogui.rightClick)
        _last_right = now
        _confirm["right"] = 0
        cv2.putText(frame, "Right Click", (10,134), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
        return

    # DOUBLE CLICK
    double_condition = (ang_idx < 50) and (ang_mid < 50) and (thumb_index_px > CLICK_PX_THRESHOLD)
    if double_condition:
        _confirm["double"] += 1
    else:
        _confirm["double"] = 0
    if _confirm["double"] >= CONFIRM_FRAMES:
        if (now - _last_double) < DOUBLE_CLICK_WINDOW:
            enqueue(pyautogui.doubleClick)
            cv2.putText(frame, "Double Click", (10,164), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
            _last_double = 0
            _confirm["double"] = 0
            return
        else:
            _last_double = now
            _confirm["double"] = 0

    # SCREENSHOT
    snap_condition = (ang_idx < 50) and (ang_mid < 50) and (thumb_index_px < SNAPSHOT_PX_THRESHOLD)
    if snap_condition:
        _confirm["screenshot"] += 1
    else:
        _confirm["screenshot"] = 0
    if _confirm["screenshot"] >= CONFIRM_FRAMES:
        def save_shot():
            im = pyautogui.screenshot()
            im.save(f'my_screenshot_{random.randint(1000,9999)}.png')
        enqueue(save_shot)
        _confirm["screenshot"] = 0
        cv2.putText(frame, "Screenshot Taken", (10,194), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
        return

def main():
    print("Running hand_controller.py — press 'q' in window to quit")
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("camera read failed")
                break
            frame = cv2.flip(frame, 1)  # mirror for natural interaction
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            lm_list = []
            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)
                for lm in hand_landmarks.landmark:
                    lm_list.append((lm.x, lm.y))

            detect_gestures_and_act(frame, lm_list, processed)
            cv2.imshow("Hand Controller (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
