import os
import requests
import urllib
import gzip
import shutil

def download_and_extract(url, files_dir):
    """Downloads and extracts a .gz file and returns its size."""

    # Extract the file name from the URL without query parameters
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)  # Extracts "2025-03_890_58B0_in-network-rates_41_of_240.json.gz"

    gz_filepath = os.path.join(files_dir, filename)
    extracted_filepath = gz_filepath.replace(".gz", "")

    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    with open(gz_filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    with gzip.open(gz_filepath, "rb") as f_in:
        with open(extracted_filepath, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.remove(gz_filepath)
    print(f"Extracted: {extracted_filepath}")

    return extracted_filepath, os.path.getsize(extracted_filepath)