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

def set_docker_env():
    """Set Docker environment to use minikube's Docker daemon"""
    try:
        output = subprocess.check_output("minikube docker-env --shell=bash", shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error obteniendo entorno docker de minikube: {}".format(e))
        sys.exit(1)
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("export "):
            kv = line[len("export "):]
            if "=" in kv:
                k, v = kv.split("=", 1)
                os.environ[k] = v.strip('"')
        elif line.startswith("unset "):
            k = line[len("unset "):]
            os.environ.pop(k, None)

def main():
    os.chdir(BASE_DIR)
    
    # Asegurar contexto minikube; si no existe, iniciar minikube y fijar contexto
    current_ctx = subprocess.call("kubectl config current-context | grep minikube > /dev/null 2>&1", shell=True)
    if current_ctx != 0:
        print("Iniciando Minikube...")
        subprocess.check_call("minikube start --driver=docker", shell=True)
        subprocess.call("kubectl config use-context minikube", shell=True)
        print("Minikube iniciado")
    else:
        print("Minikube detectado")
        print("Asegurando que Minikube está levantado...")
        subprocess.call("minikube start --driver=docker", shell=True)
    
    # Configurar Docker para Minikube
    print("\nConfigurando Docker para Minikube...")
    set_docker_env()
    
    # Construir imagenes desde parte_4/
    print("\nConstruyendo imagenes...")
    run_cmd("docker build -f Dockerfile.productpage -t {}/productpage .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.details -t {}/details .".format(TEAM_ID))
    run_cmd("docker build -f Dockerfile.ratings -t {}/ratings .".format(TEAM_ID))
    
    # Compilar reviews
    print("\nCompilando Reviews...")
    reviews_path = os.path.abspath(os.path.join(BASE_DIR, "bookinfo/src/reviews"))
    run_cmd('docker run --rm -u root -v "{}:/home/gradle/project" -w /home/gradle/project gradle:4.8.1 gradle clean build'.format(reviews_path))
    
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
    set_docker_env()
    
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
    
    # Iniciar minikube tunnel en background
    print("\n" + "="*60)
    print("Iniciando minikube tunnel...")
    print("="*60)
    print("NOTA: minikube tunnel requiere privilegios sudo")
    print("El proceso quedara ejecutandose en segundo plano")
    
    # Iniciar tunnel en background
    tunnel_process = subprocess.Popen(
        ["sudo", "minikube", "tunnel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar a que el LoadBalancer obtenga una IP externa
    print("\nEsperando a que el servicio obtenga una IP externa...")
    external_ip = None
    for i in range(60):
        try:
            output = subprocess.check_output(
                "kubectl get svc productpage-service -n {} -o jsonpath='{{.status.loadBalancer.ingress[0].ip}}'".format(NAMESPACE),
                shell=True,
                text=True
            )
            if output and output != "":
                external_ip = output.strip()
                break
        except:
            pass
        time.sleep(2)
    
    print("\n" + "="*60)
    print("Despliegue completado!")
    print("="*60)
    
    if external_ip:
        url = "http://{}:9080/productpage".format(external_ip)
        print("\n✓ Servicio expuesto exitosamente!")
        print("\n  URL: {}".format(url))
        print("\nAccede a la aplicacion en tu navegador (Windows o WSL)")
        print("\nNOTA: El tunel de minikube debe permanecer activo.")
        print("      Para detenerlo: sudo pkill -f 'minikube tunnel'")
    else:
        print("\n⚠ No se pudo obtener la IP externa")
        print("  Verifica el estado con: kubectl get svc -n {}".format(NAMESPACE))
        print("  Asegurate de que minikube tunnel este ejecutandose")
    
    print("="*60)

if __name__ == "__main__":
    main()
