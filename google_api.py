from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate_drive():
    creds = None
    # Check if the token.json file exists (this stores the user's access and refresh tokens)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def list_folders(service):
    """
    Lists all folders in the user's Google Drive, handling pagination to retrieve all results.

    :param service: Authorized Google Drive API service instance.
    :return: A list of all folders.
    """
    folders = []
    page_token = None

    while True:
        response = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields="nextPageToken, files(id, name)",
            pageToken=page_token  # Use the pageToken to get the next page of results
        ).execute()

        folders.extend(response.get('files', []))  # Add the current page of results to the list
        page_token = response.get('nextPageToken')  # Get the nextPageToken from the response

        if not page_token:
            break  # Exit the loop if there are no more pages to retrieve

    return folders  # Return the list of folders


def create_folder(service, folder_name, status_label):
    """
    Creates a new folder in the user's Google Drive.

    :param service: Authorized Google Drive API service instance.
    :param folder_name: Name of the new folder to create.
    :param status_label: Kivy Label widget to update the status message in the GUI.
    :return: The ID of the created folder.
    """
    file_metadata = {
        'name': folder_name,  # Set the name of the new folder
        'mimeType': 'application/vnd.google-apps.folder'  # Specify that this is a folder
    }
    # Create the folder in Google Drive
    folder = service.files().create(body=file_metadata, fields='id').execute()
    # Update the GUI with the new folder ID
    status_label.text = f"Folder '{folder_name}' created with ID: {folder.get('id')}"
    return folder.get('id')


def choose_folder(service, status_label):
    """
    Lists folders and prompts the user to select one by entering its ID.

    :param service: Authorized Google Drive API service instance.
    :param status_label: Kivy Label widget to update the status message in the GUI.
    :return: The list of folders.
    """
    folders = list_folders(service)  # Get the list of folders from Google Drive
    if folders:
        # Prompt the user in the GUI
        status_label.text = "Folders found. Select one by entering its ID in the input field."
        folder_list_text = "\n".join([f"{folder['name']} (ID: {folder['id']})" for folder in folders])
        status_label.text += "\n" + folder_list_text  # Display the folder names and IDs in the GUI
    else:
        # Inform the user if no folders are found
        status_label.text = "No folders found, file will be uploaded to the root directory."
    return folders


def upload_file_to_drive(service, file_path, folder_id=None, status_label=None):
    """
    Uploads a file to the user's Google Drive, optionally to a specific folder.

    :param service: Authorized Google Drive API service instance.
    :param file_path: Path to the file to upload.
    :param folder_id: ID of the folder to upload the file to. If None, uploads to the root directory.
    :param status_label: Kivy Label widget to update the status message in the GUI.
    :return: None
    """
    file_metadata = {'name': os.path.basename(file_path)}  # Set the file name in Google Drive
    if folder_id:
        file_metadata['parents'] = [folder_id]  # Set the parent folder ID if provided

    media = MediaFileUpload(file_path, resumable=True)  # Prepare the file for upload
    # Upload the file to Google Drive
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    if status_label:
        status_label.text = f"File ID: {file.get('id')}"  # Update the GUI with the file ID
