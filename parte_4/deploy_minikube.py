#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import subprocess
import os
import sys

TEAM_ID = "17"
NAMESPACE = "cdps-{}".format(TEAM_ID)

def run_cmd(cmd):
    print(cmd)
    return subprocess.call(cmd, shell=True)

def main():
    # Detectar minikube
    result = subprocess.call("kubectl config current-context | grep minikube > /dev/null 2>&1", shell=True)
    if result != 0:
        print("Error: No estás en minikube")
        sys.exit(1)
    
    print("Minikube detectado")
    
    # Configurar Docker para Minikube
    print("\nConfigurando Docker para Minikube...")
    os.system('eval $(minikube docker-env)')
    
    # Volver a la raiz de parte_4
    os.chdir("../../..")
    
    # Construir imagenes
    print("\nConstruyendo imagenes...")
    run_cmd("docker build -f Dockerfile.productpage -t {}/productpage .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.details -t {}/details .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.ratings -t {}/ratings .".format(TEAM_ID))
    
    # Compilar reviews
    print("\nCompilando Reviews...")
    os.chdir("bookinfo/src/reviews")
    run_cmd('docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build')
    os.chdir("../../..")
    
    # Construir reviews
    print("\nConstruyendo imagenes de Reviews...")
    run_cmd("docker build -t {}/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    run_cmd("docker build -t {}/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    run_cmd("docker build -t {}/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    
    # Volver a kube
    os.chdir("bookinfo/platform/kube")
    
    # Desplegar
    print("\nDesplegando en Kubernetes...")
    run_cmd("kubectl apply -f cdps-namespace.yaml")
    run_cmd("kubectl apply -f details.yaml")
    run_cmd("kubectl apply -f ratings.yaml")
    run_cmd("kubectl apply -f reviews-svc.yaml")
    run_cmd("kubectl apply -f reviews-v1-deployment.yaml")
    run_cmd("kubectl apply -f reviews-v2-deployment.yaml")
    run_cmd("kubectl apply -f reviews-v3-deployment.yaml")
    run_cmd("kubectl apply -f productpage.yaml")
    
    # Mostrar estado
    print("\nPods:")
    run_cmd("kubectl get pods -n {}".format(NAMESPACE))
    
    print("\nServicios:")
    run_cmd("kubectl get services -n {}".format(NAMESPACE))
    
    print("\nDeployments:")
    run_cmd("kubectl get deployments -n {}".format(NAMESPACE))

if __name__ == "__main__":
    main()
