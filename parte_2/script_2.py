#!/usr/bin/env python
import subprocess, os
import sys


if len(sys.argv) < 2:
    print("Usage: python script_2.py [build|run|stop|delete]")
    sys.exit(1)

cmd = sys.argv[1].lower()


if cmd == "build":
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
    subprocess.run("sudo systemctl enable docker", shell=True)
    subprocess.run("sudo systemctl restart docker || true", shell=True)
    subprocess.run("sudo docker build -t cdps-productpage:g17 .", shell=True)
elif cmd == "run":
    subprocess.run("sudo docker run --name productpage_cdps_17 -p 9095:8080 -e TEAM_ID=17 -e APP_OWNER=Perez-et-al -d cdps-productpage:g17", shell=True)
elif cmd == "stop":
    subprocess.run("sudo docker stop productpage_cdps_17", shell=True)
    subprocess.run("sudo docker rm productpage_cdps_17", shell=True)
elif cmd == "delete":
    subprocess.run("sudo docker rm -f productpage_cdps_17", shell=True)
else:
    print("Invalid command. Use: build, run, stop, or delete")
    sys.exit(1)
