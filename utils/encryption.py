import getpass
import os

import py7zr


def encrypt_file_py7zr(filepath: str) -> str:
    """
    Encrypt the file with password
    """

    headpath, filename = os.path.split(filepath)
    while True:
        password = getpass.getpass(prompt=f"Enter the password for {filename}: ")
        conf_password = getpass.getpass(prompt=f"Confirm the password for {filename}: ")

        if password == conf_password:
            break

        print("Password didn't match")

    print("[Status]: Encrypting File...")
    with py7zr.SevenZipFile(
        filename.split(".")[0] + ".7z", "w", password=password
    ) as archive:
        archive.writeall(filepath)

    return filename.split(".")[0] + ".7z"
