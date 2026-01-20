#!/usr/bin/env python3
import subprocess, os
import sys
import time

if len(sys.argv) < 2:
    print("Usage: python script_4.py [install|build|run|stop|delete]")
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "install":
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt-get update -y", shell=True)
    subprocess.run("export DEBIAN_FRONTEND=noninteractive && sudo apt install -y docker.io", shell=True)
    subprocess.run("sudo systemctl enable docker", shell=True)
    subprocess.run("sudo systemctl restart docker || true", shell=True)
    subprocess.run("sudo snap install kubectl --classic", shell=True)
    subprocess.run("wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 -O minikube", shell=True)
    subprocess.run("chmod 755 minikube ", shell=True)
    subprocess.run("sudo mv minikube /usr/local/bin/", shell=True)
    subprocess.run("sudo groupadd -f docker", shell=True)
    subprocess.run("sudo usermod -aG docker $USER", shell=True)
    subprocess.run("sudo systemctl restart docker", shell=True)
    subprocess.run("sudo minikube start --force --driver=docker --memory=2048 --cpus=2", shell=True)
    subprocess.run("sudo minikube status", shell=True)
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
    
    print("Loading images into Minikube (this may take a while)...")
    print("Loading 17/productpage")
    subprocess.run("sudo minikube image load 17/productpage", shell=True)
    print("Loading 17/ratings")
    subprocess.run("sudo minikube image load 17/ratings", shell=True)
    print("Loading 17/details")
    subprocess.run("sudo minikube image load 17/details", shell=True)
    print("Loading 17/reviews-v1")
    subprocess.run("sudo minikube image load 17/reviews-v1", shell=True)
    print("Loading 17/reviews-v2")
    subprocess.run("sudo minikube image load 17/reviews-v2", shell=True)
    print("Loading 17/reviews-v3")
    subprocess.run("sudo minikube image load 17/reviews-v3", shell=True)
    print("All images loaded into Minikube. Ready to run the application.")

elif cmd == "run":
    os.chdir("bookinfo/platform/kube")
    subprocess.run("sudo kubectl apply --validate=false -f cdps-namespace.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f details.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f ratings.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f reviews-svc.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f reviews-v1-deployment.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f reviews-v2-deployment.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f reviews-v3-deployment.yaml", shell=True)
    subprocess.run("sudo kubectl apply --validate=false -f productpage.yaml", shell=True)
    subprocess.run("sudo kubectl get svc productpage-service -n cdps-17 -o wide", shell=True)
    
    print("\nStarting port-forward to expose service externally...")
    print("Access the service at http://34.163.46.254:9080")
    subprocess.Popen("sudo kubectl port-forward -n cdps-17 svc/productpage-service 9080:9080 --address 0.0.0.0", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print("Port-forward started in background. Service is now accessible!")

elif cmd == "stop":
    subprocess.run("sudo kubectl delete namespace cdps-17", shell=True)

elif cmd == "delete":
    subprocess.run("kubectl delete namespace cdps-17 2>/dev/null || true", shell=True)
    subprocess.run("sudo docker rmi -f 17/productpage 17/details 17/ratings 17/reviews-v1 17/reviews-v2 17/reviews-v3 2>/dev/null || true", shell=True)

else:
    print("Invalid command. Use: install, build, run, watch, stop, or delete")
    sys.exit(1)