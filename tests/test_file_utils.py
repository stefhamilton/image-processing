import os,sys
import pytest
import json
from PIL import Image
# # Get the current file's directory
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_directory = os.path.dirname(os.path.dirname(current_file_path)) 

#Add the parent directory to sys.path
#To Do: Do this correctly
sys.path.append(parent_directory)
from scripts.file_utils import extract_meta_from_heic
from scripts.file_utils import convert_heics_in_folder
from scripts.file_utils import extract_meta_from_jpg

# Test folder and image setup
TEST_FOLDER = "./tests/data"
TEST_IMAGE = "test.jpg"

TEST_IMAGE_PATH = os.path.join(TEST_FOLDER, TEST_IMAGE)
TEST_JSON_PATH = TEST_IMAGE_PATH.replace(".jpg", ".HEIC.json")
TEST_KML_PATH = os.path.join(TEST_FOLDER, "all_locations.kml")


def test_extract_gps_from_heic():
    """Test that GPS data is correctly extracted and saved to a JSON file."""
    # Run the GPS extraction
    TEST_HEIC = "tests/data/IMG_5585.HEIC"
    meta_data= extract_meta_from_heic(TEST_HEIC)
    
    # Check that GPS data was successfully extracted
    assert meta_data is not None, "GPS data should not be None"
    assert "geoData" in meta_data, "GPS data should have a 'geoData' key"
    assert "latitude" in meta_data["geoData"], "GPS data should contain latitude"
    assert "longitude" in meta_data["geoData"], "GPS data should contain longitude"

def test_extract_meta_from_jpg():
    """Test that GPS data is correctly extracted and saved to a JSON file."""
    # Run the GPS extraction
    TEST_JPG = "tests/data/jpgs/has_gps.jpg"
    meta_data = extract_meta_from_jpg(TEST_JPG)
    
    # Check that GPS data was successfully extracted
    assert meta_data is not None, "GPS data should not be None"
    assert "geoData" in meta_data, "GPS data should have a 'geoData' key"
    assert "latitude" in meta_data["geoData"], "GPS data should contain latitude"
    assert "longitude" in meta_data["geoData"], "GPS data should contain longitude"


def test_convert_heics_in_folder():
    """Test that HEIC files are converted to JPEG in a folder."""
    # Convert HEIC files in the test folder
    TEST_FOLDER = "./data/Stargazer Farm Produce for Guests to Find/"
    TEST_META_PATH = "./data/Stargazer Farm Produce for Guests to Find/IMG_5107.HEIC.json"
    TEST_IMAGE_PATH = "./data/Stargazer Farm Produce for Guests to Find/IMG_5107.jpg"
    convert_heics_in_folder(TEST_FOLDER)
    
    # Check that the converted JPEG file exists
    assert os.path.exists(TEST_META_PATH), "Converted JSON file should exist"
    assert os.path.exists(TEST_IMAGE_PATH), "Converted JPEG file should exist"
