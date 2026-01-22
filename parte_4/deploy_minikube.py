#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import subprocess
import os
import sys
import time
import platform

TEAM_ID = "17"
NAMESPACE = "cdps-{}".format(TEAM_ID)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd):
    print(cmd)
    return subprocess.call(cmd, shell=True)

def main():
    os.chdir(BASE_DIR)
    
    # Detectar minikube
    result = subprocess.call("kubectl config current-context | grep minikube > /dev/null 2>&1", shell=True)
    if result != 0:
        print("Error: No estás en minikube")
        sys.exit(1)
    
    print("Minikube detectado")
    
    # Iniciar minikube
    print("Iniciando Minikube...")
    subprocess.call("minikube start", shell=True)
    
    print("Minikube iniciado")
    
    # Configurar Docker para Minikube
    print("\nConfigurando Docker para Minikube...")
    os.system('eval $(minikube docker-env)')
    
    # Construir imagenes desde parte_4/
    print("\nConstruyendo imagenes...")
    run_cmd("docker build -f Dockerfile.productpage -t {}/productpage .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.details -t {}/details .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.ratings -t {}/ratings .".format(TEAM_ID))
    
    # Compilar reviews
    print("\nCompilando Reviews...")
    run_cmd('cd bookinfo/src/reviews && docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build && cd {}'.format(BASE_DIR))
    
    # Construir reviews desde parte_4/
    print("\nConstruyendo imagenes de Reviews...")
    run_cmd("docker build -t {}/reviews-v1 --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    run_cmd("docker build -t {}/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true --build-arg star_color=black bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    run_cmd("docker build -t {}/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red bookinfo/src/reviews/reviews-wlpcfg".format(TEAM_ID))
    
    # Desplegar desde bookinfo/platform/kube
    print("\nDesplegando en Kubernetes...")
    os.chdir(os.path.join(BASE_DIR, "bookinfo/platform/kube"))
    
    # Verificar que minikube está listo
    print("Esperando a que Minikube esté listo...")
    for i in range(30):
        result = subprocess.call("kubectl cluster-info > /dev/null 2>&1", shell=True)
        if result == 0:
            break
        time.sleep(2)
    
    # Re-evaluar variables de Docker
    os.system('eval $(minikube docker-env)')
    
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
    
    # Esperar a que los pods estén listos
    print("\nEsperando a que los pods estén listos...")
    for i in range(60):
        result = subprocess.call("kubectl get pods -n {} -o jsonpath='{{.items[?(@.status.phase==\"Running\")].metadata.name}}' | grep -q productpage".format(NAMESPACE), shell=True)
        if result == 0:
            print("Pods listos")
            break
        time.sleep(1)
    
    # Obtener IP y puerto de acceso
    print("\nObtener acceso a la aplicacion:")
    print("Ejecuta en otra terminal: minikube tunnel")
    print("\nIniciando tunnel de Minikube en background...")
    try:
        tunnel_process = subprocess.Popen(
            ["minikube", "tunnel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
        )
        time.sleep(3)
        print("Tunnel iniciado")
    except Exception as e:
        print("Error iniciando tunnel: {}".format(e))
    print("\nURL del servicio:")
    run_cmd("minikube service productpage-service -n {} --url".format(NAMESPACE))

if __name__ == "__main__":
    main()
