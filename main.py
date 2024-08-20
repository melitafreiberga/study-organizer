from my_package.image_processing import DocumentProcessingApp
from my_package.drive_uploader import DriveUploaderApp


# Main logic with user choice
def main():
    # PROCESS THE IMAGE
    DocumentProcessingApp().run()

    # SAVE FILE ON GOOGLE DRIVE
    DriveUploaderApp().run()


if __name__ == "__main__":
    main()
