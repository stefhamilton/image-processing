import exifread

def extract_gps_exifread(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file, details=False)
        gps_tags = {tag: tags[tag] for tag in tags.keys() if tag.startswith('GPS')}
        
        if gps_tags:
            for tag, value in gps_tags.items():
                print(f"{tag}: {value}")
        else:
            print("No GPS data found.")

# Example usage
image_path = 'tests/data/jpgs/has_gps.jpg'
extract_gps_exifread(image_path)
