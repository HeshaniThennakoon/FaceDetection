import cv2
import pickle
import face_recognition
import os
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facedetection-5274a-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket':"facedetection-5274a.firebasestorage.app"
})



bucket = storage.bucket()
# Check if the bucket exists




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

        if matches[matchIndex]:
            # print("Known Face Detected")
            # print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]
            # print(studentIds)
            # print("ID:", id)

            # Get student info from Firebase
            if counter == 0:
                counter = 1
                # studentId = studentIds[matchIndex]
                # print("Student ID:", studentId)

                if counter!= 0:

                    if counter == 1:
                        # Get the Data from Firebase
                        studentInfo = db.reference(f'Students/{id}').get()
                        print("Student Info:", studentInfo)


                        # Get the Image from Firebase Storage
                        blob = bucket.get_blob(f'Images/{id}.jpeg')
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                        # imgStudent = cv2.resize(imgStudent, (200, 200))


                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 100), cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 50, 50), 1)

                        cv2.putText(imgBackground, str(studentInfo['regNo']), (750, 470), cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['batch']), (750, 500), cv2.FONT_HERSHEY_COMPLEX, 0.7, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['academicYear']), (1050, 500), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['department']), (750, 530), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['email']), (750, 560), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['phone']), (750, 590), cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
                        cv2.putText(imgBackground, str(studentInfo['address']), (750, 620), cv2.FONT_HERSHEY_COMPLEX, 0.5, (50, 50, 50), 1)
                        

                        # Resize the student image
                        imgStudent = cv2.resize(imgStudent, (216, 216))
                        # Place the student image on the background
                        imgBackground[175:175+216, 909:909+216] = imgStudent                       


                        counter += 1


    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Detection", imgBackground)
    cv2.waitKey(1)