import hashlib


def generate_hash(text: str):
    result = hashlib.sha256(text.encode())
    return result.hexdigest()

