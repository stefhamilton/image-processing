import sys,os
# Get the absolute path to the parent directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(script_dir, "..")

# Add the absolute path to the modules directory to the Python module search path
sys.path.append(modules_path)

from modules import google_helper as gph
from modules import image_utils as iu

def process_time_lapse():
    GoogIT = gph.GoogleHelper(gph.GoogleHelper.ProfileType.IT)
    days = 1
    limit = 10
    next_page_token = None
    while True:
        items_list = GoogIT.fetch_media_items(days, limit)
        downloaded_items = gph.download_images(GoogIT.photo_service, items_list, gph.base_output_directory)

        # Process the items_list as needed
        if not downloaded_items:
            break  # Exit the loop if there are no more pages

    print(f"Downloaded {len(downloaded_items)} images.")
    print(f"Completed successfully")


if __name__ == '__main__':
    process_time_lapse()