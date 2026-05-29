"""
Upload historical data files to Azure Data Lake Storage Gen2.

Scans the local 'data/historical_data/' directory and uploads all
CSV and JSON files to the 'historical_data/' folder in ADLS.

Credentials are loaded from environment variables or a '.env' file.

Required environment variables:
    AZURE_STORAGE_CONNECTION_STRING : Azure Storage Account connection string

Usage:
    python upload_historical.py
"""

import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

_HISTORICAL_DATA_DIR = Path(__file__).parent / "data" / "historical_data"
_CONTAINER_NAME      = "ride-hailing-lake"
_DESTINATION_PREFIX  = "historical_data"


def _build_client() -> BlobServiceClient:
    """
    Creates a Blob Service client using credentials from the environment.

    Raises:
        EnvironmentError: If AZURE_STORAGE_CONNECTION_STRING is not set.
    """
    connection_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_str:
        raise EnvironmentError(
            "Missing required environment variable.\n"
            "Ensure AZURE_STORAGE_CONNECTION_STRING is set in your .env file."
        )
    return BlobServiceClient.from_connection_string(connection_str)


def run() -> None:
    """
    Upload all CSV and JSON files from historical_data/ to ADLS.
    """
    load_dotenv()
    client = _build_client()
    container = client.get_container_client(_CONTAINER_NAME)

    files = [f for f in _HISTORICAL_DATA_DIR.iterdir() if f.suffix in (".csv", ".json")]

    if not files:
        print("No historical data files found.")
        return

    print(f"Uploading {len(files)} file(s) to {_CONTAINER_NAME}/{_DESTINATION_PREFIX}/")

    for file in files:
        blob_name = f"{_DESTINATION_PREFIX}/{file.name}"
        with open(file, "rb") as data:
            container.upload_blob(name=blob_name, data=data, overwrite=True)
        print(f"  Uploaded: {file.name}")

    print("Done.")


if __name__ == "__main__":
    run()
