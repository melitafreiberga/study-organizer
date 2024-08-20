from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

import os

from my_package.google_api import authenticate_drive, create_folder, choose_folder, upload_file_to_drive


# UPLOADING A FILE TO GOOGLE DRIVE
class DriveUploaderApp(App):
    def __init__(self, **kwargs):
        """
            Initializes the DriveUploaderApp with necessary attributes.
            :param kwargs: Additional arguments passed to the parent class.
        """
        # Initialize the parent class (App) and set up initial attributes
        super().__init__(**kwargs)
        # Authenticate the user with Google Drive and get the service object
        self.service = authenticate_drive()
        # Initialize selected_folder_id to None; this will hold the ID of the selected Google Drive folder
        self.selected_folder_id = None
        # Initialize UI components as instance variables; they will be set up in the build() method
        self.layout = None
        self.file_name_input = None
        self.new_folder_input = None
        self.select_folder_btn = None
        self.upload_btn = None
        self.status_label = None
        self.folder_layout = None

    def build(self):
        """
        Builds the Kivy UI layout and returns the root widget.
        :return: The root widget for the Kivy application.
        """
        # Set up the UI layout using a vertical BoxLayout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        # Create a TextInput widget for the user to enter the file name to upload
        self.file_name_input = TextInput(hint_text='Enter file name', multiline=False)
        self.layout.add_widget(self.file_name_input)

        # Create a Button for selecting an existing folder in Google Drive
        self.select_folder_btn = Button(text="Select Folder to Upload")
        self.select_folder_btn.bind(on_press=self.select_folder)
        self.layout.add_widget(self.select_folder_btn)

        # Create a TextInput widget for entering a new folder name (optional)
        self.new_folder_input = TextInput(hint_text='Enter new folder name (optional)', multiline=False)
        self.layout.add_widget(self.new_folder_input)

        # Layout for folder selection buttons
        self.folder_layout = BoxLayout(orientation='vertical', spacing=5)
        self.layout.add_widget(self.folder_layout)

        # Create a Button for uploading the file to the selected or newly created folder
        self.upload_btn = Button(text="Upload File")
        self.upload_btn.bind(on_press=self.upload_file)
        self.layout.add_widget(self.upload_btn)

        # Create a Label to display status messages to the user (e.g., upload success, errors)
        self.status_label = Label(text="")
        self.layout.add_widget(self.status_label)

        # Return the completed layout to be used as the root widget of the application
        return self.layout
    '''
    def select_folder(self, instance):
        """ Handles the event when the 'Select Folder to Upload' button is pressed. """
        # Folders are listed in the status_label, and the user can input the ID in the TextInput field.
        folders = choose_folder(self.service, self.status_label)
    '''

    def select_folder(self, instance):
        """ Handles the event when the 'Select Folder to Upload' button is pressed. """
        # Clear any existing folder buttons
        self.folder_layout.clear_widgets()

        # Fetch folders from Google Drive
        folders = choose_folder(self.service, self.status_label)

        if folders:
            # Create a button for each folder
            for folder in folders:
                button = Button(text=f"{folder['name']} (ID: {folder['id']})", size_hint_y=None, height=40)
                button.bind(on_press=lambda btn, folder_id=folder['id']: self.set_selected_folder(folder_id))
                self.folder_layout.add_widget(button)
        else:
            self.status_label.text = "No folders found, file will be uploaded to the root directory."

    def set_selected_folder(self, folder_id):
        # Set the selected folder ID and update the status label
        self.selected_folder_id = folder_id
        self.status_label.text = f"Selected Folder ID: {folder_id}"

    def upload_file(self, instance):
        """
        Handles the event when the 'Upload File' button is pressed.

        :param instance: The button instance that triggered the event.
        :return: None
        """
        # Get the new folder name from the input
        new_folder_name = self.new_folder_input.text.strip()
        if new_folder_name:
            # Create a new folder if a name is provided
            self.selected_folder_id = create_folder(self.service, new_folder_name, self.status_label)

        file_path = self.file_name_input.text.strip()  # Get the file path from the input

        if file_path and os.path.exists(file_path):  # Check if the file exists
            # Upload the file to Google Drive
            upload_file_to_drive(self.service, file_path, self.selected_folder_id, self.status_label)
            # Update the status label
            self.status_label.text += f"\nFile '{file_path}' uploaded successfully!"
        else:
            # Display an error if the file doesn't exist
            self.status_label.text = "File not found. Please check the file name and try again."
