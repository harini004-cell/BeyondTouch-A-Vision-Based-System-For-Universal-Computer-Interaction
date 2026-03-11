# kalman2d.py
import numpy as np

class Kalman2D:
    def __init__(self, q=1.0, r=5.0):
        self.A = np.array([[1,0,1,0],
                           [0,1,0,1],
                           [0,0,1,0],
                           [0,0,0,1]], dtype=float)
        self.H = np.array([[1,0,0,0],[0,1,0,0]], dtype=float)
        self.Q = np.eye(4)*q
        self.R = np.eye(2)*r
        self.P = np.eye(4)*1000.0
        self.x = np.zeros((4,1))
        self.initialized = False

    def predict(self):
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q

    def update(self, meas):
        z = np.array([[meas[0]],[meas[1]]], dtype=float)
        y = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

    def step(self, meas):
        if not self.initialized:
            self.x[0,0], self.x[1,0] = meas[0], meas[1]
            self.initialized = True
        self.predict(); self.update(meas)
        return float(self.x[0,0]), float(self.x[1,0])
