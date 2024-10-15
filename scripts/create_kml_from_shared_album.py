import os
import requests

import os

import json
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fractions import Fraction
import piexif
from scripts.azure_helper import upload_file_to_azure
from scripts.file_utils import convert_heics_in_folder
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from src.extract_metadata_orchestrator import extract_metadata
from src.image_metadata import ImageMetadata

# Load environment variables from .env file
load_dotenv()


# Set up the credentials
client_secret_file = "credentials/client_secret.json"
refresh_token_file = "credentials/refresh_token_admin.json"





# def update_image_metadata(img_path, json_path, output_folder):
#     if not os.path.exists(json_path):
#         print(f"No JSON file found at {json_path}. Skipping")
#         return
    
#     if os.path.isfile(json_path):
#         # Load the JSON file
#         with open(json_path, 'r') as f:
#             metadata = json.load(f)

#         # Load the image
#         image = Image.open(img_path)
#         exif_data = image.getexif() or {}        

#         # Prepare GPS metadata
#         gps_data = {}
#         if 'geoData' in metadata and metadata['geoData'] is not None:
#             gps_data['Latitude'] = metadata['geoData']['latitude']
#             gps_data['Longitude'] = metadata['geoData']['longitude']
#             gps_data['Altitude'] = metadata['geoData']['altitude']
#             gps_data['LatitudeRef'] = 'N' if gps_data['Latitude'] > 0 else 'S'
#             gps_data['LongitudeRef'] = 'E' if gps_data['Longitude'] > 0 else 'W'

#         # Write metadata to the image
#         for key in exif_data:
#             if key in TAGS:
#                 if TAGS[key] == 'GPSInfo':
#                     for gps_key in exif_data[key]:
#                         if gps_key in GPSTAGS:
#                             gps_data[GPSTAGS[gps_key]] = exif_data[key][gps_key]
#                 else:
#                     image.info[TAGS[key]] = exif_data[key]            

#         # Save the metadata to the image attributes
#         image.info['Title'] = metadata.get('title', '')
#         image.info['Description'] = metadata.get('description', '')
#         image.info['DateTimeOriginal'] = metadata.get('photoTakenTime', {}).get('formatted', '')
#         image.info['GPSInfo'] = gps_data
#         image.info['Latitiude']=999

#         # Save the updated image with the new metadata
#         image.save(os.path.join(output_folder, os.path.basename(img_path)))



def upload_json_and_images(folder_path, azure_config):
    # Create the output subfolder if it doesn't exist
    output_folder = os.path.join(folder_path, '')

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            img_path = os.path.join(folder_path, filename)
            json_filename = os.path.splitext(filename)[0] + '.json'
            # if file does not exist, print a message and skip
            if not os.path.exists(os.path.join(folder_path, json_filename)):
                print(f"No JSON file found for {filename}. Skipping")
                continue
            json_path = os.path.join(folder_path, json_filename)
            
            # Get the last folder name from folder_path
            last_folder = os.path.basename(os.path.normpath(folder_path))

            azure_path = 'kml-images/data/'+ last_folder + os.path.dirname(filename)
            
            url = upload_file_to_azure(img_path, f"{azure_path}/{filename}",azure_config)

            print(url)
            return azure_path

def create_kml_file_with_gps_from_json(folder_path, azure_config, width=400, height=400):
    kml_ns = "http://www.opengis.net/kml/2.2"

    kml = ET.Element("kml", xmlns=kml_ns)
    document = ET.SubElement(kml, "Document")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            # Load GPS coordinates from JSON file using GPSData class
            try:
                json_file_path = os.path.join(folder_path, filename.replace(".jpg", ".json"))
                with open(json_file_path, 'r') as f:
                    gps_data_json = json.load(f)
                    gps_data = ImageMetadata.from_json(gps_data_json)
            except (FileNotFoundError, ValueError, KeyError) as e:
                print(f"GPS data is missing or invalid for file {filename}: {e}")
                continue

            # Skip if GPS data is missing
            if not gps_data.latitude or not gps_data.longitude:
                print(f"Skipping {filename} due to missing GPS coordinates.")
                continue

            img_path = os.path.join(folder_path, filename)
            azure_path = 'kml-images/kmls/' + img_path.replace(" ", "-").replace("data/", "")

            # Upload image to Azure and get the URL
            url = upload_file_to_azure(img_path, f"{azure_path}", azure_config)

            # Create KML Placemark entry
            placemark = ET.SubElement(document, "Placemark")
            name = ET.SubElement(placemark, "name")
            name.text = filename

            description = ET.SubElement(placemark, "description")
            description.text = f"<![CDATA[<img src=\"{url}\" alt=\"Image\" width=\"{width}\" height=\"{height}\"/>]]>"

            point = ET.SubElement(placemark, "Point")
            coordinates = ET.SubElement(point, "coordinates")
            coordinates.text = f"{gps_data.longitude},{gps_data.latitude},0"

    # Save the KML file
    kml_tree = ET.ElementTree(kml)
    kml_file_path = os.path.join(folder_path, "output.kml")
    kml_tree.write(kml_file_path, xml_declaration=True, encoding='utf-8')

    print(f"KML file created: {kml_file_path}")
    
    @classmethod
    def from_json(cls, json_data):
        """Create an ImageMetadata instance from a JSON dictionary."""
        return cls(
            latitude=json_data.get("latitude"),
            longitude=json_data.get("longitude"),
            altitude=json_data.get("altitude"),
            timestamp=json_data.get("timestamp"),
            date_stamp=json_data.get("date_stamp"),
            processing_method=json_data.get("processing_method"),
            direction=json_data.get("direction"),
            camera_make=json_data.get("camera_make"),
            camera_model=json_data.get("camera_model"),
            datetime_original=json_data.get("datetime_original")
        )

def main(image_folder):
    
    azure_config = os.getenv("AZURE_CONFIG_FILE")
    
    #download_from_google(params['album_title'], output_folder, params['is_shared'])
    extract_metadata(image_folder)

    # Turn on when not debugging
    upload_json_and_images(image_folder, azure_config)
    #convert_heics_in_folder(image_folder)
    create_kml_file_with_gps_from_json(image_folder, azure_config)

if __name__ == "__main__":
    image_folder = "data/plant-inspections"
    #image_folder = "tests/data/jpgs"
    main(image_folder)
