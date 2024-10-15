from src.image_metadata_extract.heic_extractor import HEICMetadataExtractor
from src.image_metadata_extract.jpg_extractor import JPEGMetadataExtractor

# Factory function to select the correct extractor based on file extension
def get_metadata_extractor(image_path):
    if image_path.lower().endswith('.heic'):
        return HEICMetadataExtractor(image_path)
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        return JPEGMetadataExtractor(image_path)
    else:
        raise ValueError("Unsupported image format")