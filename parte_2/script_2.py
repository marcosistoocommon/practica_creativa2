#!/usr/bin/env python
import subprocess, os

subprocess.run("docker build -t cdps-productpage:g17 .", shell=True)
subprocess.run("docker run -p 9095:8080 -e TEAM_ID=17 -e APP_OWNER=Perez-et-al -d cdps-productpage:g17", shell=True)