import random

def generate_model(class_code: str):
    rand_num = random.randint(10**9, (10**10)-1)
    prefix = class_code.split(".")[0]
    return f"{prefix}-{rand_num}"