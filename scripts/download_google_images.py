import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from google_photo_helper import get_google_photos_credentials

client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials_google_admin.json"
refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token_admin.json"
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",
]
credentials = get_google_photos_credentials(client_secret_file,refresh_token_file, SCOPES)
service = discovery.build("photoslibrary", "v1", credentials=credentials, static_discovery=False)

def download_images_with_gps_info(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch the media items
    next_page_token = None
    while True:
        try:
            results = service.mediaItems().list(pageSize=100, pageToken=next_page_token).execute()
            items = results.get("mediaItems", [])

            for item in items:
                # Check if the image has GPS information
                if "geo" in item:
                    # Download the image
                    image_url = item["baseUrl"]
                    response = requests.get(image_url)

                    # Save the image to the output directory
                    file_name = item["filename"]
                    file_path = os.path.join(output_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(response.content)

                    print(f"Downloaded: {file_path}")

            # Check if there is a next page of results
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break

        except HttpError as error:
            print(f"An error occurred: {error}")
            break

output_directory = "data"
download_images_with_gps_info(output_directory)
