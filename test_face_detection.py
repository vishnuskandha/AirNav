"""Quick test for face detection"""
import cv2
import numpy as np

CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

cap = cv2.VideoCapture(0)
print("Press ESC to exit, showing face detection for 10 seconds...")

import time
start = time.time()

while time.time() - start < 10:
    ret, frame = cap.read()
    if not ret:
        print("Can't read frame")
        break
    
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Try different parameters
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
    
    print(f"Detected {len(faces)} faces")
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, "FACE", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    cv2.imshow('Face Detection Test', frame)
    
    if cv2.waitKey(100) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("Test complete")
