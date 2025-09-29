# This file downloads the images from azure data lake
from azure.storage.filedatalake import DataLakeServiceClient
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Connection details
account_name = os.getenv("account_name")
account_key = os.getenv("account_key")
container_name = os.getenv("file_system_name")
remote_folder = "raw"
local_folder = "../data/caseStudy2"

# Create client
service_client = DataLakeServiceClient(
    account_url=f"https://{account_name}.dfs.core.windows.net",
    credential=account_key
)

file_system_client = service_client.get_file_system_client(file_system=container_name)

# List all paths in the remote folder
paths = file_system_client.get_paths(path=remote_folder)

for path in paths:
    if not path.is_directory:
        file_client = file_system_client.get_file_client(path.name)
        download = file_client.download_file().readall()

        # Build relative path
        relative_path = os.path.relpath(path.name, remote_folder)

        # Replace invalid Windows filename characters
        safe_path = re.sub(r'[<>:"/\\|?*]', "_", relative_path)

        # Join with local folder
        local_path = os.path.join(local_folder, safe_path)

        # Create directories if needed
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Save file
        with open(local_path, "wb") as f:
            f.write(download)

        print(f"Downloaded: {path.name} -> {local_path}")
