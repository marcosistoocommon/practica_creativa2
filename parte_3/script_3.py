#!/usr/bin/env python3
import subprocess, os
import sys
from pathlib import Path

subprocess.run("sudo apt install -y podman-docker", shell=True)

os.chdir("bookinfo/src/reviews")
pwd = os.getcwd()
subprocess.run(f"docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
os.chdir("../../..")
subprocess.run("docker compose -f docker-compose.micro.yml build", shell=True)
subprocess.run("docker compose -f docker-compose.micro.yml up -d", shell=True)