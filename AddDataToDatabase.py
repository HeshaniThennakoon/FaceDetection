import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facedetection-5274a-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Reference to the database
ref = db.reference('Student')
teacher_ref = db.reference('Teacher')

# Student data to add
data = {
    "EG_2020_4346":
    {
        "name": "G.H.M.Thennakoon",
        "regNo": "EG_2020_4346",
        "email": "heshanithennakoon118@gmail.com",
        "phone": "075-8167490",
        "address": "C/107, Ahambadeniya Road, Dewalegama, Sri Lanka",
        "department": "Computer Engineering",
        "batch": "22nd Batch",
        "academicYear": "2019/2020"
    },

    "EG_2020_4343":
    {
        "name": "H.A.D.Sathsarani",
        "regNo": "EG_2020_4343",
        "email": "sathsaranid31@gmail.com",
        "phone": "077-6271913",
        "address": "C/107, 2nd Lane, Galle, Sri Lanka",
        "department": "Computer Engineering",
        "batch": "22nd Batch",
        "academicYear": "2019/2020"
    },

    "EG_2019_3555":
    {
        "name": "R.H.S.Darshana",
        "regNo": "EG_2019_3555",
        "email": "samithdarshana49@gmail.com",
        "phone": "077-0215160",
        "address": "70/B, Anuradapura, Sri Lanka",
        "department": "Computer Engineering",
        "batch": "21st Batch",
        "academicYear": "2018/2019"
    },

    "EG_2019_3717":
    {
        "name": "R.M.K.N.Rathnayaka",
        "regNo": "EG_2019_3717",
        "email": "nimeshrathnayaka10@gmail.com",
        "phone": "070-5891312",
        "address": "Mawanella, Kegalle, Sri Lanka",
        "department": "Marine Engineering and Naval Architecture",
        "batch": "21st Batch",
        "academicYear": "2018/2019"
    },

    "EG_2019_3709":
    {
        "name": "R.I.M.Rajapaksha",
        "regNo": "EG_2019_3709",
        "email": "ishaararajapaksha@gmail.com",
        "phone": "077-5385995",
        "address": "Serumure, Keththapahuwa, Ambanpola, Sri Lanka",
        "department": "Marine Engineering and Naval Architecture",
        "batch": "21st Batch",
        "academicYear": "2018/2019"
    }
}

# Teacher data to add
teacher_data = {
    "TCH_001": {
        "teacherName": "A.B.C.Perera",
        "teacherID": "TCH_001",
        "teacher_email": "abcperera@university.edu",
        "teacher_phone": "071-1234567",
        "department": "Computer Engineering",
        "position": "Senior Lecturer"
    },
    "TCH_002": {
        "teacherName": "D.E.F.Kumara",
        "teacherID": "TCH_002",
        "teacher_email": "defkumara@university.edu",
        "teacher_phone": "072-7654321",
        "department": "Marine Engineering",
        "position": "Professor"
    }
}

for key, value in data.items():
    ref.child(key).set(value)

for key, value in teacher_data.items():
    teacher_ref.child(key).set(value)

print("Data added to Firebase Realtime Database.")