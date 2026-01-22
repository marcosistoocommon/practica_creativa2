#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for deploying the bookinfo microservices application on Kubernetes (Play with Kubernetes)
Este script automatiza el despliegue de todos los microservicios en Kubernetes
"""

from __future__ import print_function
import subprocess
import time
import sys
import os

TEAM_ID = "17"
NAMESPACE = "cdps-{}".format(TEAM_ID)
KUBE_DIR = "bookinfo/platform/kube"

def run_command(command, description="", check=True, show_output=True):
    """Ejecuta un comando y maneja errores"""
    print("\n{}".format('='*60))
    print("Ejecutando: {}".format(description if description else command))
    print("{}".format('='*60))
    
    try:
        if show_output:
            result = subprocess.call(command, shell=True)
            class Result:
                def __init__(self, returncode):
                    self.returncode = returncode
                    self.stdout = ""
                    self.stderr = ""
            return Result(result)
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr
            result = Result(process.returncode, stdout, stderr)
            if result.stdout:
                print(result.stdout)
            if check and result.returncode != 0:
                sys.exit(1)
            return result
    except Exception as e:
        print("Error ejecutando comando: {}".format(e))
        if check:
            sys.exit(1)
        return None

def wait_for_pods(namespace, timeout=300):
    """Espera a que todos los pods estén en estado Running"""
    print("\nEsperando a que los pods estén listos (timeout: {}s)...".format(timeout))
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        process = subprocess.Popen(
            "kubectl get pods -n {}".format(namespace),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("\nEstado actual de los pods:")
            print(stdout)
            
            # Skip header
            lines = stdout.strip().split('\n')[1:]  
            if lines and all('Running' in line or 'Completed' in line for line in lines):
                print("\n✓ Todos los pods están listos!")
                return True
        
        time.sleep(10)
    
    print("\n✗ Timeout esperando a que los pods estén listos")
    return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Bookinfo Microservices - Kubernetes Deployment Script      ║
    ║   Play with Kubernetes / Minikube                            ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    
    print("\n1. Verificando instalación de kubectl...")
    result = run_command("kubectl version --client", "Verificar kubectl", check=False, show_output=False)
    if result.returncode != 0:
        print("✗ kubectl no está instalado o no está en el PATH")
        sys.exit(1)
    print("✓ kubectl está instalado")
    
    # Verificar que docker está instalado
    print("\n2. Verificando instalación de Docker...")
    result = run_command("docker --version", "Verificar Docker", check=False, show_output=False)
    if result.returncode != 0:
        print("✗ Docker no está instalado o no está en el PATH")
        sys.exit(1)
    print("✓ Docker está instalado")
    
    
    print("\n3. Verificando conexión al cluster de Kubernetes...")
    result = run_command("kubectl cluster-info", "Información del cluster", check=False, show_output=False)
    if result.returncode != 0:
        print("\n✗ Cluster no inicializado. Inicializando cluster de Kubernetes para Play with Kubernetes...")
        
        print("\n2a. Inicializando nodo master del cluster...")
        init_result = run_command(
            "kubeadm init --apiserver-advertise-address $(hostname -i) --pod-network-cidr 10.5.0.0/16",
            "Inicializar cluster con kubeadm",
            check=False
        )
        
        if init_result.returncode != 0:
            print("✗ Error al inicializar el cluster. ¿Estás ejecutando esto como root en Play with Kubernetes?")
            sys.exit(1)
        
        print("\n2b. Configurando kubectl...")
        run_command("mkdir -p $HOME/.kube", "Crear directorio .kube", check=False)
        run_command("cp -i /etc/kubernetes/admin.conf $HOME/.kube/config", "Copiar configuración", check=False)
        run_command("chown $(id -u):$(id -g) $HOME/.kube/config", "Ajustar permisos", check=False)
        
        print("\n2c. Inicializando red del cluster (kube-router)...")
        run_command(
            "kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/master/daemonset/kubeadm-kuberouter.yaml",
            "Configurar red del cluster"
        )
        
        print("\n✓ Cluster inicializado correctamente")
        print("⏳ Esperando a que el cluster esté completamente listo...")
        time.sleep(30)
        
        # Quitar taints del nodo master para permitir scheduling de pods
        print("\n3d. Configurando nodo master para aceptar pods...")
        run_command(
            "kubectl taint nodes --all node-role.kubernetes.io/control-plane- node-role.kubernetes.io/master-",
            "Quitar taints del nodo master",
            check=False
        )
    else:
        print("✓ Conectado al cluster de Kubernetes")
        
        # Asegurar que el nodo master puede aceptar pods
        print("\n3a. Verificando configuración del nodo...")
        run_command(
            "kubectl taint nodes --all node-role.kubernetes.io/control-plane- node-role.kubernetes.io/master-",
            "Quitar taints del nodo master (si existen)",
            check=False
        )
    
    # Construir imágenes Docker
    print("\n" + "="*60)
    print("CONSTRUCCIÓN DE IMÁGENES DOCKER")
    print("="*60)
    
    # Construir imagen de Details
    print("\n4. Construyendo imagen de Details...")
    run_command(
        "docker build -t {}/details -f Dockerfile.details .".format(TEAM_ID),
        "Construir imagen Details"
    )
    
    # Construir imagen de Ratings
    print("\n5. Construyendo imagen de Ratings...")
    run_command(
        "docker build -t {}/ratings -f Dockerfile.ratings .".format(TEAM_ID),
        "Construir imagen Ratings"
    )
    
    # Construir imagen de Productpage
    print("\n6. Construyendo imagen de Productpage...")
    run_command(
        "docker build -t {}/productpage -f Dockerfile.productpage .".format(TEAM_ID),
        "Construir imagen Productpage"
    )
    
    # Construir imágenes de Reviews (requiere compilación con Gradle)
    print("\n7. Compilando aplicación Reviews con Gradle...")
    reviews_dir = "bookinfo/src/reviews"
    current_dir = os.getcwd()
    
    if os.path.exists(reviews_dir):
        os.chdir(reviews_dir)
        run_command(
            'docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build',
            "Compilar Reviews con Gradle"
        )
        os.chdir(current_dir)
    else:
        print("✗ Directorio {} no encontrado".format(reviews_dir))
        sys.exit(1)
    
    # Construir Reviews v1
    print("\n8. Construyendo imagen de Reviews v1...")
    reviews_docker_dir = "bookinfo/src/reviews/reviews-wlpcfg"
    if os.path.exists(reviews_docker_dir):
        run_command(
            "docker build -t {}/reviews-v1 --build-arg service_version=v1 {}".format(TEAM_ID, reviews_docker_dir),
            "Construir imagen Reviews v1"
        )
    else:
        print("✗ Directorio {} no encontrado".format(reviews_docker_dir))
        sys.exit(1)
    
    # Construir Reviews v2
    print("\n9. Construyendo imagen de Reviews v2...")
    run_command(
        "docker build -t {}/reviews-v2 --build-arg service_version=v2 --build-arg enable_ratings=true {}".format(TEAM_ID, reviews_docker_dir),
        "Construir imagen Reviews v2"
    )
    
    # Construir Reviews v3
    print("\n10. Construyendo imagen de Reviews v3...")
    run_command(
        "docker build -t {}/reviews-v3 --build-arg service_version=v3 --build-arg enable_ratings=true --build-arg star_color=red {}".format(TEAM_ID, reviews_docker_dir),
        "Construir imagen Reviews v3"
    )
    
    # Listar imágenes construidas
    print("\n11. Verificando imágenes construidas...")
    run_command("docker images | grep {}".format(TEAM_ID), "Listar imágenes")
    
    print("\n" + "="*60)
    print("DESPLIEGUE EN KUBERNETES")
    print("="*60)
    
    print("\n" + "="*60)
    print("DESPLIEGUE EN KUBERNETES")
    print("="*60)
    
    if os.path.exists(KUBE_DIR):
        os.chdir(KUBE_DIR)
        print("\n✓ Cambiando al directorio: {}".format(KUBE_DIR))
    else:
        print("\n✗ Directorio {} no encontrado".format(KUBE_DIR))
        sys.exit(1)
    
    print("\n12. Creando namespace {}...".format(NAMESPACE))
    run_command("kubectl apply -f cdps-namespace.yaml", "Crear namespace {}".format(NAMESPACE))
    time.sleep(2)
    
    run_command("kubectl get namespace {}".format(NAMESPACE), "Verificar namespace")
    
    print("\n13. Desplegando microservicio Details (replicas: 4)...")
    run_command("kubectl apply -f details.yaml", "Desplegar Details")
    time.sleep(3)
    
    print("\n14. Desplegando microservicio Ratings (replicas: 3)...")
    run_command("kubectl apply -f ratings.yaml", "Desplegar Ratings")
    time.sleep(3)
    
    print("\n15. Desplegando microservicio Reviews...")
    run_command("kubectl apply -f reviews-svc.yaml", "Desplegar Reviews Service")
    time.sleep(2)
    
    print("\n16. Desplegando Reviews v1...")
    run_command("kubectl apply -f reviews-v1-deployment.yaml", "Desplegar Reviews v1")
    time.sleep(2)
    
    print("\n17. Desplegando Reviews v2...")
    run_command("kubectl apply -f reviews-v2-deployment.yaml", "Desplegar Reviews v2")
    time.sleep(2)
    
    print("\n18. Desplegando Reviews v3...")
    run_command("kubectl apply -f reviews-v3-deployment.yaml", "Desplegar Reviews v3")
    time.sleep(2)
    
    print("\n19. Desplegando microservicio Productpage (con acceso externo)...")
    run_command("kubectl apply -f productpage.yaml", "Desplegar Productpage")
    time.sleep(3)
    
    print("\n20. Verificando estado de los pods...")
    wait_for_pods(NAMESPACE, timeout=300)
    
    print("\n21. Mostrando recursos desplegados en el namespace {}...".format(NAMESPACE))
    run_command("kubectl get all -n {}".format(NAMESPACE), "Listar todos los recursos")
    
    print("\n22. Información de los Services...")
    run_command("kubectl get svc -n {}".format(NAMESPACE), "Listar Services")
    
    print("\n23. Obteniendo información de acceso externo...")
    run_command("kubectl get svc productpage-service -n {}".format(NAMESPACE), "Service Productpage")
    
    print("\n24. Estado detallado de los Pods...")
    run_command("kubectl get pods -n {} -o wide".format(NAMESPACE), "Pods detallados")
    
    print("\n25. Información de Deployments y réplicas...")
    run_command("kubectl get deployments -n {}".format(NAMESPACE), "Deployments")
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                  DESPLIEGUE COMPLETADO                        ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    Microservicios desplegados:
    ---------------------------
    ✓ Details      - 4 réplicas (Factor de replicación: 4)
    ✓ Ratings      - 3 réplicas (Factor de replicación: 3)
    ✓ Reviews v1   - 1 réplica
    ✓ Reviews v2   - 1 réplica
    ✓ Reviews v3   - 1 réplica
    ✓ Productpage  - 1 réplica (LoadBalancer para acceso externo)
    
    Comandos útiles:
    ----------------
    # Ver todos los recursos
    kubectl get all -n {0}
    
    # Ver pods en tiempo real
    kubectl get pods -n {0} -w
    
    # Ver logs de un pod específico
    kubectl logs <pod-name> -n {0}
    
    # Obtener IP externa del servicio productpage
    kubectl get svc productpage-service -n {0}
    
    # Describir un pod
    kubectl describe pod <pod-name> -n {0}
    
    # Escalar un deployment
    kubectl scale deployment <deployment-name> --replicas=<number> -n {0}
    
    # Eliminar todos los recursos
    kubectl delete namespace {0}
    
    Acceso a la aplicación:
    -----------------------
    En Play with Kubernetes: Clic en el puerto expuesto arriba
    En Minikube: minikube service productpage-service -n {0}
    En GKE: Usar la EXTERNAL-IP del servicio productpage-service
    
    Nota: En play-with-kubernetes, la IP externa puede tardar unos minutos
          en estar disponible. Si es <pending>, espera un momento y vuelve
          a ejecutar: kubectl get svc productpage-service -n {0}
    """.format(NAMESPACE))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print("\n\n✗ Error inesperado: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
