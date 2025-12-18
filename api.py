from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import json
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DETECTED_FILE = os.path.join(BASE_DIR, "detected_student.json")

app = Flask(__name__)

# Enable CORS for ASP.NET frontend
CORS(app, resources={
    r"/start-face-login": {"origins": "https://localhost:7205"}
})

@app.route("/start-face-login", methods=["POST"])
def start_face_login():

    # Remove old detection result
    if os.path.exists(DETECTED_FILE):
        os.remove(DETECTED_FILE)

    # Start main.py in the same directory
    subprocess.Popen(
        ["python", "main.py"],
        cwd=BASE_DIR,
        shell=False
    )

    # Wait up to 15 seconds for detection
    MAX_WAIT_SECONDS = 15
    for _ in range(MAX_WAIT_SECONDS * 2):
        time.sleep(0.5)
        if os.path.exists(DETECTED_FILE):
            with open(DETECTED_FILE, "r") as f:
                data = json.load(f)
            return jsonify({
                "success": True,
                "email": data.get("email")
            })

    # Timeout
    return jsonify({
        "success": False,
        "message": "Face not recognized"
    })


if __name__ == "__main__":
    app.run(port=5001)
