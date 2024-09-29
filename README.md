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
```

## Usage
Run the script to start capturing video:
```sh
python camera.py
```
The video feed will be displayed in a window, and the background will be removed in real-time. Press q to stop capturing.

## How it Works
- Video Capture: The script uses OpenCV to capture frames from the default camera.
- Background Removal: The rembg library is used to remove the background from each frame.
- Video Saving: The modified frames are saved to an output file (output.mp4) using OpenCV's VideoWriter.

## Notes
- Ensure that your camera is properly connected and accesible
- Background removal might require good lighting conditions for better results

## License
This project is licensed under the GNU General Public License v3.0.

## Contributing
Feel free to contribute by submitting issues or pull requests.

## Acknowledgments
- Thanks to the developers of OpenCV for making video capture simple
- Special thanks to rembg for the easy-to-use background removal.
