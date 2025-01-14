# Face Recognition System with ESP32-CAM and Python GUI

This project implements a face recognition system that uses an **ESP32-CAM** as the primary video source, with a Python-based GUI for face recognition. If the ESP32-CAM is not available, the system automatically switches to a local webcam. It uses **OpenCV**, **Face Recognition**, and **Tkinter** for the GUI and recognition logic.

---

## Features

1. **ESP32-CAM Integration**: The ESP32-CAM streams video over HTTP, and the Python GUI fetches and processes the frames for face recognition.
2. **Webcam Fallback**: If the ESP32-CAM is unavailable, the system switches to the local webcam. If neither is available, it halts the recognition process with an error.
3. **Face Recognition**: Faces are recognized using the `face_recognition` library, which compares the input with preloaded encodings.
4. **Dynamic Resolution Switching**: Supports different resolutions (low, medium, high) via the ESP32-CAM's HTTP server.
5. **Threaded GUI**: The GUI remains responsive during recognition, with the recognition logic running in a separate thread.

---

## Table of Contents

1. [Installation](#installation)
2. [ESP32-CAM Setup](#esp32-cam-setup)
3. [Python GUI Usage](#python-gui-usage)
4. [Folder Structure](#folder-structure)
5. [Contributing](#contributing)
6. [License](#license)

---

## Installation

### Python Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/RohanNagargoje/face-recognition-system.git
   cd face-recognition-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` should contain:
   ```
   opencv-python
   face-recognition
   numpy
   pillow
   ```

---

## ESP32-CAM Setup

### Hardware

- ESP32-CAM Module (e.g., Ai-Thinker)
- FTDI programmer (to upload the code)
- External 5V power source if necessary

### Software

1. Install the Arduino IDE and add the ESP32 board package. Follow [this guide](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/).

2. Update the Wi-Fi credentials in the ESP32 code:
   ```cpp
   const char* WIFI_SSID = "your-SSID";
   const char* WIFI_PASS = "your-PASSWORD";
   ```

3. Flash the ESP32 code to your ESP32-CAM using the Arduino IDE.

4. After flashing, open the Serial Monitor (baud rate: 115200) to retrieve the ESP32's IP address. For example:
   ```
   Connected to Wi-Fi. IP address: 192.168.1.10
   ```

5. Visit the following endpoints to test the ESP32-CAM:
   - High Resolution: `http://<ESP32_IP>/high-res.jpg`
   - Medium Resolution: `http://<ESP32_IP>/medium-res.jpg`
   - Low Resolution: `http://<ESP32_IP>/low-res.jpg`

---

## Python GUI Usage

1. Place face images in the `faces` directory (created automatically in the project root). Each image file name should represent the name of the person (e.g., `john_doe.jpg`).

2. Run the Python GUI:
   ```bash
   python app.py
   ```

3. GUI Options:
   - **Start Recognition**: Begins face recognition using the selected camera.
   - **Stop Recognition**: Stops the face recognition process.
   - **Quit**: Closes the application.

---

## Folder Structure

```
face-recognition-system/
├── app.py               # Python GUI and recognition logic
├── esp32_cam_code.ino   # ESP32-CAM Arduino code
├── faces/               # Folder to store known face images
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
