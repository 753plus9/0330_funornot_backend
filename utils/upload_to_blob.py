# utils/upload_to_blob.py

import os
import uuid
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)

async def upload_image_to_blob(file):
    contents = await file.read()  # ← bytes 型として読み込む

    _, ext = os.path.splitext(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    blob_client = container_client.get_blob_client(unique_filename)
    blob_client.upload_blob(contents, overwrite=True)

    blob_url = blob_client.url
    return blob_url, contents  # ← contents も返す！
