#!/usr/bin/env python3
import subprocess, os

subprocess.run("chmod +x deploy.sh", shell=True)
subprocess.run("./deploy.sh", shell=True)