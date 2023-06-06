import sys
import os
import re
from datetime import datetime
# Get the absolute path to the parent directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(script_dir, "..")

# Add the absolute path to the modules directory to the Python module search path
sys.path.append(modules_path)
from modules import azure_helper as ah
from modules import paths

def upload_takeout(folder):
    # Filter function to check if the file was taken between 6am and 6pm
    def is_within_time_range(file_name):
        # Extract the timestamp from the file name
        timestamp = file_name.split("_", 1)[1].split(".")[0]

        # Define the regular expression pattern for matching the timestamp
        pattern = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})(\(\d+\))?"

        # Match the pattern in the timestamp
        match = re.match(pattern, timestamp)

        if match:
            # Extract the date and time components from the matched groups
            date_time_str = match.group(1)
            day_str = match.group(2)

            # Convert the date and time components to datetime objects
            date_time = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
            if day_str:
                day = int(day_str.strip("()"))
                date_time = date_time.replace(day=day)
        else:
            return False

        # Check if the time is between 6am and 6pm
        return date_time.hour >= 6 and date_time.hour < 18

    output_file = "upload_results.txt"  # Specify the output file name

    with open(output_file, mode='w') as file:
        for root, _, files in os.walk(folder):
            for file_name in files:
                if file_name.lower().endswith(".jpg") and is_within_time_range(file_name):
                    local_file_path = os.path.join(root, file_name)
                    extracted_path = local_file_path.split('time_lapse', 1)[-1]
                    azure_blob_path = f"stargazerfarmmedia{extracted_path}"
                    azure_configuration = paths.AZURE_CONFIG
                    url = ah.upload_file_to_azure(local_file_path, azure_blob_path, azure_configuration)
                    file.write(f"File '{local_file_path}' uploaded to Azure Blob Storage. URL: {url}\n")

    print(f"Upload results saved to '{output_file}'")
    print(f"Completed successfully")

if __name__ == '__main__':
    folder_path = "/home/stefan/Downloads/farm_takeouts/takeout-20230508T043522Z-004/Takeout/Google Photos/"
    upload_takeout(folder_path)
