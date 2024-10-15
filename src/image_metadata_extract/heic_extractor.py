from pillow_heif import register_heif_opener
from PIL import Image
from src.image_metadata_extract.base_extractor import ImageMetadataExtractor

# Register HEIF opener with Pillow
register_heif_opener()

class HEICMetadataExtractor(ImageMetadataExtractor):
    """Extractor for HEIC image metadata."""

    def extract_metadata(self):
        try:
            image = Image.open(self.image_path)
            exif_data = image.getexif()  # Get EXIF data from HEIC

            if not exif_data:
                print(f"No EXIF data found in {self.image_path}")
                return None

            # Use base class method to extract GPS data
            gps_data = self.extract_gps(exif_data)
            return gps_data
        except Exception as e:
            print(f"Error extracting metadata from {self.image_path}: {e}")
            return None
