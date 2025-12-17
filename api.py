from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import json
import os

app = Flask(__name__)

# Enable CORS for ASP.NET frontend
CORS(app, resources={
    r"/start-face-login": {
        "origins": "https://localhost:7205"
    }
})

@app.route("/start-face-login", methods=["POST"])
def start_face_login():

    # Delete old detection file
    if os.path.exists("detected_student.json"):
        os.remove("detected_student.json")

    # Run face detection
    subprocess.Popen(["python", "main.py"])

    # Wait up to 15 seconds for detection
    for _ in range(30):
        time.sleep(0.5)
        if os.path.exists("detected_student.json"):
            with open("detected_student.json", "r") as f:
                data = json.load(f)
                return jsonify({
                    "success": True,
                    "email": data["email"]
                })

    return jsonify({
        "success": False,
        "message": "Face not recognized"
    })

if __name__ == "__main__":
    app.run(port=5001)
