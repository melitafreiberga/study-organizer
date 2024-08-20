# study-organizer
## Image Scanner and Document Management Tool
This Python-based application enables users to scan physical documents using a webcam, process the captured images, and save them either locally as a PDF or PNG file or directly upload them to Google Drive. The program features advanced image processing techniques, including contour detection, perspective transformation, binarization, and sharpening, to ensure high-quality document scans. Additionally, it offers optical character recognition (OCR) for extracting text from scanned documents, which can be manually reviewed and edited through a graphical user interface (GUI) built with Kivy.

## Table of Contents
- [Repository Structure](#repository-structure)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Contact Information](#contact-information)
- [Known Issues / Troubleshooting](#known-issues--troubleshooting)
- [Future Enhancements](#future-enhancements)

## Repository Structure
- `src/`: Contains the source code for the application.
  - `main.py`: The main script to run the application.
  - `utils/`: Folder with Utility functions used across the project.
     - `image_processing.py`:
     - `google-api.py`
     - `driver_uploader`:

## Features
- Capture images via webcam.
- Advanced document processing techniques.
- Optical Character Recognition (OCR).
- Save files as PDF or PNG.
- Google Drive integration.

## Installation
### Prerequisites
- Python 3.x
- OpenCV
- PyTesseract
- Kivy
- Google Drive API

### Setup
1. Clone the repository: git clone https://github.com/your-username/your-repository-name.git
2. Navigate to the project directory: cd your-repository-name
3. Install the required dependencies: pip install -r requirements.txt
4. Place the Google Drive OAuth credentials JSON file in the root directory.

## Usage
To run the application, navigate to the src directory of the project and execute the following command: python main.py

## Configuration
Google Drive Integration
1.	Create a New Project:
   - Go to the Google Cloud Console (https://console.cloud.google.com/).
   - Click on the project drop-down in the top left and select “New Project.”
   - Name your project and click “Create.”
2.	Enable Google Drive API:
   - In your project, go to “APIs & Services” > “Library.”
   - Search for “Google Drive API” and click “Enable.”
3.	Set Up OAuth 2.0 Credentials:
   - Go to “APIs & Services” > “Credentials.”
   - Click “+ CREATE CREDENTIALS” and select “OAuth 2.0 Client IDs.”
   - Configure the consent screen, then create the OAuth client ID, selecting “Desktop app” as the application type.
4.	Download the Credentials File:
   - Once the OAuth client ID is created, download the credentials.json file.
   - Save this file securely in your project directory and ensure it’s not publicly accessible (e.g., add to .gitignore if using Git).

## Contributing
1. Fork the repository.
2. Create a new branch: git checkout -b feature-branch
3. Make your changes and commit: git commit -m "Add a new feature"
4. Push to your branch: git push origin feature-branch
5. Open a Pull Request.

## License
This project is licensed under the MIT License.

## Credits
This project utilizes the following libraries and tools:
- **OpenCV** for image processing.
- **PyTesseract** for OCR.
- **Kivy** for creating the graphical user interface.
- **Google Drive API** for file uploads.

## Contact Information
For any questions or feedback, feel free to reach out on GitHub: melitafreiberga

## Known Issues / Troubleshooting
- Issue 1: If the webcam fails to capture images, ensure the webcam is correctly connected and that no other application is using it.
- Issue 2: In case of OCR inaccuracies, try adjusting the image contrast or resolution.
- Issue 3: It may not be possible to save files to old Google Drive folders, however, folders originally created via this program work.
 
## Future Enhancements
- Multiple Language OCR: Add support for extracting text in languages other than English.
- Enhanced Google Drive Integration: Allow users to manage and organize files more effectively within Google Drive.
- Improved GUI: Expand the user interface with more features and customization options.
