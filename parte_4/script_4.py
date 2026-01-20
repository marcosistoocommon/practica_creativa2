#!/usr/bin/env python3
import subprocess, os
import sys
import time

if len(sys.argv) < 2:
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "install":
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y curl wget apt-transport-https", shell=True)
    subprocess.run("sudo apt install -y podman-docker", shell=True)
    subprocess.run("sudo systemctl enable --now podman.socket", shell=True)
    subprocess.run("sudo systemctl start podman.socket", shell=True)
    subprocess.run("echo 'unqualified-search-registries = [\"docker.io\"]' | sudo tee -a /etc/containers/registries.conf", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
    subprocess.run("sudo systemctl restart docker || true", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y conntrack crictl", shell=True)
    subprocess.run("curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64", shell=True)
    subprocess.run("sudo install minikube-linux-amd64 /usr/local/bin/minikube", shell=True)
    subprocess.run("minikube start --driver=none --force", shell=True)
    subprocess.run("sudo snap install kubectl --classic 2>/dev/null || true", shell=True)

elif cmd == "build":
    os.chdir("bookinfo/src/reviews")
    pwd = os.getcwd()
    subprocess.run(f"sudo docker run --rm -u root -v {pwd}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
    os.chdir("reviews-wlpcfg")
    subprocess.run("sudo docker build -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false --build-arg star_color=black .", shell=True)
    subprocess.run("sudo docker build -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black .", shell=True)
    subprocess.run("sudo docker build -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red .", shell=True)
    os.chdir("../../../..")
    subprocess.run("sudo docker build -f Dockerfile.productpage -t 17/productpage .", shell=True)
    subprocess.run("sudo docker build -f Dockerfile.ratings -t 17/ratings .", shell=True)
    subprocess.run("sudo docker build -f Dockerfile.details -t 17/details .", shell=True)

elif cmd == "run":
    os.chdir("bookinfo/platform/kube")
    subprocess.run("kubectl apply --validate=false -f cdps-namespace.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f details.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f ratings.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f reviews-svc.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f reviews-v1-deployment.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f reviews-v2-deployment.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f reviews-v3-deployment.yaml", shell=True)
    subprocess.run("kubectl apply --validate=false -f productpage.yaml", shell=True)

elif cmd == "watch":
    while True:
        result = subprocess.run("kubectl get svc productpage-service -n cdps-17 -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null", shell=True, capture_output=True, text=True)
        ip = result.stdout.strip()
        if ip and ip != "''" and ip != "":
            subprocess.run(f"echo {ip}", shell=True)
            break
        time.sleep(2)

elif cmd == "stop":
    subprocess.run("kubectl delete namespace cdps-17", shell=True)

elif cmd == "delete":
    subprocess.run("kubectl delete namespace cdps-17 2>/dev/null || true", shell=True)
    subprocess.run("sudo docker rmi -f 17/productpage 17/details 17/ratings 17/reviews-v1 17/reviews-v2 17/reviews-v3 2>/dev/null || true", shell=True)

else:
    print("Invalid command. Use: install, build, run, watch, stop, or delete")
    sys.exit(1)