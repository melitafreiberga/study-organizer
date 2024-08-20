from utilities.image_processing import DocumentProcessingApp
from utilities.drive_uploader import DriveUploaderApp


# Main logic with user choice
def main():
    # PROCESS THE IMAGE
    DocumentProcessingApp().run()

    # SAVE FILE ON GOOGLE DRIVE
    DriveUploaderApp().run()


if __name__ == "__main__":
    main()
