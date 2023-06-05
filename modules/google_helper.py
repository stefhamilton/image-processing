from datetime import datetime, timedelta, timezone
import os, json
import requests
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from enum import Enum
from googleapiclient import discovery


base_output_directory = "/Users/stefanhamilton/dev/image-processing/time_lapse"

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

from dateutil.parser import parse


from dateutil.parser import parse





def get_creds():
    client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials_google_admin.json"
    refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token_admin.json"
    SCOPES = [
        "https://www.googleapis.com/auth/photoslibrary.readonly",
    ]
    credentials = get_google_photos_credentials(client_secret_file,refresh_token_file, SCOPES)
    return credentials

def get_photos_service(creds):
    service = build("photoslibrary", "v1", credentials=creds,static_discovery=False)
    return service

from datetime import datetime, timedelta, timezone
from googleapiclient.errors import HttpError
from googleapiclient import discovery
from dateutil.parser import parse

class GoogleHelper:
    class ProfileType(Enum):
        ADMIN = "admin"
        IT = "it"

    def __init__(self, profile_tpe:ProfileType):
        self.photo_service = None
        self.client_secret_file = None
        self.refresh_token_file = None
        self.SCOPES = []
        self.credentials = None
        self.profile_type = None
        self.next_page_token = None
        self.set_profile_type(profile_tpe)

    def set_profile_type(self, profile_type):
        if isinstance(profile_type, self.ProfileType):
            self.profile_type = profile_type
            self.init_profile()
        else:
            raise ValueError("Invalid profile type")

    def init_profile(self):
        if self.profile_type == self.ProfileType.ADMIN:
            self.client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials_google_admin.json"
            self.refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token_admin.json"
        elif self.profile_type == self.ProfileType.IT:
            self.client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials.json"
            self.refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token.json"
        else:
            raise ValueError("Invalid profile type")

        self.SCOPES = [
            "https://www.googleapis.com/auth/photoslibrary.readonly",
        ]
        self.credentials = get_google_photos_credentials(self.client_secret_file, self.refresh_token_file, self.SCOPES)
        self.photo_service = discovery.build("photoslibrary", "v1", credentials=self.credentials, static_discovery=False)

    def fetch_media_items(self, n_days, limit=None):
        target_date = datetime.now(timezone.utc) - timedelta(days=n_days)
        items_list = []

        while True:
            try:
                if self.next_page_token:
                    results = self.photo_service.mediaItems().list(pageSize=100, pageToken=self.next_page_token).execute()
                else:
                    results = self.photo_service.mediaItems().list(pageSize=100).execute()

                items = results.get("mediaItems", [])

                for item in items:
                    creation_time = parse(item["mediaMetadata"]["creationTime"])

                    if creation_time < target_date:
                        items_list.append(item)

                    if limit is not None and len(items_list) >= limit:
                        return items_list

                self.next_page_token = results.get("nextPageToken")
                if not self.next_page_token:
                    break

            except HttpError as error:
                print(f"An error occurred: {error}")
                break

        return items_list
    
    def download_images(self, items_list, base_output_dir):
        downloaded_items = []

        for item in items_list:
            creation_time = parse(item["mediaMetadata"]["creationTime"])

            # Determine the directory to save the image based on its creation time
            year = creation_time.year
            day_of_year = creation_time.timetuple().tm_yday
            hour = creation_time.hour
            output_dir = os.path.join(base_output_dir, str(year), str(day_of_year), str(hour))
            os.makedirs(output_dir, exist_ok=True)

            # Download the image
            image_url = item["baseUrl"]
            response = requests.get(image_url)

            # Save the image to the output directory
            file_name = item["filename"]
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"Downloaded: {file_path}")

            # Append the downloaded image's information to the list
            downloaded_items.append({"id": item["id"], "file_path": file_path})

        return downloaded_items

if __name__ == '__main__':
    days = 1
    limit = 10
    
    google_helper = GoogleHelper(GoogleHelper.ProfileType.IT)
    items_list = google_helper.fetch_media_items(days, limit)
    downloaded_items = google_helper.download_images(items_list, base_output_directory)
    
    print(f"Downloaded {len(downloaded_items)} images.")