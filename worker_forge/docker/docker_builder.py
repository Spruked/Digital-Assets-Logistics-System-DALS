import subprocess
import os

def build_and_launch_worker(path, worker_name, port):
    image_name = f"worker_{worker_name.lower()}"
    subprocess.run(["docker", "build", "-t", image_name, path])
    subprocess.run([
        "docker", "run", "-d",
        "--name", worker_name,
        "-p", f"{port}:{port}",
        image_name
    ])