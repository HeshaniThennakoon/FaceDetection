import cv2
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
import time
import os
import json

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DETECTED_FILE = os.path.join(BASE_DIR, "detected_student.json")

# Cooldown settings
last_detection_time = 0
cooldown_seconds = 30
last_detected_id = None

# Firebase initialization
cred = credentials.Certificate(os.path.join(BASE_DIR, "serviceAccountKey.json"))
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facedetection-5274a-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "facedetection-5274a.firebasestorage.app"
})
bucket = storage.bucket()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread(os.path.join(BASE_DIR, "Resources", "background.jpg"))
imgBackground = cv2.resize(imgBackground, (1280, 720))

# Load encoding file
print("Loading Encoded File ....")
with open(os.path.join(BASE_DIR, "EncodeFile.p"), "rb") as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encoded File Loaded")

# Detection loop
while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            current_time = time.time()

            # Check cooldown or new person
            if (current_time - last_detection_time > cooldown_seconds) or (last_detected_id != studentIds[matchIndex]):

                last_detection_time = current_time
                last_detected_id = studentIds[matchIndex]
                id = studentIds[matchIndex]

                # Draw face rectangle
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                # Clear old info
                imgBackground[100:720, 700:1280] = (255, 255, 255)

                # Fetch student info from Firebase
                studentInfo = db.reference(f"Student/{id}").get()
                if not studentInfo or "email" not in studentInfo:
                    continue

                # Write JSON for API
                with open(DETECTED_FILE, "w") as f:
                    json.dump({"email": studentInfo["email"], "timestamp": time.time()}, f)
                    f.flush()
                    os.fsync(f.fileno())

                print("Detected Email:", studentInfo["email"])

                # Display success
                cvzone.putTextRect(imgBackground, "Face Recognized", (275, 400), scale=2, thickness=2, colorR=(0, 255, 0))
                cv2.imshow("Face Detection", imgBackground)
                cv2.waitKey(1500)

                # Cleanup and exit
                cap.release()
                cv2.destroyAllWindows()
                exit(0)

        else:
            # Unknown person
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0, colorC=(0, 0, 255))
            imgBackground[100:720, 700:1280] = (255, 255, 255)
            cvzone.putTextRect(imgBackground, "Error : Unknown Person!", (750, 300), scale=1, thickness=2, colorR=(0, 0, 255), offset=10)

    cv2.imshow("Face Detection", imgBackground)
    cv2.waitKey(1)
