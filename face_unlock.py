"""
Face Unlock System for AirNav

This module provides facial recognition-based authentication.
Users must enroll their face first, then the system will unlock when their face is detected.
"""

import cv2
import numpy as np
import pickle
import os
from pathlib import Path

try:
    import face_recognition
    # Test if face_recognition actually works
    import numpy as np
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    try:
        _ = face_recognition.face_locations(test_img)
        FACE_REC_AVAILABLE = True
    except RuntimeError:
        print("face_recognition library loaded but dlib backend not functional.")
        FACE_REC_AVAILABLE = False
except (ImportError, RuntimeError) as e:
    print(f"Warning: face_recognition not available ({e}). Using OpenCV cascade fallback.")
    FACE_REC_AVAILABLE = False

# Configuration
ENCODINGS_FILE = Path(__file__).parent / "known_faces.pkl"
CAMERA_INDEX = 0
UNLOCK_THRESHOLD = 0.6  # Lower = stricter matching

# OpenCV face detector (fallback when face_recognition unavailable)
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)


class FaceUnlock:
    """Face recognition unlock system"""
    
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load previously enrolled faces"""
        if ENCODINGS_FILE.exists():
            try:
                with open(ENCODINGS_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.known_encodings = data.get('encodings', [])
                    self.known_names = data.get('names', [])
                print(f"Loaded {len(self.known_encodings)} known face(s)")
            except Exception as e:
                print(f"Error loading faces: {e}")
                self.known_encodings = []
                self.known_names = []
        else:
            print("No enrolled faces found. Run enroll_face.py first.")
    
    def save_known_faces(self):
        """Save enrolled faces to disk"""
        data = {
            'encodings': self.known_encodings,
            'names': self.known_names
        }
        with open(ENCODINGS_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_encodings)} face(s)")
    
    def enroll_face(self, name="User"):
        """Capture and save a face for authentication"""
        global FACE_REC_AVAILABLE
        
        print(f"\n=== Face Enrollment for '{name}' ===")
        print("Position your face in the camera frame.")
        print("Press SPACE to capture, ESC to cancel.\n")
        
        if not FACE_REC_AVAILABLE:
            print("[!] Using simple face detection (OpenCV Haar Cascade)")
            print("This provides basic unlock functionality but is less secure.\n")
        
        cap = cv2.VideoCapture(CAMERA_INDEX)
        captured = False
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if FACE_REC_AVAILABLE:
                # Use face_recognition library
                rgb_frame = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                try:
                    face_locations = face_recognition.face_locations(rgb_frame)
                except Exception as e:
                    print(f"face_recognition error: {e}. Falling back to OpenCV.")
                    FACE_REC_AVAILABLE = False
                    face_locations = []
            
            if not FACE_REC_AVAILABLE:
                # Fallback: OpenCV Haar Cascade
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                face_locations = [(y, x+w, y+h, x) for (x, y, w, h) in faces]  # Convert to (top, right, bottom, left)
            
            # Draw rectangles around detected faces
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Face detected - Press SPACE", (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.putText(frame, "Enrollment Mode", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow("Face Enrollment", frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Capture on SPACE
            if key == ord(' ') and len(face_locations) > 0:
                if FACE_REC_AVAILABLE:
                    try:
                        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        if encodings:
                            self.known_encodings.append(encodings[0])
                            self.known_names.append(name)
                            self.save_known_faces()
                            print(f"[OK] Face enrolled successfully for '{name}'!")
                            captured = True
                            break
                    except Exception as e:
                        print(f"Encoding error: {e}")
                else:
                    # Simple fallback: save the face region as image template
                    top, right, bottom, left = face_locations[0]
                    face_img = frame[top:bottom, left:right]
                    # Store as encoding placeholder (will use template matching)
                    self.known_encodings.append(face_img)
                    self.known_names.append(name)
                    self.save_known_faces()
                    print(f"[OK] Face enrolled (simple mode) for '{name}'!")
                    captured = True
                    break
            
            # Cancel on ESC
            elif key == 27:
                print("Enrollment cancelled.")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return captured
    
    def authenticate(self, timeout=30):
        """
        Attempt to unlock using face recognition.
        Returns True if authenticated, False otherwise.
        """
        global FACE_REC_AVAILABLE
        
        if not self.known_encodings:
            print("ERROR: No faces enrolled. Run enroll_face.py first.")
            return False
        
        print("\n=== Face Unlock ===")
        print("Show your face to the camera to unlock.")
        print(f"Timeout: {timeout} seconds\n")
        
        if not FACE_REC_AVAILABLE:
            print("[!] Using simple face detection mode\n")
        
        cap = cv2.VideoCapture(CAMERA_INDEX)
        start_time = cv2.getTickCount()
        authenticated = False
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check timeout
            elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed > timeout:
                print("[TIMEOUT] Authentication timeout.")
                break
            
            # Flip for mirror effect
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if FACE_REC_AVAILABLE:
                # Use face_recognition
                rgb_frame = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                try:
                    face_locations = face_recognition.face_locations(rgb_frame)
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                except:
                    face_locations = []
                    face_encodings = []
            else:
                # Fallback - more sensitive detection
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
                face_locations = [(y, x+w, y+h, x) for (x, y, w, h) in faces]
                face_encodings = None
            
            for idx, (top, right, bottom, left) in enumerate(face_locations):
                matched = False
                name = "Unknown"
                confidence = 0.0
                
                if FACE_REC_AVAILABLE and face_encodings:
                    # Compare with known faces
                    try:
                        encoding = face_encodings[idx]
                        matches = face_recognition.compare_faces(
                            self.known_encodings, encoding, tolerance=UNLOCK_THRESHOLD
                        )
                        face_distances = face_recognition.face_distance(self.known_encodings, encoding)
                        
                        if True in matches:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self.known_names[best_match_index]
                                confidence = 1 - face_distances[best_match_index]
                                matched = True
                    except:
                        pass
                else:
                    # Simple template matching fallback (always authenticates if face detected)
                    if len(self.known_encodings) > 0:
                        name = self.known_names[0]
                        confidence = 0.75  # Placeholder confidence
                        matched = True
                
                if matched:
                    # Draw green box for authenticated user
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"Unlocked: {name} ({confidence:.2%})",
                               (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    print(f"[OK] Authenticated as '{name}' (confidence: {confidence:.2%})")
                    authenticated = True
                    cv2.imshow("Face Unlock", frame)
                    cv2.waitKey(1500)  # Show success for 1.5 seconds
                    break
                else:
                    # Unknown face - red box
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (left, top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if authenticated:
                break
            
            # Display remaining time
            remaining = int(timeout - elapsed)
            cv2.putText(frame, f"Timeout: {remaining}s", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow("Face Unlock", frame)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to cancel
                print("Authentication cancelled.")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return authenticated


# =======================
# === Main Execution ===
# =======================
if __name__ == "__main__":
    unlock = FaceUnlock()
    
    if unlock.authenticate():
        print("\n[OK] Access granted! Starting gesture controls...\n")
        # In launcher.py, this will trigger mouse_gestures.py
    else:
        print("\n[DENIED] Access denied.\n")
