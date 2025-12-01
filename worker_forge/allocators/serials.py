import datetime
import uuid

def generate_serial(worker_type: str):
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:4].upper()
    prefix = f"{worker_type.upper()}-WKR"
    serial = f"{prefix}-{today}-{unique_id}"
    return serial