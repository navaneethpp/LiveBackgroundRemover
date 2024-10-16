import cv2
from rembg import remove
from PIL import Image
import numpy as np
import sys
import os
import datetime
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QVBoxLayout, QPushButton, QLabel, QComboBox, QWidget, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

# Function to resize the background image to match the frame size
def resize_background(bg_image, width, height):
    return cv2.resize(bg_image, (width, height))

# Function to apply blur to the background image
def apply_blur(image, blur_level):
    if blur_level > 0:
        return cv2.GaussianBlur(image, (blur_level * 2 + 1, blur_level * 2 + 1), 0)
    return image

# Function to detect available cameras
def detect_cameras():
    available_cameras = []
    for index in range(10):  # Check the first 10 potential camera indices
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(f"Camera {index}")
            cap.release()
    return available_cameras

# Create a PyQt application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("Background Selector with Blur and Camera Selection")
layout = QVBoxLayout()

# Button to select background image
button = QPushButton("Select Background Image")
layout.addWidget(button)

# Label to display selected image path
image_label = QLabel("No image selected.")
layout.addWidget(image_label)

# Dropdown for blur selection
blur_label = QLabel("Select Blur Level:")
layout.addWidget(blur_label)

blur_combo = QComboBox()
blur_combo.addItems(["No Blur", "1", "2", "3", "4", "5"])  # Adding blur levels
layout.addWidget(blur_combo)

# Camera selection dropdown
camera_label = QLabel("Select Camera:")
layout.addWidget(camera_label)

camera_combo = QComboBox()
layout.addWidget(camera_combo)

# Populate the camera dropdown with detected cameras
available_cameras = detect_cameras()
if available_cameras:
    camera_combo.addItems(available_cameras)
else:
    camera_combo.addItem("No cameras found")

# QLabel to display the video feed
video_label = QLabel()
layout.addWidget(video_label)

# Horizontal layout for the camera control buttons
button_layout = QHBoxLayout()

# Button to start the camera
start_camera_button = QPushButton("Start Camera")
button_layout.addWidget(start_camera_button)

# Button to stop the camera
stop_camera_button = QPushButton("Stop Camera")
stop_camera_button.setEnabled(False)  # Initially disabled
button_layout.addWidget(stop_camera_button)

# Button to capture image
capture_image_button = QPushButton("Capture Image")
button_layout.addWidget(capture_image_button)

# Add the horizontal layout to the main vertical layout
layout.addLayout(button_layout)

# Global variable to hold the background image path
background_image_path = ""
processed_frame = None  # To hold the processed frame for capturing

# Function to handle the image selection
def select_image():
    global background_image_path
    background_image_path, _ = QFileDialog.getOpenFileName(
        window, "Select a Background Image", "", 
        "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff)"
    )

    # Check if a valid file path is selected
    if background_image_path and os.path.isfile(background_image_path):
        image_label.setText(f"Selected Image: {background_image_path}")
    else:
        image_label.setText("No valid background image selected.")

# Connect the button to the select_image function
button.clicked.connect(select_image)

# Set the layout for the main window
window.setLayout(layout)
window.show()

class CameraThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    finished_signal = pyqtSignal()

    def __init__(self, camera_index=0):  # Add camera index as a parameter
        super().__init__()
        self._is_running = False
        self.camera_index = camera_index

    def run(self):
        self._is_running = True
        cam = cv2.VideoCapture(self.camera_index)  # Use the selected camera index
        if not cam.isOpened():
            print(f"Error: Could not access camera {self.camera_index}.")
            return

        frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output_with_bg.mp4', fourcc, 20.0, (frame_width, frame_height))

        while self._is_running:
            ret, frame = cam.read()
            if not ret:
                print(f"Error: Could not read frame from camera {self.camera_index}.")
                break

            global processed_frame  # Use global variable to store the processed frame

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            try:
                removed_bg = remove(frame_pil)
            except Exception as e:
                print(f"Error during background removal: {e}")
                break

            frame_no_bg = cv2.cvtColor(np.array(removed_bg), cv2.COLOR_RGBA2BGRA)

            if background_image_path and os.path.isfile(background_image_path):
                bg_image = cv2.imread(background_image_path)

                if bg_image is None:
                    print(f"Error: Could not read the image from the path '{background_image_path}'.")
                    break

                bg_image_resized = resize_background(bg_image, frame_width, frame_height)

                blur_text = blur_combo.currentText()
                if blur_text == "No Blur":
                    blur_level = 0
                else:
                    blur_level = int(blur_text)

                bg_image_blurred = apply_blur(bg_image_resized, blur_level)

                if frame_no_bg.shape[-1] == 4:  # Check if the image has an alpha channel
                    alpha_channel = frame_no_bg[:, :, 3]
                    mask = alpha_channel / 255.0

                    frame_rgb_no_alpha = frame_no_bg[:, :, :3]

                    fg_part = (mask[:, :, None] * frame_rgb_no_alpha).astype(np.uint8)
                    bg_part = ((1 - mask)[:, :, None] * bg_image_blurred).astype(np.uint8)
                    final_frame = cv2.add(fg_part, bg_part)
                else:
                    final_frame = frame
            else:
                final_frame = frame

            out.write(final_frame)
            self.frame_signal.emit(final_frame)

            processed_frame = final_frame.copy()

        cam.release()
        out.release()
        self.finished_signal.emit()

    def stop(self):
        self._is_running = False

# Instantiate the CameraThread
camera_thread = CameraThread()

# Function to start the camera when the button is pressed
def start_camera():
    global camera_thread
    if not camera_thread.isRunning():
        selected_camera_index = camera_combo.currentIndex()  # Get the selected camera index
        camera_thread = CameraThread(selected_camera_index)  # Pass the selected index

    camera_thread.frame_signal.connect(display_frame)
    camera_thread.finished_signal.connect(on_camera_stopped)

    camera_thread.start()
    stop_camera_button.setEnabled(True)
    start_camera_button.setEnabled(False)

# Function to stop the camera when the button is pressed
@pyqtSlot()
def stop_camera():
    if camera_thread.isRunning():
        camera_thread.stop()

# Function to handle actions after the camera has stopped
def on_camera_stopped():
    stop_camera_button.setEnabled(False)
    start_camera_button.setEnabled(True)

# Function to display the frame in the QLabel within the GUI
def display_frame(frame):
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    height, width, channel = rgb_image.shape
    bytes_per_line = 3 * width
    qt_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

    video_label.setPixmap(QPixmap.fromImage(qt_image))

# Function to capture the current processed frame as an image
def capture_image():
    global processed_frame
    if processed_frame is not None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(current_directory, f"processed_image_{timestamp}.png")

        cv2.imwrite(save_path, processed_frame)
        QMessageBox.information(window, "Image Saved", f"Image has been saved as '{save_path}'.")
    else:
        QMessageBox.warning(window, "No Frame", "No processed frame available to capture.")

# Connect the buttons to their respective functions
start_camera_button.clicked.connect(start_camera)
stop_camera_button.clicked.connect(stop_camera)
capture_image_button.clicked.connect(capture_image)

# Set the close event to stop the camera thread before exiting the application
def close_event():
    if camera_thread.isRunning():
        camera_thread.stop()
    window.close()

window.closeEvent = lambda event: close_event()

# Start the PyQt application event loop
sys.exit(app.exec())
