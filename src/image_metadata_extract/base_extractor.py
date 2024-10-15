# src/image_metadata/base_extractor.py

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from src.image_metadata import ImageMetadata

class ImageMetadataExtractor:
    """Base class for extracting image metadata."""

    def __init__(self, image_path):
        self.image_path = image_path

    def extract_metadata(self):
        """Extract metadata. To be implemented by subclasses."""
        raise NotImplementedError

    def extract_common_metadata(self, exif_data):
        """Extract common metadata like camera make, model, and datetime original."""
        camera_make = exif_data.get(271)  # Camera Make (TAGS.get(271) -> 'Make')
        camera_model = exif_data.get(272)  # Camera Model (TAGS.get(272) -> 'Model')
        datetime_original = exif_data.get(36867)  # DateTime Original (TAGS.get(36867) -> 'DateTimeOriginal')

        return camera_make, camera_model, datetime_original

    def extract_gps(self, exif_data):
        """Extract GPS data from EXIF."""
        gps_info = {}

        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                print(f"GPSInfo found: {value}")
                for key in value:
                    sub_decoded = GPSTAGS.get(key, key)
                    gps_info[sub_decoded] = value[key]

                gps_latitude = gps_info.get('GPSLatitude')
                gps_latitude_ref = gps_info.get('GPSLatitudeRef')
                gps_longitude = gps_info.get('GPSLongitude')
                gps_longitude_ref = gps_info.get('GPSLongitudeRef')
                gps_altitude = gps_info.get('GPSAltitude')
                gps_altitude_ref = gps_info.get('GPSAltitudeRef')
                gps_timestamp = gps_info.get('GPSTimeStamp')
                gps_date_stamp = gps_info.get('GPSDateStamp')
                gps_processing_method = gps_info.get('GPSProcessingMethod')
                gps_direction = gps_info.get('GPSImgDirection')

                if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                    # Convert latitude and longitude to decimal format
                    lat_degrees, lat_minutes, lat_seconds = gps_latitude
                    lon_degrees, lon_minutes, lon_seconds = gps_longitude

                    latitude = self.convert_gps_to_decimal(lat_degrees, lat_minutes, lat_seconds, gps_latitude_ref)
                    longitude = self.convert_gps_to_decimal(lon_degrees, lon_minutes, lon_seconds, gps_longitude_ref)

                    # Convert altitude, if available
                    altitude = float(gps_altitude) if gps_altitude else None
                    if gps_altitude_ref and gps_altitude_ref == 1:  # 1 indicates altitude below sea level
                        altitude = -altitude if altitude is not None else None

                    # Convert GPS timestamp, if available
                    timestamp = None
                    if gps_timestamp:
                        hours, minutes, seconds = gps_timestamp
                        timestamp = f"{int(hours):02}:{int(minutes):02}:{float(seconds):05.2f}"

                    # Clean up GPS processing method
                    processing_method = None
                    if isinstance(gps_processing_method, bytes):
                        processing_method = gps_processing_method.decode('utf-8', 'ignore').replace('\x00', '').replace("ASCII", "").strip()
                    elif gps_processing_method:
                        processing_method = gps_processing_method

                    # Convert GPS direction, if available
                    direction = float(gps_direction) if gps_direction else None

                    camera_make, camera_model, datetime_original = self.extract_common_metadata(exif_data)

                    # Return populated ImageMetadata instance
                    return ImageMetadata(
                        latitude=latitude,
                        longitude=longitude,
                        altitude=altitude,
                        timestamp=timestamp,
                        date_stamp=gps_date_stamp,
                        processing_method=processing_method,
                        direction=direction,
                        camera_make=camera_make,
                        camera_model=camera_model,
                        datetime_original=datetime_original
                    )

        return None

    @staticmethod
    def convert_gps_to_decimal(degrees, minutes, seconds, direction):
        """Convert GPS coordinates to decimal format."""
        decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return decimal_degrees
