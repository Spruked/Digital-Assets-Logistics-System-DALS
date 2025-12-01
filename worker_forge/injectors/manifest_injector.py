import json
import os

def inject_manifest(path, manifest):
    file = os.path.join(path, "worker_manifest.json")
    with open(file, "w") as f:
        json.dump(manifest, f, indent=4)