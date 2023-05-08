import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import subprocess
import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fractions import Fraction
import piexif
from azure_helper import upload_file_to_azure
import xml.etree.ElementTree as ET


# Set up the credentials
scopes = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
client_secret_file = "/Users/stefanhamilton/dev/image-processing/scripts/credentials_google_admin.json"
refresh_token_file = "/Users/stefanhamilton/dev/image-processing/scripts/refresh_token_admin.json"

def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
    return flow.run_local_server(port=58242)

# Get the shared album using the share token
def get_shared_album(photos_api, share_token):
    try:
        response = photos_api.sharedAlbums().get(shareToken=share_token).execute()
        return response
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# List media items in the shared album
def list_media_items(photos_api, album_id):
    try:
        response = photos_api.mediaItems().search(body={"albumId": album_id, "pageSize": 100}).execute()
        return response.get("mediaItems", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

# Download media items
import os
import requests
import json

def download_media_items(service, media_items, output_folder):
    for media_item in media_items:
        # Get the download URL and filename
        url = media_item["baseUrl"]
        filename = os.path.join(output_folder, media_item["filename"])

        # Get the metadata for the media item
        metadata = service.mediaItems().get(mediaItemId=media_item["id"]).execute()

        # Get the GPS location data, if available
        if "geoData" in metadata:
            geo_data = metadata["geoData"]
            latitude = geo_data["latitude"]
            longitude = geo_data["longitude"]
            altitude = geo_data.get("altitude", "N/A")
            print(f"GPS data: Lat={latitude}, Lon={longitude}, Alt={altitude}")

        # Get other metadata, if available
        creation_time = metadata.get("creationTime", "N/A")
        mime_type = metadata.get("mimeType", "N/A")
        file_size = metadata.get("fileSize", "N/A")

        # Download the media item
        response = requests.get(url)
        folder = os.path.dirname(filename)
        if response.status_code == 200:
            if not os.path.exists(folder):
                os.makedirs(folder)

            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename} (Type={mime_type}, Size={file_size}, Created={creation_time})")

            # Save the metadata to a JSON file alongside the downloaded image
            metadata_filename = os.path.join(output_folder, f"{media_item['filename']}.json")
            with open(metadata_filename, "w") as f:
                json.dump(metadata, f)
            print(f"Saved metadata: {metadata_filename}")

        else:
            print(f"Failed to download {filename}")




def list_albums(photos_api, is_shared):
    albums = []
    page_token = None

    while True:
        try:
            if is_shared:
                response = photos_api.sharedAlbums().list(pageSize=50, pageToken=page_token).execute()
                albums.extend(response.get("sharedAlbums", []))
            else:
                response = photos_api.albums().list(pageSize=50, pageToken=page_token).execute()
                albums.extend(response.get("albums", []))

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred: {error}")
            break

    return albums


def convert_heic_to_jpg_ffmpeg(heic_file, jpg_file):
    try:
        command = ["ffmpeg", "-y", "-i", heic_file, jpg_file]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {heic_file}: {e}")



def convert_heics_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".heic"):
            heic_path = os.path.join(folder_path, file_name)
            jpeg_path = os.path.join(folder_path, file_name[:-5] + ".jpg")
            convert_heic_to_jpg_ffmpeg(heic_path, jpeg_path)
            print(f"Converted {file_name} to {file_name[:-5]}.jpg")


def update_image_metadata(img_path, json_path, output_folder):
    if os.path.isfile(json_path):
        # Load the JSON file
        with open(json_path, 'r') as f:
            metadata = json.load(f)

        # Load the image
        image = Image.open(img_path)
        exif_data = image.getexif() or {}        

        # Prepare GPS metadata
        gps_data = {}
        if 'geoData' in metadata and metadata['geoData'] is not None:
            gps_data['Latitude'] = metadata['geoData']['latitude']
            gps_data['Longitude'] = metadata['geoData']['longitude']
            gps_data['Altitude'] = metadata['geoData']['altitude']
            gps_data['LatitudeRef'] = 'N' if gps_data['Latitude'] > 0 else 'S'
            gps_data['LongitudeRef'] = 'E' if gps_data['Longitude'] > 0 else 'W'

        # Write metadata to the image
        for key in exif_data:
            if key in TAGS:
                if TAGS[key] == 'GPSInfo':
                    for gps_key in exif_data[key]:
                        if gps_key in GPSTAGS:
                            gps_data[GPSTAGS[gps_key]] = exif_data[key][gps_key]
                else:
                    image.info[TAGS[key]] = exif_data[key]            

        # Save the metadata to the image attributes
        image.info['Title'] = metadata.get('title', '')
        image.info['Description'] = metadata.get('description', '')
        image.info['DateTimeOriginal'] = metadata.get('photoTakenTime', {}).get('formatted', '')
        image.info['GPSInfo'] = gps_data
        image.info['Latitiude']=999

        # Save the updated image with the new metadata
        image.save(os.path.join(output_folder, os.path.basename(img_path)))


def process_folder(folder_path,azure_config):
    # Create the output subfolder if it doesn't exist
    #output_folder = os.path.join(folder_path, 'updated')
    

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            json_filename = os.path.splitext(filename)[0] + '.HEIC.json'
            json_path = os.path.join(folder_path, json_filename)
            azure_path = 'photos-sf-4-23-2023/kml'+ os.path.dirname(filename)
            
            #update_image_metadata(img_path, json_path, output_folder)
            url = upload_file_to_azure(img_path, f"{azure_path}/{filename}",azure_config)
            print(url)

def create_kml_file_with_gps_from_json(folder_path, azure_config, width=400, height=400):
    kml_ns = "http://www.opengis.net/kml/2.2"

    kml = ET.Element("kml", xmlns=kml_ns)
    document = ET.SubElement(kml, "Document")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            # Load GPS coordinates from JSON file
            with open(folder_path + "/" + filename.replace(".jpg", ".HEIC.json"), 'r') as f:
                gps_data = json.load(f)

            img_path = os.path.join(folder_path, filename)
            azure_path = 'photos-sf-4-23-2023/kml' + os.path.dirname(filename)

            url = upload_file_to_azure(img_path, f"{azure_path}/{filename}", azure_config)
            print(url)

            latitude = gps_data['geoData']["latitude"]
            longitude = gps_data['geoData']["longitude"]

            placemark = ET.SubElement(document, "Placemark")
            name = ET.SubElement(placemark, "name")
            name.text = filename
            description = ET.SubElement(placemark, "description")
            description.text = f'<img src="{url}" alt="Image" width="{width}" height="{height}"/>'

            point = ET.SubElement(placemark, "Point")
            coordinates = ET.SubElement(point, "coordinates")
            coordinates.text = f"{longitude},{latitude},0"

    kml_filename = 'all_locations.kml'
    kml_path = os.path.join(folder_path, kml_filename)
    tree = ET.ElementTree(kml)
    tree.write(kml_path, xml_declaration=True, encoding='utf-8', method="xml")

def main():
    params = {"album_title": "Coffee attack by stem borer", "is_shared":False}
    output_folder = f"/Users/stefanhamilton/dev/image-processing/data/{params['album_title']}"
    
    azure_config = '/Users/stefanhamilton/dev/image-processing/azure_blob_wblms_config.ini'
    
    #download_from_google(params['album_title'], output_folder, params['is_shared'])
    
    # Turn on when not debugging
    convert_heics_in_folder(output_folder)
    create_kml_file_with_gps_from_json(output_folder,azure_config)
    #process_folder(output_folder,azure_config)

def download_from_google(album_title, output_folder, is_shared):
    credentials = get_credentials()
    service = build("photoslibrary", "v1", credentials=credentials, static_discovery=False)
    albums = list_albums(service, is_shared)
  
    album_id = None
    for album in albums:
        if album["title"] == album_title:
            album_id = album["id"]
            break

    media_items = list_media_items(service, album_id)
    download_media_items(service, media_items, output_folder)


if __name__ == "__main__":
    main()
