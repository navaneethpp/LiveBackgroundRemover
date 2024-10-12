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

# Create a PyQt application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("Background Selector with Blur")
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

    def __init__(self):
        super().__init__()
        self._is_running = False

    def run(self):
        self._is_running = True
        # Open the default camera
        cam = cv2.VideoCapture(0)

        # Check if the camera opened successfully
        if not cam.isOpened():
            print("Error: Could not access the camera.")
            return

        # Get the default frame width and height
        frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output_with_bg.mp4', fourcc, 20.0, (frame_width, frame_height))

        # Run the video processing loop
        while self._is_running:
            ret, frame = cam.read()

            if not ret:
                print("Error: Could not read frame from camera.")
                break

            global processed_frame  # Use global variable to store the processed frame

            # Convert the frame to RGB format for rembg processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            # Remove the background
            try:
                removed_bg = remove(frame_pil)
            except Exception as e:
                print(f"Error during background removal: {e}")
                break

            # Convert the processed PIL image back to OpenCV format (keeping color channels correct)
            frame_no_bg = cv2.cvtColor(np.array(removed_bg), cv2.COLOR_RGBA2BGRA)

            # Check if a background image is selected
            if background_image_path and os.path.isfile(background_image_path):
                # Open and read the background image using OpenCV
                bg_image = cv2.imread(background_image_path)

                # Check if the background image is loaded properly
                if bg_image is None:
                    print(f"Error: Could not read the image from the path '{background_image_path}'.")
                    break

                # Resize the background image to match the frame size
                bg_image_resized = resize_background(bg_image, frame_width, frame_height)

                # Get the selected blur level
                blur_text = blur_combo.currentText()
                if blur_text == "No Blur":
                    blur_level = 0
                else:
                    blur_level = int(blur_text)

                # Apply the selected blur to the background
                bg_image_blurred = apply_blur(bg_image_resized, blur_level)

                # Extract the alpha channel as a mask
                if frame_no_bg.shape[-1] == 4:  # Check if the image has an alpha channel
                    alpha_channel = frame_no_bg[:, :, 3]  # Extract the alpha channel
                    mask = alpha_channel / 255.0  # Normalize the mask to range [0, 1]

                    # Extract the RGB channels without the alpha
                    frame_rgb_no_alpha = frame_no_bg[:, :, :3]

                    # Blend the frame with the blurred background using the mask
                    fg_part = (mask[:, :, None] * frame_rgb_no_alpha).astype(np.uint8)
                    bg_part = ((1 - mask)[:, :, None] * bg_image_blurred).astype(np.uint8)
                    final_frame = cv2.add(fg_part, bg_part)
                else:
                    final_frame = frame
            else:
                final_frame = frame

            # Write the frame with the new background to the output file
            out.write(final_frame)

            # Emit the processed frame
            self.frame_signal.emit(final_frame)

            # Store the processed frame for capture
            processed_frame = final_frame.copy()

        # Release the capture and writer objects
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
        camera_thread = CameraThread()

    # Connect the frame signal to the display function
    camera_thread.frame_signal.connect(display_frame)

    # Connect the finished signal to update the UI
    camera_thread.finished_signal.connect(on_camera_stopped)

    # Start the camera thread
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
    # Convert frame from BGR to RGB format
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the RGB image to QImage
    height, width, channel = rgb_image.shape
    bytes_per_line = 3 * width
    qt_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

    # Display the QImage in the QLabel
    video_label.setPixmap(QPixmap.fromImage(qt_image))

# Function to capture the current processed frame as an image
def capture_image():
    global processed_frame
    if processed_frame is not None:
        # Get the current directory where the script is running
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Generate an automatic filename using the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(current_directory, f"processed_image_{timestamp}.png")

        # Save the current processed frame
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
