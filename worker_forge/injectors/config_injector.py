import json
import os

def inject_config(path, fields):
    file = os.path.join(path, "config.json")
    with open(file) as f:
        data = json.load(f)

    for k, v in fields.items():
        data[k] = v

    with open(file, "w") as f:
        json.dump(data, f, indent=4)