import json
import os

def register_worker(dals_db, serial, model, ledger_code, class_code, port):
    entry = {
        "serial": serial,
        "model": model,
        "ledger_code": ledger_code,
        "class_code": class_code,
        "port": port
    }
    dals_db["workers"].append(entry)
    return entry