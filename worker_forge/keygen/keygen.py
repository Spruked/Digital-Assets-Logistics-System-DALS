from nacl.signing import SigningKey

def generate_worker_keys():
    private_key = SigningKey.generate()
    public_key = private_key.verify_key

    return private_key.encode(), public_key.encode()