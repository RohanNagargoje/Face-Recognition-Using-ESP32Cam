import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import urllib.request
import numpy as np
import os
from PIL import Image, ImageTk
import threading
import time

# Global variables
camera_mode = "ESP32"
esp32_url = 'http://192.168.231.162/cam-hi.jpg'
local_webcam_index = 0
recognition_active = False
cap = None
selected_resolution = "High"

# Flags for camera status
esp32_available = False
webcam_available = False

# Lock for thread-safe GUI updates
gui_lock = threading.Lock()

# Load faces from the 'faces' folder
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_path = os.path.join(script_dir, 'faces')
if not os.path.exists(faces_path):
    os.makedirs(faces_path)
    print(f"'faces' folder created at: {faces_path}. Add face images and restart the program.")

def load_known_faces():
    known_encodings = []
    class_names = []

    print("Loading known faces from the 'faces' folder...")
    if not os.listdir(faces_path):
        print("No face images found in the 'faces' folder. Add some images and restart.")
        return known_encodings, class_names

    for file_name in os.listdir(faces_path):
        file_path = os.path.join(faces_path, file_name)
        img = cv2.imread(file_path)
        if img is None:
            print(f"Skipping invalid file: {file_name}")
            continue

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if encodings:
            known_encodings.append(encodings[0])
            class_names.append(os.path.splitext(file_name)[0])
        else:
            print(f"No face detected in image: {file_name}. Skipping.")

    print("Loaded known faces:", class_names)
    return known_encodings, class_names

# Initialize known faces
known_encodings, class_names = load_known_faces()

# Camera handling
def check_esp32():
    """Check if the ESP32 camera is available."""
    try:
        urllib.request.urlopen(esp32_url, timeout=2)
        return True
    except:
        return False

def check_webcam():
    """Check if the local webcam is available."""
    test_cap = cv2.VideoCapture(local_webcam_index)
    ret, _ = test_cap.read()
    test_cap.release()
    return ret

# Recognition process
def recognition_thread():
    global recognition_active, cap, camera_mode, esp32_available, webcam_available

    while recognition_active:
        if camera_mode == "ESP32":
            if not esp32_available:
                print("ESP32 camera not available. Switching to webcam...")
                camera_mode = "Webcam"
                continue

            try:
                img_resp = urllib.request.urlopen(esp32_url)
                imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                img = cv2.imdecode(imgnp, -1)
            except Exception as e:
                print(f"Error fetching ESP32 feed: {e}")
                esp32_available = False
                continue

        elif camera_mode == "Webcam":
            if not webcam_available:
                print("Webcam not available. Stopping recognition...")
                recognition_active = False
                gui_lock.acquire()
                messagebox.showerror("Error", "Neither ESP32 nor Webcam is available. Stopping recognition.")
                gui_lock.release()
                break

            if cap is None:
                cap = cv2.VideoCapture(local_webcam_index)

            ret, img = cap.read()
            if not ret:
                print("Error accessing webcam feed")
                webcam_available = False
                continue

        else:
            print("Invalid camera mode. Stopping recognition...")
            recognition_active = False
            break

        # Face recognition logic
        img_small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(img_rgb)
        face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            name = "UNKNOWN"
            if matches:
                match_index = np.argmin(face_distances)
                name = class_names[match_index].upper()

            top, right, bottom, left = [v * 4 for v in face_location]
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Update GUI
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

        gui_lock.acquire()
        video_label.img_tk = img_tk
        video_label.config(image=img_tk)
        gui_lock.release()

# GUI Setup
window = tk.Tk()
window.title("Face Recognition")
window.geometry("600x500")

video_label = tk.Label(window)
video_label.pack()

def start_recognition():
    global recognition_active, esp32_available, webcam_available, cap

    esp32_available = check_esp32()
    webcam_available = check_webcam()

    if not esp32_available and not webcam_available:
        messagebox.showerror("Error", "Neither ESP32 nor Webcam is available.")
        return

    recognition_active = True
    threading.Thread(target=recognition_thread, daemon=True).start()

def stop_recognition():
    global recognition_active, cap
    recognition_active = False
    if cap is not None:
        cap.release()
        cap = None

start_button = tk.Button(window, text="Start Recognition", command=start_recognition, width=25)
start_button.pack(pady=10)

stop_button = tk.Button(window, text="Stop Recognition", command=stop_recognition, width=25)
stop_button.pack(pady=10)

quit_button = tk.Button(window, text="Quit", command=window.destroy, width=25)
quit_button.pack(pady=10)

window.mainloop()
