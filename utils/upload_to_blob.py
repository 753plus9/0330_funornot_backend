# utils/upload_to_blob.py

import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import uuid

load_dotenv()

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)


def upload_image_to_blob(image_data: bytes, file_extension: str = "png") -> str:
    # ランダムなファイル名を生成
    blob_name = f"{uuid.uuid4().hex}.{file_extension}"

    # Blob にアップロード
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_data, overwrite=True)

    # 公開URLを構築（Blobのアクセスレベルが「匿名読み取り（パブリック）」に設定されている必要があります）
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"

    return blob_url
