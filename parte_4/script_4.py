#!/usr/bin/env python3
import subprocess, os

subprocess.run("chmod +x bookinfo/platform/kube/deploy.sh", shell=True)
subprocess.run("bookinfo/platform/kube/deploy.sh", shell=True)