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
def upload_to_azure_blob(photos_metadata, csv_name):
    import pandas as pd
    from azure.storage.blob import BlobServiceClient, BlobClient

    # Read the Azure connection string from the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    connection_string = config.get('DEFAULT', 'azure_connection_string')

    # Initialize the BlobServiceClient with your connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Set the name of the Blob storage container and the CSV file name
    container_name = "photos-metadata2"

    # Get a reference to the container client
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it does not exist
    if not container_client.exists():
        container_client.create_container()

    # Remove unwanted attributes from photos_metadata
    for photo in photos_metadata:
        del photo['productUrl']
        del photo['baseUrl']
        del photo['mimeType']
        del photo['mediaMetadata']['photo']
        del photo['filename']

    # Convert the JSON data to a Pandas DataFrame
    df = pd.json_normalize(photos_metadata)

    # Split the DataFrame into chunks of 100 rows each
    chunks = [df[i:i+100] for i in range(0, len(df), 100)]


    # Loop through the chunks and upload each one to Azure Blob Storage
    for i, chunk in enumerate(chunks):
        # Construct the file name for this chunk
        chunk_name = f"{csv_name.replace('.csv','')}_{i}.csv"

        # Convert the chunk to CSV and encode as bytes
        chunk_csv = chunk.to_csv(index=False).encode()

        # Upload the chunk to Azure Blob Storage
        blob_client = container_client.get_blob_client(chunk_name)
        blob_client.upload_blob(chunk_csv, overwrite=True)

        # Print a message indicating that the chunk was uploaded
        print(f"Uploaded {chunk_name} to {container_name} container in Azure Blob Storage.")

    # Print a message indicating that all chunks were uploaded
    print(f"All chunks of {csv_name} have been uploaded to {container_name} container in Azure Blob Storage.")


if __name__ == "__main__":
    # Authenticate and build the Google Photos API client
    creds = get_google_photos_credentials()
    photos_service = build("photoslibrary", "v1", credentials=creds, static_discovery=False)

    # Define the time range for the Google Photos metadata
    start_time = datetime.datetime.now() - datetime.timedelta(days=14)
    end_time = datetime.datetime.now()

    # Get the metadata of photos in the specified time range
    photos_metadata = get_photos_metadata(photos_service, start_time, end_time)

    if photos_metadata:
        csv_name = f"{start_time}-{end_time}.csv"
        # Upload the metadata to Azure Blob Storage
        upload_to_azure_blob(photos_metadata,csv_name)
    else:
        print("No photos found in the specified time range.")