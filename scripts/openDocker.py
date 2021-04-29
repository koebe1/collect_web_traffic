import subprocess
import sys
import psutil
import time
import yaml
import os.path

scripts = os.path.dirname(__file__)
dataset = os.path.dirname(scripts)

with open(os.path.join(dataset, 'config.yml')) as f:
    config = yaml.safe_load(f)
    sec = config["sec"]
    docker_path = config["docker_path"]

if "docker" in (p.name() for p in psutil.process_iter()):
    print("Docker is up and running!")
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    p = subprocess.call([opener, docker_path])
    print("Docker is up and running!")
    time.sleep(sec)
