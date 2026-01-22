#!/usr/bin/env python3
"""
Script for deploying the bookinfo microservices application on Kubernetes (Play with Kubernetes)
Este script automatiza el despliegue de todos los microservicios en Kubernetes
"""

import subprocess
import time
import sys
import os

TEAM_ID = "17"
NAMESPACE = "cdps-{}".format(TEAM_ID)
KUBE_DIR = "bookinfo/platform/kube"

def run_command(command, description="", check=True, show_output=True):
    """Ejecuta un comando y maneja errores"""
    print(f"\n{'='*60}")
    print(f"Ejecutando: {description if description else command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=not show_output,
            text=True
        )
        if not show_output and result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        if not show_output:
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def wait_for_pods(namespace, timeout=300):
    """Espera a que todos los pods estén en estado Running"""
    print(f"\nEsperando a que los pods estén listos (timeout: {timeout}s)...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = subprocess.run(
            f"kubectl get pods -n {namespace}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\nEstado actual de los pods:")
            print(result.stdout)
            

            lines = result.stdout.strip().split('\n')[1:]  
            if lines and all('Running' in line or 'Completed' in line for line in lines):
                print("\n✓ Todos los pods están listos!")
                return True
        
        time.sleep(10)
    
    print(f"\n✗ Timeout esperando a que los pods estén listos")
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
    
    
    print("\n2. Verificando conexión al cluster de Kubernetes...")
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
    else:
        print("✓ Conectado al cluster de Kubernetes")
    
    if os.path.exists(KUBE_DIR):
        os.chdir(KUBE_DIR)
        print(f"\n✓ Cambiando al directorio: {KUBE_DIR}")
    else:
        print(f"\n✗ Directorio {KUBE_DIR} no encontrado")
        sys.exit(1)
    
    print(f"\n3. Creando namespace {NAMESPACE}...")
    run_command(f"kubectl apply -f cdps-namespace.yaml", f"Crear namespace {NAMESPACE}")
    time.sleep(2)
    
    run_command(f"kubectl get namespace {NAMESPACE}", "Verificar namespace")
    
    print(f"\n4. Desplegando microservicio Details (replicas: 4)...")
    run_command("kubectl apply -f details.yaml", "Desplegar Details")
    time.sleep(3)
    
    print(f"\n5. Desplegando microservicio Ratings (replicas: 3)...")
    run_command("kubectl apply -f ratings.yaml", "Desplegar Ratings")
    time.sleep(3)
    
    print(f"\n6. Desplegando microservicio Reviews...")
    run_command("kubectl apply -f reviews-svc.yaml", "Desplegar Reviews Service")
    time.sleep(2)
    
    print(f"\n7. Desplegando Reviews v1...")
    run_command("kubectl apply -f reviews-v1-deployment.yaml", "Desplegar Reviews v1")
    time.sleep(2)
    
    print(f"\n8. Desplegando Reviews v2...")
    run_command("kubectl apply -f reviews-v2-deployment.yaml", "Desplegar Reviews v2")
    time.sleep(2)
    
    print(f"\n9. Desplegando Reviews v3...")
    run_command("kubectl apply -f reviews-v3-deployment.yaml", "Desplegar Reviews v3")
    time.sleep(2)
    
    print(f"\n10. Desplegando microservicio Productpage (con acceso externo)...")
    run_command("kubectl apply -f productpage.yaml", "Desplegar Productpage")
    time.sleep(3)
    
    print(f"\n11. Verificando estado de los pods...")
    wait_for_pods(NAMESPACE, timeout=300)
    
    print(f"\n12. Mostrando recursos desplegados en el namespace {NAMESPACE}...")
    run_command(f"kubectl get all -n {NAMESPACE}", "Listar todos los recursos")
    
    print(f"\n13. Información de los Services...")
    run_command(f"kubectl get svc -n {NAMESPACE}", "Listar Services")
    
    print(f"\n14. Obteniendo información de acceso externo...")
    run_command(f"kubectl get svc productpage-service -n {NAMESPACE}", "Service Productpage")
    
    print(f"\n15. Estado detallado de los Pods...")
    run_command(f"kubectl get pods -n {NAMESPACE} -o wide", "Pods detallados")
    
    print(f"\n16. Información de Deployments y réplicas...")
    run_command(f"kubectl get deployments -n {NAMESPACE}", "Deployments")
    
    print(f"""
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
    kubectl get all -n {NAMESPACE}
    
    # Ver pods en tiempo real
    kubectl get pods -n {NAMESPACE} -w
    
    # Ver logs de un pod específico
    kubectl logs <pod-name> -n {NAMESPACE}
    
    # Obtener IP externa del servicio productpage
    kubectl get svc productpage-service -n {NAMESPACE}
    
    # Describir un pod
    kubectl describe pod <pod-name> -n {NAMESPACE}
    
    # Escalar un deployment
    kubectl scale deployment <deployment-name> --replicas=<number> -n {NAMESPACE}
    
    # Eliminar todos los recursos
    kubectl delete namespace {NAMESPACE}
    
    Acceso a la aplicación:
    -----------------------
    En Play with Kubernetes: Clic en el puerto expuesto arriba
    En Minikube: minikube service productpage-service -n {NAMESPACE}
    En GKE: Usar la EXTERNAL-IP del servicio productpage-service
    
    Nota: En play-with-kubernetes, la IP externa puede tardar unos minutos
          en estar disponible. Si es <pending>, espera un momento y vuelve
          a ejecutar: kubectl get svc productpage-service -n {NAMESPACE}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
