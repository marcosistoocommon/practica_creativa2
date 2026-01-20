#!/usr/bin/env python3
import subprocess, os
import sys
from pathlib import Path

subprocess.run("sudo apt install -y podman-docker", shell=True)
subprocess.run("sudo systemctl enable --now podman.socket", shell=True)
subprocess.run("sudo systemctl start podman.socket", shell=True)
subprocess.run("echo 'unqualified-search-registries = [\"docker.io\"]' | sudo tee -a /etc/containers/registries.conf", shell=True)

os.chdir("bookinfo/src/reviews")
pwd = os.getcwd()
subprocess.run(f"sudo docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
os.chdir("../../..")
subprocess.run("sudo docker compose -f docker-compose.micro.yml build", shell=True)
subprocess.run("sudo docker compose -f docker-compose.micro.yml up -d", shell=True)