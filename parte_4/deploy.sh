#!/bin/bash
cd "$(dirname "$0")"

eval $(minikube docker-env)
cd bookinfo/src/reviews && docker run --rm -u root -v $(pwd):/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build && cd ../../..
docker build -f Dockerfile.productpage -t 17/productpage .
docker build -f Dockerfile.details -t 17/details .
docker build -f Dockerfile.ratings -t 17/ratings --build-arg star_color=black .
docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false .
docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black .
docker build -f bookinfo/src/reviews/reviews-wlpcfg/Dockerfile -t 17/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red .
kubectl apply -f bookinfo/platform/kube/cdps-namespace.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/details.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/ratings.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/reviews-svc.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/reviews-v1-deployment.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/reviews-v2-deployment.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/reviews-v3-deployment.yaml --validate=false
kubectl apply -f bookinfo/platform/kube/productpage.yaml --validate=false
kubectl port-forward --address=0.0.0.0 -n cdps-17 svc/productpage-service 9080:9080
