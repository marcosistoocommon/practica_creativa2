#!/usr/bin/env python3
import subprocess, os
import sys
import time

if len(sys.argv) < 2:
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "install":
    subprocess.run("sudo rm -f /etc/apt/sources.list.d/kubernetes.list 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -f /etc/apt/sources.list.d/*kubernetes* 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -f /usr/share/keyrings/kubernetes-archive-keyring.gpg 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -rf /tmp/juju-* 2>/dev/null || true", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y curl wget apt-transport-https", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y conntrack containernetworking-plugins", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
    subprocess.run("curl -LO https://github.com/Mirantis/cri-dockerd/releases/download/v0.3.4/cri-dockerd-0.3.4.amd64.tgz && tar xzf cri-dockerd-0.3.4.amd64.tgz && sudo install -o root -g root -m 0755 cri-dockerd/cri-dockerd /usr/local/bin/cri-dockerd && rm -rf cri-dockerd cri-dockerd-0.3.4.amd64.tgz", shell=True)
    subprocess.run("curl -LO https://raw.githubusercontent.com/Mirantis/cri-dockerd/master/packaging/systemd/cri-docker.service && sudo install -D -m 0644 cri-docker.service /etc/systemd/system/cri-docker.service && rm cri-docker.service", shell=True)
    subprocess.run("curl -LO https://raw.githubusercontent.com/Mirantis/cri-dockerd/master/packaging/systemd/cri-docker.socket && sudo install -D -m 0644 cri-docker.socket /etc/systemd/system/cri-docker.socket && rm cri-docker.socket", shell=True)
    subprocess.run("sudo systemctl daemon-reload && sudo systemctl enable cri-docker && sudo systemctl start cri-docker", shell=True)
    subprocess.run("curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64", shell=True)
    subprocess.run("sudo install minikube-linux-amd64 /usr/local/bin/minikube", shell=True)
    subprocess.run("sudo minikube delete --all --purge 2>/dev/null || true", shell=True)
    subprocess.run("sudo rm -rf /root/.minikube 2>/dev/null || true", shell=True)
    subprocess.run("sudo sysctl -w fs.protected_regular=0", shell=True)
    subprocess.run("sudo minikube start --driver=none --force --cri-socket /run/cri-dockerd.sock", shell=True)
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