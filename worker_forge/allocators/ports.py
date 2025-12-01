USED_PORTS = set()

def allocate_port(dals_db=None, base_port=6000):
    port = base_port
    while port in USED_PORTS:
        port += 1
    USED_PORTS.add(port)
    return port