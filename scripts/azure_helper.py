import configparser
import pandas as pd
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import BlobSasPermissions
from azure.storage.blob import BlobSasPermissions, generate_blob_sas


from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
bucket = 'stargazerfarmmedia'

def upload_file_to_azure(local_path, azure_path, azure_config, make_public=False):
    """
    Upload a local file to Azure Blob Storage.

    :param local_path: str, path to the local file
    :param azure_path: str, path in Azure Blob Storage (format: "container_name/blob_name")
    :param azure_config: dict, Azure configuration containing connection string
    :param make_public: bool, whether to make the blob publicly accessible or not (default: False)
    :return: str, the URL of the uploaded file
    """

    # Read the Azure connection string from the config file
    config = configparser.ConfigParser()
    config.read(azure_config)
    connection_string = config.get('DEFAULT', 'azure_connection_string')

    # Split the azure_path into container_name and blob_name
    container_name, blob_name = azure_path.split("/", 1)

    # Instantiate a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it doesn't exist
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container {container_name} already exists or an error occurred. Error: {str(e)}")

    # Instantiate a BlobClient
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the local file to Azure Blob Storage
    with open(local_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


    print(f"File '{local_path}' uploaded to '{azure_path}'")

    #url = f"https://{bucket}.s3.<region>.amazonaws.com/{azure_path}"
    url = f"https://{bucket}.blob.core.windows.net/{azure_path}"
  

    return url

# Upload JSON files to Azure Blob Storage
def upload_photo_df_to_azure_blob(photos_metadata, csv_name, azure_config):

    # Read the Azure connection string from the config file
    config = configparser.ConfigParser()
    config.read(azure_config)
    connection_string = config.get('DEFAULT', 'azure_connection_string')

    # Initialize the BlobServiceClient with your connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Set the name of the Blob storage container and the CSV file name
    container_name = "photos-metadata2"

    # Get a reference to the container client
    container_client = blob_service_client.get_container_client(container_name)

    # Create the container if it does not exist
    if not container_client.exists():
        container_client.create_container()

    # Remove unwanted attributes from photos_metadata
    for photo in photos_metadata:
        del photo['productUrl']
        del photo['baseUrl']
        del photo['mimeType']
        del photo['mediaMetadata']['photo']
        del photo['filename']

    # Convert the JSON data to a Pandas DataFrame
    df = pd.json_normalize(photos_metadata)

    # Split the DataFrame into chunks of 100 rows each
    chunks = [df[i:i+100] for i in range(0, len(df), 100)]


    # Loop through the chunks and upload each one to Azure Blob Storage
    for i, chunk in enumerate(chunks):
        # Construct the file name for this chunk
        chunk_name = f"{csv_name.replace('.csv','')}_{i}.csv"

        # Convert the chunk to CSV and encode as bytes
        chunk_csv = chunk.to_csv(index=False).encode()

        # Upload the chunk to Azure Blob Storage
        blob_client = container_client.get_blob_client(chunk_name)
        blob_client.upload_blob(chunk_csv, overwrite=True)

        # Print a message indicating that the chunk was uploaded
        print(f"Uploaded {chunk_name} to {container_name} container in Azure Blob Storage.")

    # Print a message indicating that all chunks were uploaded
    print(f"All chunks of {csv_name} have been uploaded to {container_name} container in Azure Blob Storage.")

if __name__ == "__main__":
    # Example usage:
    local_file_path = "/Users/stefanhamilton/dev/image-processing/data/IMG_0503.jpg"
    azure_blob_path = "stargazerfarmmedia/10_plant_sample/IMG_0503.jpg"
    azure_configuration = '/Users/stefanhamilton/dev/image-processing/azure_blob_wblms_config.ini'
    upload_file_to_azure(local_file_path, azure_blob_path, azure_configuration)