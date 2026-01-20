#!/usr/bin/env python3
import subprocess, os
import sys
from pathlib import Path

subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y curl wget apt-transport-https", shell=True)
subprocess.run("sudo apt install -y podman-docker", shell=True)
subprocess.run("sudo systemctl enable --now podman.socket", shell=True)
subprocess.run("sudo systemctl start podman.socket", shell=True)
subprocess.run("echo 'unqualified-search-registries = [\"docker.io\"]' | sudo tee -a /etc/containers/registries.conf", shell=True)
subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
subprocess.run("sudo systemctl enable --now docker", shell=True)
subprocess.run("curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64", shell=True)
subprocess.run("sudo install minikube-linux-amd64 /usr/local/bin/minikube", shell=True)
subprocess.run("minikube start --driver=docker --force", shell=True)
subprocess.run("sudo snap install kubectl --classic", shell=True)

os.chdir("bookinfo/src/reviews")
pwd = os.getcwd()
subprocess.run(f"sudo docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
os.chdir("reviews-wlpgc")
subprocess.run("sudo docker build -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false .", shell=True)
subprocess.run("sudo docker build -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black .", shell=True)
subprocess.run("sudo docker build -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red .", shell=True)
os.chdir("../../../..")
subprocess.run("sudo docker build -f Dockerfile.productpage -t 17/productpage .", shell=True)
subprocess.run("sudo docker build -f Dockerfile.ratings -t 17/ratings .", shell=True)
subprocess.run("sudo docker build -f Dockerfile.details -t 17/details .", shell=True)

os.chdir("../../parte_4/bookinfo/platform/kube")

subprocess.run("kubectl apply -f cdps-namespace.yaml", shell=True)
subprocess.run("kubectl apply -f details.yaml", shell=True)
subprocess.run("kubectl apply -f ratings.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-svc.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v1.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v2.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v3.yaml", shell=True)
subprocess.run("kubectl apply -f productpage.yaml", shell=True)

