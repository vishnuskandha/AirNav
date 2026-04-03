import os
import sys
import io
import time
import ctypes
from typing import Optional

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

from mediapipe.tasks.python.core import base_options as mp_base_options
from mediapipe.tasks.python.vision.core import vision_task_running_mode as mp_vtr
from mediapipe.tasks.python.vision.core import image as mp_image
from mediapipe.tasks.python import vision as mp_vision

# Restore stderr
sys.stderr = _stderr_backup


class GestureEngine:
    """Hand tracking + mouse control using MediaPipe Tasks HandLandmarker.

    This version uses the modern MediaPipe Tasks API (0.10.x+) instead of the
    deprecated mp.solutions.hands API, so it will keep working with current
    wheels on Windows / Python 3.11.
    """

    def __init__(self, model_path: Optional[str] = None):
        # Mouse controller
        self.mouse = Controller()

        # Timing variables
        self.last_double_click_time = 0.0
        self.click_delay = 0.3

        # Dragging state
        self.dragging = False
        self.pinch_start_time = 0.0
        self.drag_release_time = 0.0
        self.DRAG_HOLD_TIME = 0.8
        self.left_pinch_active = False
        self.left_click_consumed = False

        # Config
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = self._get_screen_size()
        self.LEFT_CLICK_THRESHOLD = 0.05
        self.RIGHT_CLICK_THRESHOLD = 0.05

        # Smoothing
        self.prev_x, self.prev_y = 0.0, 0.0
        self.SMOOTHING = 4

        # Click flags
        self.left_click_ready = True
        self.right_click_ready = True

        # Frame timestamp (ms) for VIDEO mode
        self.timestamp_ms = 0
        self.frame_interval_ms = 1000 // 30  # assume ~30 FPS

        # Resolve model path
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "hand_landmarker.task")

        if not os.path.exists(model_path):
            raise RuntimeError(
                f"MediaPipe hand_landmarker.task model not found at '{model_path}'. "
                "Please download the official MediaPipe hand_landmarker.task file "
                "and place it in the 'models' folder."
            )

        # MediaPipe Tasks setup (HandLandmarker in VIDEO mode)
        base_options = mp_base_options.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vtr.VisionTaskRunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = mp_vision.HandLandmarker.create_from_options(options)

        # Use the canonical hand connections defined by the Tasks API
        from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarksConnections
        self.connections = HandLandmarksConnections.HAND_CONNECTIONS

    def _get_screen_size(self):
        """Get current screen size with Windows-first fallback."""
        try:
            if os.name == "nt":
                return (
                    ctypes.windll.user32.GetSystemMetrics(0),
                    ctypes.windll.user32.GetSystemMetrics(1),
                )
        except Exception:
            pass

        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
        except Exception:
            return 1920, 1080

    # ------------------------------------------------------------------
    # Core per-frame processing
    # ------------------------------------------------------------------
    def process_frame(self, frame):
        """Process a single BGR frame: move mouse + draw landmarks.

        Returns the processed frame (BGR) for display.
        """
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Wrap into MediaPipe Image
        mp_img = mp_image.Image(
            image_format=mp_image.ImageFormat.SRGB,
            data=frame_rgb,
        )

        # Advance timestamp for VIDEO mode
        self.timestamp_ms += self.frame_interval_ms

        # Run hand landmark detection
        result = self.landmarker.detect_for_video(mp_img, self.timestamp_ms)

        if result and result.hand_landmarks and result.handedness:
            # result.hand_landmarks: List[List[NormalizedLandmark]]
            # result.handedness: List[List[Category]]
            for hand_index, (landmarks, handedness_list) in enumerate(
                zip(result.hand_landmarks, result.handedness)
            ):
                label = handedness_list[0].category_name  # "Left" or "Right"

                # Draw landmarks on the frame (using the RGB landmarks coordinates)
                self._draw_landmarks(frame, landmarks)

                if label == "Left":
                    self._handle_left_hand(landmarks)
                elif label == "Right":
                    self._handle_right_hand(landmarks)

        return frame

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    def _draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks on the BGR frame using OpenCV."""
        h, w, _ = frame.shape
        # Draw connections manually (HandLandmarksConnections is a list of index pairs)
        for connection in self.connections:
            start_idx = connection.start
            end_idx = connection.end
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            x1, y1 = int(start.x * w), int(start.y * h)
            x2, y2 = int(end.x * w), int(end.y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw keypoints
        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)

    # ------------------------------------------------------------------
    # Hand-specific logic
    # ------------------------------------------------------------------
    def _handle_left_hand(self, landmarks):
        """Left hand controls cursor movement (index finger tip)."""
        index_tip = landmarks[8]
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

    def _handle_right_hand(self, landmarks):
        """Right hand controls clicks and drag (thumb + fingers)."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]

        # Distances in normalized coordinates
        dist_index_thumb = np.hypot(
            index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y
        )
        dist_middle_thumb = np.hypot(
            middle_tip.x - thumb_tip.x, middle_tip.y - thumb_tip.y
        )

        current_time = time.time()

        # Left pinch gesture state (click or drag depending on hold time)
        if dist_index_thumb < self.LEFT_CLICK_THRESHOLD:
            if not self.left_pinch_active:
                self.left_pinch_active = True
                self.pinch_start_time = current_time
                self.left_click_consumed = False

            held_time = current_time - self.pinch_start_time
            if held_time >= self.DRAG_HOLD_TIME and not self.dragging:
                self.mouse.press(Button.left)
                self.dragging = True
                self.left_click_consumed = True
        else:
            if self.left_pinch_active and not self.left_click_consumed and self.left_click_ready:
                if current_time - self.last_double_click_time < self.click_delay:
                    self.mouse.click(Button.left, 2)
                    self.last_double_click_time = 0
                else:
                    self.mouse.click(Button.left, 1)
                    self.last_double_click_time = current_time
                self.left_click_ready = False
            else:
                self.left_click_ready = True

            self.left_pinch_active = False
            self.left_click_consumed = False
            self.pinch_start_time = 0

        # Right Click (thumb + middle)
        if dist_middle_thumb < self.RIGHT_CLICK_THRESHOLD and self.right_click_ready:
            if time.time() - self.drag_release_time > 0.3:
                self.mouse.click(Button.right, 1)
                self.right_click_ready = False
        elif dist_middle_thumb >= self.RIGHT_CLICK_THRESHOLD:
            self.right_click_ready = True

        # End drag on release
        if dist_index_thumb >= self.LEFT_CLICK_THRESHOLD and self.dragging:
            self.mouse.release(Button.left)
            self.dragging = False
            self.drag_release_time = current_time
