#!/usr/bin/env python

import subprocess, os, sys

if len(sys.argv) < 2:
    print("Usage: python script_2.py [build|run]")
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "build":
    subprocess.run("sudo apt update", shell=True)
    subprocess.run("sudo apt install software-properties-common", shell=True)
    subprocess.run("sudo add-apt-repository -y ppa:deadsnakes/ppa", shell=True)
    subprocess.run("sudo apt install -y python3.9 python3.9-venv python3.9-distutils", shell=True)
    os.chdir("bookinfo/src/productpage/")

    subprocess.run("python3.9 -m venv venv", shell=True)
    subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True)

    os.environ['TEAM_ID'] = '17'
elif cmd == "run":
    os.chdir("bookinfo/src/productpage/")
    subprocess.run("export TEAM_ID=17 && ./venv/bin/python3.9 productpage_monolith.py 6050", shell=True)
else:
    print("Invalid command. Use: build or run")
    sys.exit(1)