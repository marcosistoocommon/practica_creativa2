#!/usr/bin/env python

import subprocess, os

subprocess.run("git clone https://github.com/CDPS-ETSIT/practica_creativa2.git", shell=True)
subprocess.run("sudo apt update", shell=True)
subprocess.run("sudo apt install software-properties-common", shell=True)
subprocess.run("sudo add-apt-repository -y ppa:deadsnakes/ppa", shell=True)
subprocess.run("sudo apt install -y python3.9 python3.9-venv python3.9-distutils", shell=True)
os.chdir("practica_creativa2/bookinfo/src/productpage/")

subprocess.run("python3.9 -m venv venv", shell=True)
subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True)

os.environ['TEAM_ID'] = '17'
subprocess.run("export TEAM_ID=17 && ./venv/bin/python3.9 productpage_monolith.py 6050", shell=True)