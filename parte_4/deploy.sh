#!/bin/bash

minikube start

SCRIPT_DIR="$(pwd)"

eval $(minikube docker-env)

docker build -f Dockerfile.productpage -t 17/productpage . 
docker build -f Dockerfile.details -t 17/details . 
docker build -f Dockerfile.ratings -t 17/ratings . 
cd bookinfo/src/reviews

docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build

cd ../../..
docker build -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg 
docker build -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg 
docker build -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg 
cd bookinfo/platform/kube


kubectl apply --validate=false -f cdps-namespace.yaml

kubectl apply --validate=false -f details.yaml
kubectl apply --validate=false -f ratings.yaml
kubectl apply --validate=false -f reviews-svc.yaml
kubectl apply --validate=false -f reviews-v1-deployment.yaml
kubectl apply --validate=false -f reviews-v2-deployment.yaml
kubectl apply --validate=false -f reviews-v3-deployment.yaml
kubectl apply --validate=false -f productpage.yaml

kubectl port-forward --address=0.0.0.0 -n cdps-17 svc/productpage-service 9080:9080