import glob
import hashlib
import os


def gen_uid(username: str, filename: str) -> str:
    # Encode the username and filename as bytes
    data = f"{username}_{filename}".encode("utf-8")

    # Compute the SHA-256 hash of the data
    hashed_data = hashlib.sha1(data).hexdigest()

    # Return the hashed data
    return f"{hashed_data}"


def find_file_by_uid(upload_path, uid):
    search_pattern = os.path.join(upload_path, f"{uid}.*")
    matching_files = glob.glob(search_pattern)

    if not matching_files:
        return ""

    return matching_files[0]
