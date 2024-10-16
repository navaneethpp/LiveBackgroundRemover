# Camera Capture with Background Removal

This Python application uses OpenCV, rembg, and PyQt6 to provide a graphical user interface for applying background images and blur effects to a live video feed captured from your camera. The background removal is powered by the rembg library, allowing dynamic replacement with a selected background image. Users can also control the level of blur applied to the background and capture processed frames as images.

## FeaturesCaptures video from the default camera.
- Live camera feed with real-time background removal.
- Option to replace the removed background with a custom image.
- Adjustable background blur levels (from 0 to 5).
- Capture and save processed frames as PNG images.
- Simple GUI built using PyQt6.
- Camera Selection Option

## Requirements
To run this script, you need:
- Python 3.7 or higher
- OpenCV
- rembg
- PyQt6
- Pillow(PIL)

## Installation
To get started, clone the repository and install the necessary dependencies:

```sh
git clone https://github.com/navaneethpp/LiveBackgroundRemover.git
cd <repository_folder>
pip install opencv-python rembg Pillow
```
## How to Use
1. Select a Background Image:
   - Click on the `Select Background Image` button to choose an image file that will be used as the background
2. Adjust the Blur Level:
   - Use the `Select Blur Level` dropdown to adjust the blur effect applied to the background
3. Start/Stop the Camera:
   - Click on the `Start Camera` button to start the live camera feed.
   - The `Stop Camera` button stops the feed when clicked.
5. Capture an Image:
   - After starting camera, you can click on the `Capture Image` button to save the current processed frame as a PNG file. The image will be saved in the same directory as the script with an automatic filename based on the timestamp.
  
## Dependencies
The project uses the following libraries:
- **OpenCV**: For capturing live video feed and processing images.
- **rembg**: To remove the background from the camera feed.
- **PyQt6**: To create the graphical user interface (GUI).
- **Pillow(PIL)**: To handle image formats for background removal.
- **NumPy**: For handling image arrays and numeric operations.

Install all dependencies by running:
`pip install opencv-python rembg PyQt6 pillow numpy`

## Privacy Disclaimer
The `rembg` library, which is used for background removal, may make use of third-party remote servers for processing images. This means that when using this application, your video feed or images may be uploaded to external servers for the purpose of removing the background

Please be aware of the following:
- **Internet Access:** The `rembg` package requires an active internet connection for background removal.
- **Data Privacy:** If privacy is a concern, be cautious about the type of image or videos you process, as they might be transmitted over the internet.
- **Local Processing:** For environments where privacy is critical, consider using alternative local models or tools for background removal that don't rely on external servers.

By using this application, you acknowledge and accept that the remg package may send images to external servers for processing.

## License
This project is licensed under the GNU General Public License v3.0.

## Contribution
If you would like to contribute, feel free to create a pull request or open an issue for bugs or featur suggestions.

## Disclaimer on Privacy

This project uses the `rembg` package, which requires an internet connection for background removal. Be aware that processing images through external services may involve privacy concerns regarding the data being transmitted. I, as the project owner, am not responsible for any privacy issues that arise due to external packages or services. If you encounter any privacy-related concerns, please report them, and I will address them accordingly.
