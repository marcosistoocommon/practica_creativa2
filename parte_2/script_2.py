#!/usr/bin/env python
import subprocess, os

subprocess.run("sudo docker build -t cdps-productpage:g17 .", shell=True)
subprocess.run("sudo docker run --name productpage_cdps_17 -p 9095:8080 -e TEAM_ID=17 -e APP_OWNER=Perez-et-al -d cdps-productpage:g17", shell=True)