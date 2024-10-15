import os
import json
from PIL import Image
import subprocess
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS, GPSTAGS

# Register HEIF opener with Pillow
register_heif_opener()
def convert_ifdrational_to_float(value):
    """Converts IFDRational objects to float, or returns the value directly if not IFDRational."""
    if isinstance(value, tuple):
        return [convert_ifdrational_to_float(v) for v in value]
    elif isinstance(value, Image.IFDRational):
        return float(value.numerator) / float(value.denominator)
    return value

def convert_heic_to_jpg_ffmpeg(heic_file, jpg_file):
    try:
        command = ["ffmpeg", "-y", "-i", heic_file, "-map_metadata", "0", jpg_file]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error processing {heic_file}: {e}")

def convert_heics_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".heic") or file_name.lower().endswith(".jpg"):
            heic_path = os.path.join(folder_path, file_name)
            jpeg_path = os.path.join(folder_path, file_name + ".jpg")
            convert_heic_to_jpg_ffmpeg(heic_path, jpeg_path)
            print(f"Converted {file_name} to {file_name}.jpg")
            try:
                meta = extract_meta_from_heic(heic_path)
                if meta:
                    json_path = os.path.join(folder_path, file_name+ ".json")
                    with open(json_path, 'w') as json_file:
                        json.dump(meta, json_file, indent=4)
                    print(f"Saved metadata to {json_path}")
            except Exception as e:
                print(f"Error extracting metadata from {heic_path}: {e}")

def extract_meta_from_heic(image_path):
    """Extract metadata (including GPS) from a HEIC image using Pillow-Heif."""
    
    try:
        # Open the HEIC image using Pillow-Heif
        image = Image.open(image_path)
        exif_data = image.getexif()
        
        if not exif_data:
            print(f"No EXIF data found in {image_path}")
            return None
        
        gps_info = extract_gps_info(exif_data)
        simple_meta_data = extract_simple_metadata(exif_data)
        #gps_info = {key: convert_ifdrational_to_float(value) for key, value in gps_info.items()}

        if gps_info:
            meta_data = {**gps_info, **simple_meta_data}
            print(f"Metadata extracted from {image_path}")
            return meta_data
        else:
            print(f"No GPS data found in {image_path}")
            return simple_meta_data
    except Exception as e:
        print(f"Error extracting metadata from {image_path}: {e}")
        return None

def extract_gps_info(exif_data):
    """Extract GPS info from EXIF data."""
    gps_info = {}
    gps_data = exif_data.get_ifd(34853)  # GPSInfo IFD tag
    
    if gps_data:
        for key, value in gps_data.items():
            decoded_key = GPSTAGS.get(key, key)
            gps_info[decoded_key] = value

        gps_latitude = gps_info.get('GPSLatitude')
        gps_latitude_ref = gps_info.get('GPSLatitudeRef')
        gps_longitude = gps_info.get('GPSLongitude')
        gps_longitude_ref = gps_info.get('GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            # Fix: Access the numerator and denominator of IFDRational objects directly
            lat_degrees = gps_latitude[0].numerator / gps_latitude[0].denominator
            lat_minutes = gps_latitude[1].numerator / gps_latitude[1].denominator
            lat_seconds = gps_latitude[2].numerator / gps_latitude[2].denominator

            lon_degrees = gps_longitude[0].numerator / gps_longitude[0].denominator
            lon_minutes = gps_longitude[1].numerator / gps_longitude[1].denominator
            lon_seconds = gps_longitude[2].numerator / gps_longitude[2].denominator

            latitude = convert_gps_to_decimal(lat_degrees, lat_minutes, lat_seconds, gps_latitude_ref)
            longitude = convert_gps_to_decimal(lon_degrees, lon_minutes, lon_seconds, gps_longitude_ref)

            return {
                "geoData": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "altitude": float(gps_info.get('GPSAltitude', 0)),
                    "direction": float(gps_info.get('GPSImgDirection', None)),

                }
            }
    return None

def extract_simple_metadata(exif_data):
    """Extract simple metadata (Make, Model, DateTime) from EXIF data."""
    simple_meta = {}
    
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name in ['Make', 'Model', 'DateTime']:
            val = value.decode('utf-8') if isinstance(value, bytes) else value
            simple_meta[tag_name] = str(val)

    return simple_meta

def convert_gps_to_decimal(degrees, minutes, seconds, direction):
    """Convert GPS coordinates to decimal format."""
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W']:
        decimal_degrees *= -1
    return decimal_degrees

def extract_gps_info_jpg(exif_data):
    """Extract GPS info from JPEG EXIF data."""
    gps_info = {}
    
    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for key in value:
                sub_decoded = GPSTAGS.get(key, key)
                gps_info[sub_decoded] = value[key]

            gps_latitude = gps_info.get('GPSLatitude')
            gps_latitude_ref = gps_info.get('GPSLatitudeRef')
            gps_longitude = gps_info.get('GPSLongitude')
            gps_longitude_ref = gps_info.get('GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat_degrees = gps_latitude[0]
                lat_minutes = gps_latitude[1]
                lat_seconds = gps_latitude[2]

                lon_degrees = gps_longitude[0]
                lon_minutes = gps_longitude[1]
                lon_seconds = gps_longitude[2]

                latitude = convert_gps_to_decimal(lat_degrees, lat_minutes, lat_seconds, gps_latitude_ref)
                longitude = convert_gps_to_decimal(lon_degrees, lon_minutes, lon_seconds, gps_longitude_ref)

                return {
                    "geoData": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "altitude": float(gps_info.get('GPSAltitude', 0)),
                        "direction": float(gps_info.get('GPSImgDirection', 0)),
                    }
                }
    return None

def extract_meta_from_jpg(image_path):
    """Extract metadata (including GPS) from a JPEG image."""
    try:
        # Open the image
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            print(f"No EXIF data found in {image_path}")
            return None

        gps_info = extract_gps_info_jpg(exif_data)
        if gps_info:
            print(f"Extracted GPS Info: {gps_info}")
            return gps_info
        else:
            print(f"No GPS data found in {image_path}")
            return None
    except Exception as e:
        print(f"Error extracting metadata from {image_path}: {e}")
        return None
    
def extract_metadata(image_path):
    if image_path.lower().endswith('.heic'):
        return extract_meta_from_heic(image_path)
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        return extract_meta_from_jpg(image_path)
    else:
        print("Unsupported format")
        return None
