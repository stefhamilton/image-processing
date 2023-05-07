import os
import json
import datetime
import sys
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import webbrowser
from azure_helper import upload_photo_df_to_azure_blob
import requests


def get_refresh_token(client_secret_file, scopes):
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
    credentials = flow.run_local_server(port=0)
    return credentials.refresh_token

def store_refresh_token(refresh_token, refresh_token_file):
    with open(refresh_token_file, "w") as f:
        json.dump({"refresh_token": refresh_token}, f)

def get_google_photos_credentials(client_secret_file,refresh_token_file, SCOPES):
    creds = None

    if os.path.exists(refresh_token_file):
        print("Getting credentials from refresh token")
        with open(refresh_token_file, "r") as f:
            refresh_token_data = json.load(f)
            refresh_token = refresh_token_data.get("refresh_token")

        if refresh_token:
            with open(client_secret_file, "r") as f:
                client_secret_data = json.load(f)
                try:
                    client_id = client_secret_data["installed"]["client_id"]
                    client_secret = client_secret_data["installed"]["client_secret"]
                except:
                    client_id = client_secret_data["web"]["client_id"]
                    client_secret = client_secret_data["web"]["client_secret"]

            creds = Credentials.from_authorized_user_info(info={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token
            }, scopes=SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token")
            creds.refresh(Request())
            print("token was refreshed")
        else:
            # No refresh token found, prompt the user to get a new one
            print("No valid refresh token found, please generate a new one")

    return creds
# Rest of the code remains the same

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



if __name__ == "__main__":
    try:
        azure_config = '/Users/stefanhamilton/dev/image-processing/config.ini'
        # Authenticate and build the Google Photos API client
        print("Getting google creds")
        client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials.json"
        refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token.json"
        SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/bigquery",
        "openid",
    ]
        creds = get_google_photos_credentials(client_secret_file, refresh_token_file, SCOPES)
        print("creating photos service")
        photos_service = build("photoslibrary", "v1", credentials=creds, static_discovery=False)

        # Define the time range for the Google Photos metadata
        start_time = datetime.datetime.now() - datetime.timedelta(hours=1)
        end_time = datetime.datetime.now()

        # Get the metadata of photos in the specified time range
        print("getting photos metadata")
        photos_metadata = get_photos_metadata(photos_service, start_time, end_time)

        if photos_metadata:
            csv_name = f"{start_time}-{end_time}.csv"
            # Upload the metadata to Azure Blob Storage
            upload_photo_df_to_azure_blob(photos_metadata, csv_name, azure_config)
        else:
            print("No photos found in the specified time range.")
    except Exception as e:
        print(e)
