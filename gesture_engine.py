import os
import sys
import io
import time
import cv2
import numpy as np
from pynput.mouse import Controller, Button

# Suppress verbose logs
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"
os.environ["ABSL_MIN_LOG_LEVEL"] = "2"

# Redirect stderr to suppress MediaPipe init warnings
_stderr_backup = sys.stderr
sys.stderr = io.StringIO()

try:
    from absl import logging as absl_logging
    absl_logging.set_verbosity(absl_logging.FATAL)
except Exception:
    pass

import mediapipe as mp

# Restore stderr
sys.stderr = _stderr_backup

class GestureEngine:
    def __init__(self):
        # Mouse controller
        self.mouse = Controller()
        
        # Timing variables
        self.last_double_click_time = 0
        self.last_click_time = 0
        self.click_delay = 0.3
        
        # Dragging state
        self.dragging = False
        self.pinch_start_time = 0
        self.drag_release_time = 0
        self.DRAG_HOLD_TIME = 0.8
        
        # Mediapipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
        # Config
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.LEFT_CLICK_THRESHOLD = 0.05
        self.RIGHT_CLICK_THRESHOLD = 0.05
        
        # Smoothing
        self.prev_x, self.prev_y = 0, 0
        self.SMOOTHING = 4
        
        # Click flags
        self.left_click_ready = True
        self.right_click_ready = True

    def process_frame(self, frame):
        """
        Process a single frame: detect hands, move mouse, draw landmarks.
        Returns the processed frame (with drawings).
        """
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = hand_info.classification[0].label  # "Left" or "Right"
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # --- LEFT HAND: Mouse Movement ---
                if label == "Left":
                    index_tip = hand_landmarks.landmark[8]
                    # Scale to screen
                    DPI_FACTOR = 1.5
                    x = np.interp(index_tip.x, [0, 1], [0, self.SCREEN_WIDTH]) * DPI_FACTOR
                    y = np.interp(index_tip.y, [0, 1], [0, self.SCREEN_HEIGHT]) * DPI_FACTOR
                    
                    # Smooth
                    curr_x = self.prev_x + (x - self.prev_x) / self.SMOOTHING
                    curr_y = self.prev_y + (y - self.prev_y) / self.SMOOTHING
                    self.prev_x, self.prev_y = curr_x, curr_y
                    
                    # Move mouse
                    self.mouse.position = (curr_x, curr_y)
                
                # --- RIGHT HAND: Clicks ---
                elif label == "Right":
                    thumb_tip = hand_landmarks.landmark[4]
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    
                    dist_index_thumb = np.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                    dist_middle_thumb = np.hypot(middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y)
                    
                    current_time = time.time()
                    
                    # Left Click
                    if dist_index_thumb < self.LEFT_CLICK_THRESHOLD and self.left_click_ready:
                        if current_time - self.last_double_click_time < self.click_delay:
                            self.mouse.click(Button.left, 2)
                            self.last_double_click_time = 0
                        else:
                            self.mouse.click(Button.left, 1)
                            self.last_double_click_time = current_time
                        self.left_click_ready = False
                    elif dist_index_thumb >= self.LEFT_CLICK_THRESHOLD:
                        self.left_click_ready = True
                        
                    # Right Click
                    if dist_middle_thumb < self.RIGHT_CLICK_THRESHOLD and self.right_click_ready:
                        if time.time() - self.drag_release_time > 0.3:
                            self.mouse.click(Button.right, 1)
                            self.right_click_ready = False
                    elif dist_middle_thumb >= self.RIGHT_CLICK_THRESHOLD:
                        self.right_click_ready = True
                        
                    # Drag
                    if dist_index_thumb < self.LEFT_CLICK_THRESHOLD:
                        if self.pinch_start_time == 0:
                            self.pinch_start_time = current_time
                        held_time = current_time - self.pinch_start_time
                        if held_time >= self.DRAG_HOLD_TIME and not self.dragging:
                            self.mouse.press(Button.left)
                            self.dragging = True
                    else:
                        self.pinch_start_time = 0
                        if self.dragging:
                            self.mouse.release(Button.left)
                            self.dragging = False
                            self.drag_release_time = time.time()
                            
        return frame
