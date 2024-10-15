from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import json

class ImageMetadata:
    """Class to represent GPS metadata and general image metadata."""

    """Class to hold metadata for an image, including GPS and camera details."""
    
    def __init__(self, latitude=None, longitude=None, altitude=None, timestamp=None,
                 date_stamp=None, processing_method=None, direction=None,
                 camera_make=None, camera_model=None, datetime_original=None):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timestamp = timestamp
        self.date_stamp = date_stamp
        self.processing_method = processing_method
        self.direction = direction
        self.camera_make = camera_make
        self.camera_model = camera_model
        self.datetime_original = datetime_original

    def to_dict(self):
        """Convert the metadata to a dictionary."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "timestamp": self.timestamp,
            "date_stamp": self.date_stamp,
            "processing_method": self.processing_method,
            "direction": self.direction,
            "camera_make": self.camera_make,
            "camera_model": self.camera_model,
            "datetime_original": self.datetime_original
        }

    def to_json_file(self, json_path):
        """Save the metadata to a JSON file."""
        try:
            with open(json_path, 'w') as json_file:
                json.dump(self.to_dict(), json_file, indent=4)
            print(f"Metadata saved to {json_path}")
        except Exception as e:
            print(f"Error saving metadata to {json_path}: {e}")
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
    @classmethod
    def from_exif(cls, exif_data):
        """Load GPS and other image data from EXIF data and return a GPSData instance."""
        if not exif_data:
            return None

        # Extract standard metadata fields
        camera_make = exif_data.get(271)  # Make
        camera_model = exif_data.get(272)  # Model
        datetime_original = exif_data.get(36867)  # DateTimeOriginal

        # Extract GPS metadata fields
        gps_info = {}
        gps_data = exif_data.get_ifd(34853)  # GPSInfo IFD tag
        if gps_data:
            for key, value in gps_data.items():
                sub_decoded = GPSTAGS.get(key, key)
                gps_info[sub_decoded] = value

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
                lat_degrees, lat_minutes, lat_seconds = [float(v) for v in gps_latitude]
                lon_degrees, lon_minutes, lon_seconds = [float(v) for v in gps_longitude]

                latitude = lat_degrees + (lat_minutes / 60.0) + (lat_seconds / 3600.0)
                if gps_latitude_ref == 'S':
                    latitude = -latitude

                longitude = lon_degrees + (lon_minutes / 60.0) + (lon_seconds / 3600.0)
                if gps_longitude_ref == 'W':
                    longitude = -longitude

                # Convert altitude, if available
                altitude = float(gps_altitude) if gps_altitude else None
                if gps_altitude_ref and gps_altitude_ref == 1:  # 1 indicates altitude below sea level
                    altitude = -altitude if altitude is not None else None

                # Convert GPS timestamp, if available
                timestamp = None
                if gps_timestamp:
                    hours, minutes, seconds = gps_timestamp
                    timestamp = f"{int(hours):02}:{int(minutes):02}:{float(seconds):05.2f}"

                # Convert GPS processing method, if available
                processing_method = None
                if isinstance(gps_processing_method, bytes):
                    processing_method = gps_processing_method.decode('utf-8', 'ignore')
                elif gps_processing_method:
                    processing_method = gps_processing_method

                # Convert GPS direction, if available
                direction = float(gps_direction) if gps_direction else None

                return cls(
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    timestamp=timestamp,
                    date_stamp=gps_date_stamp,
                    processing_method=processing_method,
                    camera_make=camera_make,
                    camera_model=camera_model,
                    datetime_original=datetime_original,
                    direction=direction
                )
        return None

    def to_json_file(self, json_file_path):
        """Save the GPS data to a JSON file."""
        try:
            # Prepare the data as a dictionary
            data = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude,
                "timestamp": self.timestamp,
                "date_stamp": self.date_stamp,
                "processing_method": self.processing_method,
                "camera_make": self.camera_make,
                "camera_model": self.camera_model,
                "datetime_original": self.datetime_original,
                "direction": self.direction,
            }

            # Save data as JSON
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Saved GPS data to {json_file_path}")
        except Exception as e:
            print(f"Error saving GPS data to {json_file_path}: {e}")

    def __repr__(self):
        return (
            f"GPSData(latitude={self.latitude}, longitude={self.longitude}, altitude={self.altitude}, "
            f"timestamp={self.timestamp}, date_stamp={self.date_stamp}, processing_method={self.processing_method}, "
            f"camera_make={self.camera_make}, camera_model={self.camera_model}, datetime_original={self.datetime_original}, "
            f"direction={self.direction})"
        )


    # def extract_metadata(image_path):
    #     """Extract metadata from an image, including GPS data."""
    #     try:
    #         image = Image.open(image_path)
    #         exif_data = image.getexif()

    #         if not exif_data:
    #             print(f"No EXIF data found in {image_path}")
    #             return

    #         # Extract metadata
    #         gps_data = ImageMetadata.from_exif(exif_data)

    #         if gps_data:
    #             # Save GPS and other metadata to JSON file
    #             json_file_path = image_path.rsplit('.', 1)[0] + ".json"
    #             gps_data.to_json_file(json_file_path)

    #     except Exception as e:
    #         print(f"Error extracting metadata from {image_path}: {e}")


    def clean_processing_method(self, processing_method):
        """Clean the processing method to remove unnecessary characters."""
        if processing_method and isinstance(processing_method, str):
            # Remove null characters and strip whitespace
            cleaned = processing_method.replace('\x00', '').strip()
            # If the cleaned method is empty, set it to None
            return cleaned if cleaned else None
        return None
