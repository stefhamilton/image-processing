import sys,os
import csv
from datetime import datetime

# Get the absolute path to the parent directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(script_dir, "..")

# Add the absolute path to the modules directory to the Python module search path
sys.path.append(modules_path)
from modules import azure_helper as ah
from modules import google_helper as gph
from modules import image_utils as iu
from modules import paths

def process_time_lapse(DELETE_OLD_GOOG=False):
    GoogIT = gph.GoogleHelper(gph.GoogleHelper.ProfileType.IT)
    days = 1
    limit = None

    # Initialize the CSV file
    csv_file = f"{paths.AZURE_TIME_LAPSE_URLS}/"+ datetime.now().strftime("%Y_%j.txt")
    with open(csv_file, mode='a', newline='') as file:
        fieldnames = ['AZURE_URL',"GOOGLE_ID"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()  # Write the header row

        while True:
            items_list = GoogIT.fetch_media_items(days, limit)
            downloaded_items = GoogIT.download_images(items_list, gph.base_output_directory)

            # Process the items_list as needed
            if not downloaded_items:
                break  # Exit the loop if there are no more pages

            # Upload downloaded_items to Azure Blob Storage and write to CSV file
            for item in downloaded_items:
                local_file_path = item["file_path"]
                extracted_path = local_file_path.split('time_lapse', 1)[-1]
                azure_blob_path = f"stargazerfarmmedia{extracted_path}"
                azure_configuration = '/Users/stefanhamilton/dev/image-processing/azure_blob_wblms_config.ini'
                url = ah.upload_file_to_azure(local_file_path, azure_blob_path, azure_configuration)
                print(f"File '{local_file_path}' uploaded to Azure Blob Storage. URL: {url}")

                # Write the row to the CSV file and flush the buffer
                writer.writerow({'AZURE_URL': url, 'GOOGLE_ID':item['id']})
                file.flush()  # Ensures that the buffer is written to disk
 

    print(f"Data appended to {csv_file}.")
    print(f"Downloaded {len(downloaded_items)} images.")
    print(f"Completed successfully")

if __name__ == '__main__':
    process_time_lapse(DELETE_OLD_GOOG=True)
