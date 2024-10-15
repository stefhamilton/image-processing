from PIL import Image
from src.image_metadata_extract.base_extractor import ImageMetadataExtractor

class JPEGMetadataExtractor(ImageMetadataExtractor):
    """Extractor for JPEG image metadata."""

    def extract_metadata(self):
        try:
            image = Image.open(self.image_path)
            exif_data = image._getexif()  # Get EXIF data from JPEG

            if not exif_data:
                print(f"No EXIF data found in {self.image_path}")
                return None

            # Use base class method to extract GPS data
            image_meta = self.extract_gps(exif_data)
            return image_meta
        except Exception as e:
            print(f"Error extracting metadata from {self.image_path}: {e}")
            return None
