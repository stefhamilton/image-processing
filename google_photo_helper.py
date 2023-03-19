import os
import json
import datetime
import sys
print(sys.executable)
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import configparser


# Existing imports and functions ...
# Set up Google Photos API credentials
def get_google_photos_credentials():
    SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/bigquery",
    ]

    creds = None

    if os.path.exists("token.json"):
        creds = credentials.Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds
# Fetch Google Photos metadata
def get_photos_metadata(service, start_time, end_time):
    try:
        next_page_token = None
        photos_metadata = []

        while True:
            results = service.mediaItems().search(
                body={
                    "filters": {
                        "dateFilter": {
                            "ranges": [
                                {
                                    "startDate": {
                                        "year": start_time.year,
                                        "month": start_time.month,
                                        "day": start_time.day,
                                    },
                                    "endDate": {
                                        "year": end_time.year,
                                        "month": end_time.month,
                                        "day": end_time.day,
                                    },
                                }
                            ]
                        },
                        "mediaTypeFilter": {
                            "mediaTypes": ["PHOTO"]
                        }
                    },
                    "pageSize": 100,
                    "pageToken": next_page_token,
                }
            ).execute()

            if "mediaItems" in results:
                photos_metadata.extend(results["mediaItems"])

            # Check if there is a nextPageToken, if not, break the loop
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break

        return photos_metadata
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


# Upload JSON files to Azure Blob Storage
def upload_to_azure_blob(photos_metadata):
    config = configparser.ConfigParser()
    config.read('config.ini')
    connection_string = config.get('DEFAULT', 'azure_connection_string')

    # Initialize the BlobServiceClient with your connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create a new container if it does not exist
    container_name = "photos-metadata"
    container_client = blob_service_client.get_container_client(container_name)

    if not container_client.exists():
        container_client = blob_service_client.create_container(container_name)

    # Upload the JSON files
    for photo in photos_metadata:
        blob_name = f"{photo['id']}.json"
        blob_client = container_client.get_blob_client(blob_name)

        # Convert the photo metadata to JSON
        photo_json = json.dumps(photo)

        # Upload the JSON file
        blob_client.upload_blob(photo_json, overwrite=True)
        print(f"Uploaded {blob_name} to {container_name} container in Azure Blob Storage.")

if __name__ == "__main__":
    # Authenticate and build the Google Photos API client
    creds = get_google_photos_credentials()
    photos_service = build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    # Define the time range for the Google Photos metadata
    start_time = datetime.datetime.now() - datetime.timedelta(days=2)
    end_time = datetime.datetime.now()

    # Get the metadata of photos in the specified time range
    photos_metadata = get_photos_metadata(photos_service, start_time, end_time)

    if photos_metadata:
        # Upload the metadata to Azure Blob Storage
        upload_to_azure_blob(photos_metadata)
    else:
        print("No photos found in the specified time range.")