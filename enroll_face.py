"""
Face Enrollment Script

Run this script to register your face for the unlock system.
You only need to do this once (or when adding new authorized users).
"""

from face_unlock import FaceUnlock

if __name__ == "__main__":
    print("=== AirNav Face Enrollment ===\n")
    
    name = input("Enter your name (or press Enter for 'User'): ").strip()
    if not name:
        name = "User"
    
    unlock = FaceUnlock()
    
    if unlock.enroll_face(name):
        print(f"\n[OK] Enrollment complete! You can now use face unlock.")
    else:
        print(f"\n[ERROR] Enrollment failed. Please try again.")
