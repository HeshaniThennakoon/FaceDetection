import cv2
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
import time
import json

# Set cooldown periods
last_detection_time = 0
cooldown_seconds = 30
last_detected_id = None

# Firebase INIT
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facedetection-5274a-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket':"facedetection-5274a.firebasestorage.app"
})

bucket = storage.bucket()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.jpg")
imgBackground = cv2.resize(imgBackground, (1280, 720))


# Load the encoding file
print("Loading Encoded File ....")
file = open("EncodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encoded File Loaded")


counter = 0
id = -1
imgStudent = []


while True:
    success, img = cap.read()
    if not success:
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480,55: 55 + 640] = img

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches:", matches)
        # print("faceDis:", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("match Index:", matchIndex)

        # Known person
        if matches[matchIndex]:
            current_time = time.time()

            # New person OR cooldown expired
            if (current_time - last_detection_time > cooldown_seconds) or (last_detected_id != studentIds[matchIndex]):

                last_detection_time = current_time
                last_detected_id = studentIds[matchIndex]
                id = studentIds[matchIndex]

                # Draw face rectangle
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                # Clear old student info area
                imgBackground[100:720, 700:1280] = (255, 255, 255)  # white area

                # Fetch student data
                studentInfo = db.reference(f"Students/{last_detected_id}").get()

                if not studentInfo or "email" not in studentInfo:
                    continue

                # Save email temporarily
                with open("detected_student.json", "w") as f:
                    json.dump({
                        "email": studentInfo["email"],
                        "timestamp": time.time()
                    }, f)

                print("Detected Email:", studentInfo["email"])

                # SHOW SUCCESS
                cvzone.putTextRect(
                    imgBackground,
                    "Face Recognized",
                    (275, 400),
                    scale=2,
                    thickness=2,
                    colorR=(0, 255, 0)
                )

                cv2.imshow("Face Detection", imgBackground)
                cv2.waitKey(1500)

                # CLEAN EXIT
                cap.release()
                cv2.destroyAllWindows()
                exit()

                # Show "Loading..." before fetching data
                cvzone.putTextRect(imgBackground, "Loading...", (275, 400))
                cv2.imshow("Face Detection", imgBackground)
                cv2.waitKey(1)

                # Fetch student data
                studentInfo = db.reference(f'Students/{id}').get()
                print("Student Info:", studentInfo)

                # Fetch image from Firebase Storage
                blob = bucket.get_blob(f'Images/{id}.jpeg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Display text info
                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2
                cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['regNo']), (750, 470), cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['batch']), (750, 500), cv2.FONT_HERSHEY_COMPLEX, 0.7, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['academicYear']), (1050, 500), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['department']), (750, 530), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['email']), (750, 560), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['phone']), (750, 590), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['address']), (750, 620), cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)

                # Display student image
                imgStudent = cv2.resize(imgStudent, (216, 216))
                imgBackground[175:175+216, 909:909+216] = imgStudent
                
        # Unknown Person 
        else:
            # Draw face rectangle
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0, colorC=(0,0,255))

            # clear old student info area
            imgBackground[100:720, 700:1280] = (255, 255, 255)

            # Show error message
            cvzone.putTextRect(imgBackground, "Error : Unknown Person!", (750, 300), scale=1, thickness=2, colorR=(0, 0, 255), offset=10)


    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Detection", imgBackground)
    cv2.waitKey(1)