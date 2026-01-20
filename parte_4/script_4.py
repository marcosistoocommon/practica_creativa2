#!/usr/bin/env python3
import subprocess, os, sys, time

PROJECT_ID = "perfect-obelisk-480209-b2"
REGION = "europe-north1"
ZONE = f"{REGION}-a"
CLUSTER_NAME = "productpage-cluster"

if len(sys.argv) < 2:
    sys.exit(1)

cmd = sys.argv[1].lower()

if cmd == "install":
    subprocess.run("sudo apt-get update -y", shell=True)
    subprocess.run("sudo apt-get install -y docker.io", shell=True)
    subprocess.run("sudo usermod -aG docker $USER", shell=True)
    subprocess.run("gcloud auth application-default login --quiet 2>/dev/null || true", shell=True)
    subprocess.run(f"gcloud config set project {PROJECT_ID}", shell=True)
    subprocess.run(f"gcloud container clusters create {CLUSTER_NAME} --num-nodes=3 --zone={ZONE} --no-enable-autoscaling", shell=True)
    subprocess.run(f"gcloud container clusters get-credentials {CLUSTER_NAME} --zone={ZONE}", shell=True)
    subprocess.run("gcloud auth configure-docker --quiet", shell=True)

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
    
    subprocess.run(f"sudo docker tag 17/productpage gcr.io/{PROJECT_ID}/productpage:latest", shell=True)
    subprocess.run(f"sudo docker tag 17/ratings gcr.io/{PROJECT_ID}/ratings:latest", shell=True)
    subprocess.run(f"sudo docker tag 17/details gcr.io/{PROJECT_ID}/details:latest", shell=True)
    subprocess.run(f"sudo docker tag 17/reviews-v1 gcr.io/{PROJECT_ID}/reviews:v1", shell=True)
    subprocess.run(f"sudo docker tag 17/reviews-v2 gcr.io/{PROJECT_ID}/reviews:v2", shell=True)
    subprocess.run(f"sudo docker tag 17/reviews-v3 gcr.io/{PROJECT_ID}/reviews:v3", shell=True)
    
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/productpage:latest", shell=True)
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/ratings:latest", shell=True)
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/details:latest", shell=True)
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/reviews:v1", shell=True)
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/reviews:v2", shell=True)
    subprocess.run(f"sudo docker push gcr.io/{PROJECT_ID}/reviews:v3", shell=True)

elif cmd == "run":
    subprocess.run(f"sed -i 's|image: 17/productpage|image: gcr.io/{PROJECT_ID}/productpage:latest|g' bookinfo/platform/kube/productpage.yaml", shell=True)
    subprocess.run(f"sed -i 's|image: 17/details|image: gcr.io/{PROJECT_ID}/details:latest|g' bookinfo/platform/kube/details.yaml", shell=True)
    subprocess.run(f"sed -i 's|image: 17/ratings|image: gcr.io/{PROJECT_ID}/ratings:latest|g' bookinfo/platform/kube/ratings.yaml", shell=True)
    subprocess.run(f"sed -i 's|image: 17/reviews-v1|image: gcr.io/{PROJECT_ID}/reviews:v1|g' bookinfo/platform/kube/reviews-v1-deployment.yaml", shell=True)
    subprocess.run(f"sed -i 's|image: 17/reviews-v2|image: gcr.io/{PROJECT_ID}/reviews:v2|g' bookinfo/platform/kube/reviews-v2-deployment.yaml", shell=True)
    subprocess.run(f"sed -i 's|image: 17/reviews-v3|image: gcr.io/{PROJECT_ID}/reviews:v3|g' bookinfo/platform/kube/reviews-v3-deployment.yaml", shell=True)
    
    os.chdir("bookinfo/platform/kube")
    subprocess.run("kubectl apply -f cdps-namespace.yaml", shell=True)
    subprocess.run("kubectl apply -f details.yaml", shell=True)
    subprocess.run("kubectl apply -f ratings.yaml", shell=True)
    subprocess.run("kubectl apply -f reviews-svc.yaml", shell=True)
    subprocess.run("kubectl apply -f reviews-v1-deployment.yaml", shell=True)
    subprocess.run("kubectl apply -f reviews-v2-deployment.yaml", shell=True)
    subprocess.run("kubectl apply -f reviews-v3-deployment.yaml", shell=True)
    subprocess.run("kubectl apply -f productpage.yaml", shell=True)
    
    time.sleep(60)
    result = subprocess.run("kubectl get svc productpage-service -n cdps-17 -o jsonpath='{.status.loadBalancer.ingress[0].ip}'", shell=True, capture_output=True, text=True)
    ip = result.stdout.strip().replace("'", "")
    if ip:
        subprocess.run(f"echo http://{ip}:9080", shell=True)

elif cmd == "stop":
    subprocess.run("kubectl delete namespace cdps-17", shell=True)

elif cmd == "delete":
    subprocess.run(f"gcloud container clusters delete {CLUSTER_NAME} --zone={ZONE} --quiet", shell=True)

else:
    sys.exit(1)
