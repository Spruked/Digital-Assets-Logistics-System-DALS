import hashlib
import os

def hash_directory(path):
    hasher = hashlib.sha256()
    for root, dirs, files in os.walk(path):
        for file in sorted(files):
            filepath = os.path.join(root, file)
            with open(filepath, 'rb') as f:
                hasher.update(f.read())
    return hasher.hexdigest()