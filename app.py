import tkinter as tk
from tkinter import ttk
import cv2
import face_recognition
import urllib.request
import numpy as np
import os
from PIL import Image, ImageTk

# Global variables
camera_mode = "ESP32"  # Default to ESP32 camera
esp32_url = 'http://192.168.231.162/cam-hi.jpg'  # ESP32 Camera URL
local_webcam_index = 0  # Index for the local webcam (usually 0)
recognition_active = False
cap = None
selected_resolution = "High"

# Load faces from the 'faces' folder
script_dir = os.path.dirname(os.path.abspath(__file__))
faces_path = os.path.join(script_dir, 'faces')
if not os.path.exists(faces_path):
    os.makedirs(faces_path)
    print(f"'faces' folder created at: {faces_path}. Add face images and restart the program.")

# Encoding known faces
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

        # Convert image to RGB and encode face
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if encodings:
            known_encodings.append(encodings[0])
            class_names.append(os.path.splitext(file_name)[0])
        else:
            print(f"No face detected in image: {file_name}. Skipping.")

    print("Loaded known faces:", class_names)
    return known_encodings, class_names


# Initialize known faces and encodings
known_encodings, class_names = load_known_faces()

# GUI
window = tk.Tk()
window.title("Face Recognition")
window.geometry("500x500")

# Dropdown for resolution
def update_esp32_url(*args):
    global esp32_url
    resolutions = {
        "Low": "http://192.168.231.162/cam-lo.jpg",
        "Medium": "http://192.168.231.162/cam.bmp",
        "High": "http://192.168.231.162/cam-hi.jpg"
    }
    esp32_url = resolutions[resolution_var.get()]

resolution_var = tk.StringVar(value="High")
resolution_var.trace("w", update_esp32_url)

resolution_label = tk.Label(window, text="Select Resolution:")
resolution_label.pack(pady=5)

resolution_dropdown = ttk.Combobox(window, textvariable=resolution_var, values=["Low", "Medium", "High"], state="readonly")
resolution_dropdown.pack(pady=5)

# Video feed display
video_label = tk.Label(window)
video_label.pack()

# Switch camera
def switch_camera():
    global camera_mode, cap, recognition_active
    if recognition_active:
        stop_recognition()

    if camera_mode == "ESP32":
        camera_mode = "Webcam"
        switch_button.config(text="Switch to ESP32 Camera")
    else:
        camera_mode = "ESP32"
        switch_button.config(text="Switch to Webcam")

# Start/Stop video feed
def start_recognition():
    global recognition_active, cap
    recognition_active = True
    start_button.config(text="Stop Face Recognition")
    
    while recognition_active:
        if camera_mode == "ESP32":
            try:
                # Fetch frame from ESP32 camera
                img_resp = urllib.request.urlopen(esp32_url)
                imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
                img = cv2.imdecode(imgnp, -1)
            except Exception as e:
                print(f"Error fetching ESP32 camera feed: {e}")
                continue
        else:
            if cap is None:
                cap = cv2.VideoCapture(local_webcam_index)
            ret, img = cap.read()
            if not ret:
                print("Error accessing local webcam feed")
                break

        # Resize and convert to RGB for face recognition
        img_small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        # Detect faces and compare with known encodings
        face_locations = face_recognition.face_locations(img_rgb)
        face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            if matches:
                match_index = np.argmin(face_distances)
                name = class_names[match_index].upper()
            else:
                name = "UNKNOWN"

            # Scale face locations back to original frame size
            top, right, bottom, left = [v * 4 for v in face_location]

            # Draw rectangle and label around face
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Convert frame to ImageTk format for display
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        video_label.img_tk = img_tk
        video_label.config(image=img_tk)
        video_label.update()

# Stop video feed
def stop_recognition():
    global recognition_active, cap
    recognition_active = False
    start_button.config(text="Start Face Recognition")
    if cap is not None:
        cap.release()
        cap = None

# Start/Stop button
def toggle_recognition():
    if recognition_active:
        stop_recognition()
    else:
        start_recognition()

# Camera switch button
switch_button = tk.Button(window, text="Switch to Webcam", command=switch_camera, width=25)
switch_button.pack(pady=10)

# Start/Stop button
start_button = tk.Button(window, text="Start Face Recognition", command=toggle_recognition, width=25)
start_button.pack(pady=10)

# Quit button
quit_button = tk.Button(window, text="Quit", command=window.destroy, width=25)
quit_button.pack(pady=10)

# Run the GUI
window.mainloop()
