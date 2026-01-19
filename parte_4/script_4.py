#!/usr/bin/env python3
import subprocess, os

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
kube_dir = os.path.join(script_dir, "bookinfo/platform/kube")

# Build Gradle (Reviews)
os.chdir(os.path.join(script_dir, "bookinfo/src/reviews"))
subprocess.run(f"docker run --rm -u root -v {os.getcwd()}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
os.chdir(script_dir)

# Build Docker images
subprocess.run("docker build -f Dockerfile.productpage -t 17/productpage .", shell=True)
subprocess.run("docker build -f Dockerfile.details -t 17/details bookinfo/src/details", shell=True)
subprocess.run("docker build -f Dockerfile.ratings -t 17/ratings --build-arg star_color=black bookinfo/src/ratings", shell=True)

subprocess.run("docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg", shell=True)
subprocess.run("docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg", shell=True)
subprocess.run("docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg", shell=True)

# Apply Kubernetes manifests
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'cdps-namespace.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'details.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'ratings.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'reviews-svc.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'reviews-v1-deployment.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'reviews-v2-deployment.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'reviews-v3-deployment.yaml')}", shell=True)
subprocess.run(f"kubectl apply -f {os.path.join(kube_dir, 'productpage.yaml')}", shell=True)

# Port forward
subprocess.run("kubectl port-forward --address=0.0.0.0 -n cdps-17 svc/productpage-service 9080:9080", shell=True)