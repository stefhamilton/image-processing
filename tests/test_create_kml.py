import os, sys
from _pytest._py.path import LocalPath
import pytest
from xml.dom.minidom import parseString
# # Get the current file's directory
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_directory = os.path.dirname(os.path.dirname(current_file_path)) 

#Add the parent directory to sys.path
#To Do: Do this correctly
sys.path.append(parent_directory)
from scripts.create_kml import create_kml_file

@pytest.fixture
def sample_placemarks():
    """Fixture that provides sample placemarks for testing."""
    return [
        {
            "latitude": 11.471447,
            "longitude": 122.553253,
            "altitude": 52.84,
            "timestamp": "2024:09:26 08:35:52",
            "make": "Apple",
            "model": "iPhone XS",
            "bearing": 183.60,
            "file_url": "https://example.com/image1.jpg"
        },
        {
            "latitude": 11.472761,
            "longitude": 122.550994,
            "altitude": 119.24,
            "timestamp": "2024:09:27 10:04:00",
            "make": "Apple",
            "model": "iPhone XS",
            "bearing": 26.13,
            "file_url": "https://example.com/image2.jpg"
        }
    ]

def test_create_kml_file(sample_placemarks):
    """Test the create_kml_file function."""
    
    # Temporary directory for output
    output_file = os.path.join('./tests/', "test_output.kml")
    
    # Call the function to create the KML file
    create_kml_file(sample_placemarks, output_file)
    
    # Check if the file is created
    assert os.path.exists(output_file), "KML file was not created."
    
    # Read the KML file contents
    with open(output_file, 'r') as f:
        kml_content = f.read()
    
    # Parse the KML XML structure
    kml_dom = parseString(kml_content)
    
    # Check for the correct structure and elements in the KML file
    placemarks = kml_dom.getElementsByTagName('Placemark')
    assert len(placemarks) == len(sample_placemarks), "Number of placemarks in KML file does not match the input data."

    # Check content of the first placemark
    first_placemark = placemarks[0]
    description = first_placemark.getElementsByTagName('description')[0].firstChild.data
    assert "iPhone XS" in description, "Make/Model not found in KML description."
    assert "https://example.com/image1.jpg" in description, "File URL not found in KML description."

    coordinates = first_placemark.getElementsByTagName('coordinates')[0].firstChild.data
    assert "122.553253,11.471447,52.84" in coordinates, "Coordinates do not match the expected value."

