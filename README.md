# LiveBackgroundRemover
This project demonstrates a Python script that captures video using the default camera, removes the background in real-time, and saves the captured video to a file. It uses OpenCV to handle video capture and the rembg library to remove the background from each frame.

# Camera Capture with Background Removal

This project demonstrates a Python script that captures video from the default camera, removes the background in real-time, and saves the captured video to a file. It uses OpenCV to handle video capture and the `rembg` library to remove the background from each frame.

## Features
- Captures video from the default camera.
- Removes the background from the live video feed using the `rembg` library.
- Saves the video output to an MP4 file.
- Displays a real-time preview with background removal.

## Requirements
To run this script, you need:
- Python 3.x
- The following Python libraries:
  - `opencv-python`
  - `rembg`
  - `Pillow`

## Installation
To get started, clone the repository and install the necessary dependencies:

```sh
git clone <repository_URL>
cd <repository_folder>
pip install opencv-python rembg Pillow
