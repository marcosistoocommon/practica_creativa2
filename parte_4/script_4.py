#!/usr/bin/env python3
import subprocess, os

os.chdir("bookinfo/src/reviews")
subprocess.run(f"docker run --rm -u root -v {os.getcwd()}:/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build", shell=True)
os.chdir("../../..")
subprocess.run("docker build -f Dockerfile.productpage -t 17/productpage .", shell=True)
subprocess.run("docker build -f Dockerfile.details -t 17/details bookinfo/src/details", shell=True)
subprocess.run("docker build -f Dockerfile.ratings -t 17/ratings --build-arg star_color=black bookinfo/src/ratings", shell=True)

subprocess.run("docker build -f Dockerfile.reviews -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg", shell=True)
subprocess.run("docker build -f Dockerfile.reviews -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg", shell=True)
subprocess.run("docker build -f Dockerfile.reviews -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg", shell=True)

subprocess.run("kubectl apply -f cdps-namespace.yaml", shell=True)
subprocess.run("kubectl apply -f details.yaml", shell=True)
subprocess.run("kubectl apply -f ratings.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-svc.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v1.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v2.yaml", shell=True)
subprocess.run("kubectl apply -f reviews-v3.yaml", shell=True)
subprocess.run("kubectl apply -f productpage.yaml", shell=True)


subprocess.run("kubectl port-forward -n cdps-17 svc/productpage-service 9080:9080", shell=True)