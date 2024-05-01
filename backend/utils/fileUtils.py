import hashlib

def gen_uid(username: str, filename: str) -> str:
    # Encode the username and filename as bytes
    data = f"{username}_{filename}".encode('utf-8')

    # Compute the SHA-256 hash of the data
    hashed_data = hashlib.sha1(data).hexdigest()

    # Return the hashed data
    return f"{hashed_data}.pdf"
