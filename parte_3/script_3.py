#!/usr/bin/env python3
import subprocess, os
import sys


if len(sys.argv) < 2:
    print("Usage: python script_3.py [build|run [v1|v2|v3]|stop|debug|delete]")
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
    # Reviews version: defaults to v1 if not provided
    raw_ver = sys.argv[2].lower().strip() if len(sys.argv) >= 3 else "v1"
    if raw_ver in ("1", "v1"):
        version = "v1"
    elif raw_ver in ("2", "v2"):
        version = "v2"
    elif raw_ver in ("3", "v3"):
        version = "v3"
    else:
        print("Invalid reviews version. Use v2, or v3.")
        sys.exit(1)

    env = os.environ.copy()
    if version == "v1":
        env["REVIEWS_APP_VERSION"] = "v1"
        env["REVIEWS_ENABLE_RATINGS"] = "false"
        env["REVIEWS_STAR_COLOR"] = ""
    elif version == "v2":
        env["REVIEWS_APP_VERSION"] = "v2"
        env["REVIEWS_ENABLE_RATINGS"] = "true"
        env["REVIEWS_STAR_COLOR"] = "black"
    elif version == "v3":
        env["REVIEWS_APP_VERSION"] = "v3"
        env["REVIEWS_ENABLE_RATINGS"] = "true"
        env["REVIEWS_STAR_COLOR"] = "red"

    subprocess.run("sudo docker compose -f docker-compose.micro.yml up -d", shell=True, env=env)

elif cmd == "stop":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml down", shell=True)

elif cmd == "debug":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml up", shell=True)

elif cmd == "delete":
    subprocess.run("sudo docker compose -f docker-compose.micro.yml down --rmi all", shell=True)
else:
    print("Invalid command. Use: build, run, stop, debug, or delete")
    sys.exit(1)
