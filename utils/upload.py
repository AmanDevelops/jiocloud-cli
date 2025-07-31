import hashlib
import json
import os
from argparse import Namespace

import requests
from tqdm import tqdm

from utils.encryption import encrypt_file_py7zr

LOGIN_DETAILS_PATH = "login_details.json"
FIRST_CHUNK_SIZE = 2 * 1024 * 1024
MIN_CHUNK_SIZE_IN_MB = 1 * 1024 * 1024


def compute_md5(file_path: str, chunk_size=8192) -> str:
    """
    Calculate the MD5 hex for the chunk
    """

    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
    except FileNotFoundError:
        return None
    return md5.hexdigest()


def generate_json_from_file_with_md5(filename: str, folder_key: str) -> dict:
    """
    generate the md5 hex for the whole file
    """

    try:
        size_bytes = os.path.getsize(filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None

    file_hash = compute_md5(filename)
    if file_hash is None:
        print(f"Cannot compute hash, file missing: {filename}")
        return None

    headpath, filename = os.path.split(filename)

    json_data = {
        "name": filename,
        "size": size_bytes,
        "hash": file_hash,
        "folderKey": folder_key,
    }

    return json_data


def upload_file(args: Namespace) -> None:
    """
    Upload files
        - check if user has requested a file encryption
        - read login details from file
        - genrate md5 hash of complete file
        - create a request to initiate the file upload - got transaction id and offset
        - read the file in chunks and calculate hash of each chunk
        - update the offset and content-length header
        - upload the chunk - response -> new offset
    """

    filepath = str(args.path)
    encryption_state = str(args.encryption)
    folder_key = str(args.folder)

    # check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError()

    if encryption_state == "true":
        filepath = encrypt_file_py7zr(filepath)

    if not os.path.exists(LOGIN_DETAILS_PATH):
        print("Login Details not Found, Login first")
        return

    headers = {}
    with open(LOGIN_DETAILS_PATH, "r") as f:
        headers = json.loads(f.read())

    headers["X-User-Id"] = headers.pop("userId", None)

    json_data = generate_json_from_file_with_md5(filepath, folder_key)

    upload_initiate = requests.post(
        "https://jaws-upload.jiocloud.com/upload/files/chunked/initiate",
        headers=headers,
        json=json_data,
    ).json()

    if upload_initiate.get("createdDate"):
        print("File already exists or uploaded from cache")
        return

    params = {
        "uploadId": upload_initiate.get("transactionId"),
    }

    file_size = json_data["size"]

    with open(filepath, "rb") as f, tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc="Uploading",
        initial=upload_initiate.get("offset"),
    ) as progress_bar:
        offset = upload_initiate.get("offset")
        start = offset
        chunk_index = 0

        while offset > FIRST_CHUNK_SIZE - MIN_CHUNK_SIZE_IN_MB * chunk_index:
            chunk_index += 1

        while start < file_size:
            if chunk_index < 2:
                current_chunk_size = min(FIRST_CHUNK_SIZE, file_size)
            else:
                remaining = file_size - start
                current_chunk_size = min(MIN_CHUNK_SIZE_IN_MB, remaining)

            chunk = f.read(current_chunk_size)

            if not chunk:
                break

            md5_hex = hashlib.md5(chunk).hexdigest()

            headers["Content-MD5"] = md5_hex
            headers["Content-Length"] = str(current_chunk_size)
            headers["X-Offset"] = str(offset)
            headers["Content-Type"] = "application/octet-stream"

            response = requests.put(
                "https://jaws-upload.jiocloud.com/upload/files/chunked",
                data=chunk,
                headers=headers,
                params=params,
            )

            offset = response.json().get("offset")

            progress_bar.update(len(chunk))

            start += len(chunk)
            chunk_index += 1
