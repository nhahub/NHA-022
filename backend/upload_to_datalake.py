from azure.storage.filedatalake import DataLakeServiceClient
import io
import cv2
from dotenv import load_dotenv
import os

load_dotenv() # load vars from .env

# Your Azure Data Lake Storage credentials
# Replace with your actual values
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
file_system_name = os.getenv("file_system_name")

# Create a DataLakeServiceClient
service_client = DataLakeServiceClient.from_connection_string(connection_string)
file_system_client = service_client.get_file_system_client(file_system=file_system_name)

def upload_to_datalake(image, file_path_in_datalake, file_system_name=file_system_name, connection_string=connection_string):
    try:
        # Convert the OpenCV image to bytes
        is_success, buffer = cv2.imencode(".jpg", image)
        if not is_success:
            raise ValueError("Could not encode image to JPG format")

        byte_stream = io.BytesIO(buffer)

        # Get a file client and upload the data
        file_client = file_system_client.get_file_client(file_path_in_datalake)

        # The upload_data method handles the upload of the byte stream
        file_client.upload_data(data=byte_stream, overwrite=True)
        print(f"Image successfully uploaded to Azure Data Lake at: {file_path_in_datalake}")
        
    except Exception as ex:
        print('Exception:')
        print(ex)