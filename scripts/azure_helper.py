import configparser
import pandas as pd
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import BlobSasPermissions
from azure.storage.blob import BlobSasPermissions, generate_blob_sas


from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
bucket = 'sfdatalake'

def upload_file_to_azure(local_path, azure_path, azure_config, make_public=True):
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
    #Disabling since this shouldn't be needed
    # try:
    #     container_client.create_container()
    # except Exception as e:
    #     print(f"Container {container_name} already exists or an error occurred. Error: {str(e)}")

    # Instantiate a BlobClient
    blob_client = container_client.get_blob_client(blob_name)

    # Upload the local file to Azure Blob Storage
    with open(local_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


    print(f"File '{local_path}' uploaded to '{azure_path}'")

    url = f"https://{bucket}.blob.core.windows.net/{azure_path}"


    return url

if __name__ == "__main__":
    # Example usage:
    local_file_path = "/Users/stefanhamilton/dev/image-processing/data/IMG_0503.jpg"
    azure_blob_path = "stargazerfarmmedia/10_plant_sample/IMG_0503.jpg"
    azure_configuration = '/Users/stefanhamilton/dev/image-processing/azure_blob_wblms_config.ini'
    upload_file_to_azure(local_file_path, azure_blob_path, azure_configuration)