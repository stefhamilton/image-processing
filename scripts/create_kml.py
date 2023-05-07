import os
import exifread
from svg_pins import create_svg_pin
from azure_helper import upload_file_to_azure
from xml.dom.minidom import Document
from PIL import Image
import exifread
import piexif

# Change these
image_folder = "album/15 cameras Stargazer Farm"
azure_config = '/Users/stefanhamilton/dev/image-processing/azure_blob_wblms_config.ini'

# This corresponds to red, green, blue, transparency with a max of 256
# Use this to select colors https://rgbacolorpicker.com/rgba-to-hex
# To Do: This doesn't work - probably since css isn't fully supported
marker_color = (211, 211, 211) # light gray
marker_color = (173, 216, 230) # light blue
marker_opacity = 0.4 # a low value is transparent

# Do not change these
placemark_prefix = "C"
album_name = os.path.basename(os.path.normpath(image_folder))
azure_folder = f"stargazermedia/{image_folder}/"
output_file = image_folder+f"/{album_name}.kml"

png_path = create_svg_pin(image_folder, marker_color,marker_opacity)
png_url = upload_file_to_azure(png_path, f"{azure_folder}{os.path.basename(png_path)}", azure_config, make_public=True)

def rotate_image_to_orientation(image_path):
    # Open the image and read its EXIF data
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False, stop_tag="EXIF Orientation")

    # Extract the orientation metadata
    orientation = tags.get("Image Orientation", "TopLeft").values[0]

    # Open the image using the PIL library
    image = Image.open(image_path)

    # Rotate the image based on the orientation
    rotation_angle = 0
    if orientation == 3:
        image = image.rotate(180)
        rotation_angle = 180
    elif orientation == 6:
        image = image.rotate(-90)
        rotation_angle = -90
    elif orientation == 8:
        image = image.rotate(90)
        rotation_angle = 90

    # Update the orientation in the EXIF data to "TopLeft" (1)
    exif_dict = piexif.load(image.info['exif'])
    exif_dict['0th'][piexif.ImageIFD.Orientation] = 1
    exif_bytes = piexif.dump(exif_dict)

    # Save the rotated image to the original file path with the updated EXIF data
    image.save(image_path, exif=exif_bytes)

    return image, rotation_angle

def get_gps_data(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)

    gps_data = {}
    for tag, value in tags.items():
        if "GPS" in tag or tag in ["Image Make", "Image Model", "Image DateTime", "Image Orientation"]:
            gps_data[tag] = value

    return gps_data

def parse_fraction(fraction_str):
    num, den = fraction_str.strip("[]").split("/")
    return float(num) / float(den)

def create_placemark_element(doc, placemark_data):
    placemark_element = doc.createElement('Placemark')

    name_element = create_name_element(doc, placemark_data)
    placemark_element.appendChild(name_element)

    description_element = create_description_element(doc, placemark_data)
    placemark_element.appendChild(description_element)

    style_element = create_style_element(doc, placemark_data)
    placemark_element.appendChild(style_element)

    point_element = create_point_element(doc, placemark_data)
    placemark_element.appendChild(point_element)

    return placemark_element


def create_name_element(doc, placemark_data):
    name_element = doc.createElement('name')
    name_text = f"{placemark_prefix}{placemark_data['index']}"
    name_text_node = doc.createTextNode(name_text)
    name_element.appendChild(name_text_node)
    return name_element

def create_description_element(doc, placemark_data):
    description_element = doc.createElement('description')
    description_text = f'''
    
    <b>Timestamp:</b> {placemark_data['timestamp']}<br>
    <b>Model:</b> {placemark_data['model']}<br>
    <b>Bearing:</b> {round(placemark_data['bearing'], 1)}<br>
    <a href="{placemark_data['file_url']}">Image URL</a><br>

    <img src="{placemark_data['file_url']}" alt="Image" width="300" /><br>
    '''
    description_text_node = doc.createCDATASection(description_text)
    description_element.appendChild(description_text_node)
    return description_element


def create_style_element(doc, placemark_data):
    style_element = doc.createElement("Style")

    icon_style_element = create_icon_style_element(doc, placemark_data)
    style_element.appendChild(icon_style_element)

    return style_element


def create_icon_style_element(doc, placemark_data):
    icon_style_element = doc.createElement("IconStyle")

    icon_element = create_icon_element(doc)
    icon_style_element.appendChild(icon_element)

    hotspot_element = create_hotspot_element(doc)
    icon_style_element.appendChild(hotspot_element)

    heading_element = create_heading_element(doc, placemark_data)
    icon_style_element.appendChild(heading_element)

    return icon_style_element


def create_icon_element(doc):
    icon_element = doc.createElement("Icon")

    href_element = doc.createElement("href")
    href_text_node = doc.createTextNode(png_url)  
    href_element.appendChild(href_text_node)
    icon_element.appendChild(href_element)



    return icon_element


def create_hotspot_element(doc):
    hotspot_element = doc.createElement("hotSpot")
    hotspot_element.setAttribute("x", "0.5")
    hotspot_element.setAttribute("y", "1")
    hotspot_element.setAttribute("xunits", "fraction")
    hotspot_element.setAttribute("yunits", "fraction")
    return hotspot_element


def create_heading_element(doc, placemark_data):
    heading_element = doc.createElement("heading")
    rotation_angle = placemark_data['bearing']
    heading_text_node = doc.createTextNode(str(rotation_angle))
    heading_element.appendChild(heading_text_node)
    return heading_element


def create_point_element(doc, placemark_data):
    point_element = doc.createElement('Point')

    coordinates_element = doc.createElement('coordinates')
    coordinates_text = f"{placemark_data['longitude']},{placemark_data['latitude']},{placemark_data['altitude']}"
    coordinates_text_node = doc.createTextNode(coordinates_text)
    coordinates_element.appendChild(coordinates_text_node)
    point_element.appendChild(coordinates_element)

    return point_element


def create_kml_file(placemarks, output_file):
    doc = Document()

    kml_element = doc.createElement('kml')
    kml_element.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    doc.appendChild(kml_element)

    document_element = doc.createElement('Document')
    kml_element.appendChild(document_element)

    for i, placemark_data in enumerate(placemarks):
        placemark_data['index'] = i
        placemark_element = create_placemark_element(doc, placemark_data)
        document_element.appendChild(placemark_element)

    with open(output_file, 'w') as f:
        f.write(doc.toprettyxml(indent='  '))

placemarks = []

for file in os.listdir(image_folder):

    if file.lower().endswith(".jpg"):
        image, rotation_angle = rotate_image_to_orientation(image_folder+'/'+file)

        image_path = os.path.join(image_folder, file)
        gps_data = get_gps_data(image_path)

        if "GPS GPSLatitude" in gps_data and "GPS GPSLongitude" in gps_data:
            latitude = float(gps_data["GPS GPSLatitude"].values[0]) + float(gps_data["GPS GPSLatitude"].values[1])/60 + float(gps_data["GPS GPSLatitude"].values[2].num)/gps_data["GPS GPSLatitude"].values[2].den/3600
            longitude = float(gps_data["GPS GPSLongitude"].values[0]) + float(gps_data["GPS GPSLongitude"].values[1])/60 + float(gps_data["GPS GPSLongitude"].values[2].num)/gps_data["GPS GPSLongitude"].values[2].den/3600
            altitude = parse_fraction(str(gps_data.get("GPS GPSAltitude", "0/1")))
            timestamp = str(gps_data.get("Image DateTime", ""))
            make = str(gps_data.get("Image Make", ""))
            model = str(gps_data.get("Image Model", ""))
            bearing = (float(gps_data["GPS GPSImgDirection"].values[0].num) / gps_data["GPS GPSImgDirection"].values[0].den + rotation_angle) % 360 if "GPS GPSImgDirection" in gps_data else 0

            img_url = upload_file_to_azure(image_path, f"{azure_folder}{file}", azure_config, make_public=True)
            print(f"Uploaded {file} to Azure Blob Storage: {img_url}")

            placemarks.append({
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "timestamp": timestamp,
                "make": make,
                "model": model,
                "bearing": bearing,
                "file_url": img_url,
            })

if __name__ == "__main__":
    create_kml_file(placemarks, output_file)
    print(f"file saved to {output_file}")