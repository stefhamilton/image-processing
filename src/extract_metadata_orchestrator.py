import os
import json
from src.image_metadata_extract.extractor_factory import get_metadata_extractor

def extract_metadata(folder_path):
    """Processes all images (HEIC and JPEG) in the folder, extracting metadata."""
    for file_name in os.listdir(folder_path):
        image_path = os.path.join(folder_path, file_name)
        if file_name.lower().endswith(".heic") or file_name.lower().endswith(".jpg"):
            try:
                extractor = get_metadata_extractor(image_path)

                # If it's a HEIC file, convert to JPEG
                if file_name.lower().endswith(".heic"):
                    jpg_path = os.path.join(folder_path, file_name + ".jpg")
                    extractor.convert_to_jpg(jpg_path)
                    print(f"Converted {file_name} to {file_name}.jpg")
                
                # Extract metadata
                meta = extractor.extract_metadata()

                if meta:
                    json_path = os.path.join(folder_path, file_name.replace("jpg","json"))
                    meta.to_json_file(json_path)

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
