#!/bin/bash

SCRIPT_DIR="$(pwd)"

eval $(minikube docker-env)
cd "$SCRIPT_DIR/../../.." || exit 1
docker build -f Dockerfile.productpage -t 17/productpage . || true
docker build -f Dockerfile.details -t 17/details . || true
docker build -f Dockerfile.ratings -t 17/ratings . || true
cd bookinfo/src/reviews

docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build

cd ../../..
docker build -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg || true
docker build -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg || true
docker build -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg || true
cd "$SCRIPT_DIR"


kubectl apply -f cdps-namespace.yaml
sleep 2
kubectl apply -f details.yaml
kubectl apply -f ratings.yaml
kubectl apply -f reviews-svc.yaml
kubectl apply -f reviews-v1-deployment.yaml
kubectl apply -f reviews-v2-deployment.yaml
kubectl apply -f reviews-v3-deployment.yaml
kubectl apply -f productpage.yaml

kubectl port-forward --address=0.0.0.0 -n cdps-17 svc/productpage-service 9080:9080
