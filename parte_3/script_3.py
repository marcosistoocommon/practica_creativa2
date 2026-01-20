#!/usr/bin/env python3
import subprocess, os
import sys


if len(sys.argv) < 2:
    print("Usage: python script_2.py [build|run|stop|debug]|delete")
    sys.exit(1)

cmd = sys.argv[1].lower()

subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
subprocess.run("sudo systemctl enable docker", shell=True)
subprocess.run("sudo systemctl restart docker || true", shell=True)

if cmd == "build":

    os.chdir("bookinfo/src/reviews")
    pwd = os.getcwd()
    subprocess.run(f"sudo docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
    os.chdir("../../..")
    subprocess.run("sudo docker compose -f docker-compose.micro.yml build", shell=True)

if cmd == "run":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml up -d", shell=True)

elif cmd == "stop":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml down", shell=True)

elif cmd == "debug":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml up", shell=True)

elif cmd == "delete":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml down --rmi all", shell=True)
else:
    print("Invalid command. Use: build, run, stop, debug, or delete")
    sys.exit(1)
