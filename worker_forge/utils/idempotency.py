import os
import shutil

def ensure_unique_worker(final_path):
    if os.path.exists(final_path):
        raise ValueError(f"Worker already exists at {final_path}")
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(final_path), exist_ok=True)