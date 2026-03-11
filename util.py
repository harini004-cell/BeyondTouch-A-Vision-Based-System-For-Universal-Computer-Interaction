# util.py
import math
import numpy as np

def get_angle(a, b, c):
    """
    a,b,c are tuples (x,y) in normalized coords (0..1) or pixels.
    returns angle at point b formed by a-b-c in degrees (0..180)
    """
    (ax, ay), (bx, by), (cx, cy) = a, b, c
    v1 = (ax - bx, ay - by)
    v2 = (cx - bx, cy - by)
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    n1 = math.hypot(v1[0], v1[1])
    n2 = math.hypot(v2[0], v2[1])
    if n1 == 0 or n2 == 0:
        return 0.0
    cosv = max(-1.0, min(1.0, dot / (n1*n2)))
    return math.degrees(math.acos(cosv))

def pixel_distance(a, b, frame_w, frame_h):
    """
    a and b are normalized landmark tuples (x_norm, y_norm) OR pixel coords.
    If the numbers are <=1 assume normalized and convert using frame size.
    Returns Euclidean pixel distance.
    """
    ax, ay = a
    bx, by = b
    if max(ax,ay) <= 1.05 and max(bx,by) <= 1.05:
        ax *= frame_w; ay *= frame_h
        bx *= frame_w; by *= frame_h
    return math.hypot(ax - bx, ay - by)

def get_distance(landmark_list):
    """
    compatibility helper used in some legacy code:
    if given a list of two (x,y) normalized coords returns pixel-like measure scaled to 0..1000
    (not used by the final hand_controller, provided for backward compatibility)
    """
    if len(landmark_list) < 2:
        return 0
    (x1,y1), (x2,y2) = landmark_list[0], landmark_list[1]
    L = math.hypot(x2 - x1, y2 - y1)
    # map normalized distance (0..~0.5) to 0..1000 for compatibility with original repo
    return np.interp(L, [0, 1], [0, 1000])
