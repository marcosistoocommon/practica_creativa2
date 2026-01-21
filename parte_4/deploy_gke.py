#!/usr/bin/env python3
"""
Script para desplegar la aplicación bookinfo en GKE con IP pública
Requisitos: gcloud SDK y kubectl instalados y configurados
"""

import subprocess
import sys
import time
import argparse
import os

# Configuración
CLUSTER_NAME = "bookinfo-cluster"
ZONE = "us-central1-a"
NUM_NODES = 3
NAMESPACE = "cdps-17"

# Obtener el directorio del script y construir la ruta a los archivos YAML
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KUBE_DIR = os.path.join(SCRIPT_DIR, "bookinfo", "platform", "kube")
SRC_DIR = os.path.join(SCRIPT_DIR, "bookinfo", "src")


def run_command(command, check=True, capture_output=False, cwd=None):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🚀 Ejecutando: {command}")
    try:
        if capture_output:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=check, cwd=cwd)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None


def check_prerequisites():
    """Verifica que gcloud y kubectl estén instalados"""
    print("\n📋 Verificando prerequisitos...")
    
    # Verificar que existe el directorio de archivos YAML
    if not os.path.exists(KUBE_DIR):
        print(f"❌ No se encuentra el directorio: {KUBE_DIR}")
        print(f"   Asegúrate de ejecutar el script desde el directorio parte_4/")
        sys.exit(1)
    print(f"✅ Directorio de archivos YAML encontrado: {KUBE_DIR}")
    
    # Verificar gcloud
    try:
        run_command("gcloud --version", capture_output=True)
        print("✅ gcloud SDK instalado")
    except:
        print("❌ gcloud SDK no encontrado. Instala Google Cloud SDK")
        sys.exit(1)
    
    # Verificar kubectl
    try:
        run_command("kubectl version --client", capture_output=True)
        print("✅ kubectl instalado")
    except:
        print("❌ kubectl no encontrado. Instala kubectl")
        sys.exit(1)


def build_docker_images(team_id="17"):
    """Construye todas las imágenes Docker necesarias"""
    print("\n🔨 Construyendo imágenes Docker...")
    print(f"   Team ID: {team_id}")
    
    # Verificar que Docker esté disponible
    try:
        run_command("docker --version", capture_output=True)
        print("✅ Docker instalado")
    except:
        print("❌ Docker no encontrado. Instala Docker")
        sys.exit(1)
    
    # 1. Construir imagen de productpage
    print("\n📦 Construyendo imagen de productpage...")
    cmd = f"docker build -t cdps-productpage:g{team_id} -f Dockerfile.productpage ."
    run_command(cmd, cwd=SCRIPT_DIR)
    print(f"✅ Imagen cdps-productpage:g{team_id} creada")
    
    # 2. Construir imagen de details
    print("\n📦 Construyendo imagen de details...")
    cmd = f"docker build -t cdps-details:g{team_id} -f Dockerfile.details ."
    run_command(cmd, cwd=SCRIPT_DIR)
    print(f"✅ Imagen cdps-details:g{team_id} creada")
    
    # 3. Construir imagen de ratings
    print("\n📦 Construyendo imagen de ratings...")
    cmd = f"docker build -t cdps-ratings:g{team_id} -f Dockerfile.ratings ."
    run_command(cmd, cwd=SCRIPT_DIR)
    print(f"✅ Imagen cdps-ratings:g{team_id} creada")
    
    # 4. Construir imágenes de reviews (requiere compilación previa con gradle)
    print("\n📦 Construyendo imágenes de reviews (v1, v2, v3)...")
    reviews_src_dir = os.path.join(SRC_DIR, "reviews")
    
    # Compilar con gradle primero
    print("   Compilando código Java con Gradle...")
    gradle_cmd = 'docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build'
    
    # En Windows, ajustar el comando para PowerShell
    if sys.platform == "win32":
        gradle_cmd = f'docker run --rm -u root -v "{reviews_src_dir}:/home/gradle/project" -w /home/gradle/project gradle:4.8.1 gradle clean build'
    
    run_command(gradle_cmd, cwd=reviews_src_dir)
    print("   ✅ Compilación de Java completada")
    
    # Construir las tres versiones de reviews
    reviews_wlpcfg_dir = os.path.join(reviews_src_dir, "reviews-wlpcfg")
    
    for version in ["v1", "v2", "v3"]:
        print(f"\n   Construyendo reviews {version}...")
        cmd = f"docker build -t cdps-reviews:{version}-g{team_id} --build-arg service_version={version} -f Dockerfile ."
        run_command(cmd, cwd=reviews_wlpcfg_dir)
        print(f"   ✅ Imagen cdps-reviews:{version}-g{team_id} creada")
    
    print("\n✅ Todas las imágenes Docker construidas exitosamente")
    
    # Mostrar las imágenes creadas
    print("\n📋 Imágenes Docker creadas:")
    run_command(f"docker images | grep cdps")


def push_images_to_gcr(project_id, team_id="17"):
    """Sube las imágenes a Google Container Registry"""
    print(f"\n📤 Subiendo imágenes a Google Container Registry...")
    print(f"   Proyecto: {project_id}")
    
    # Configurar Docker para usar gcloud como credential helper
    run_command("gcloud auth configure-docker --quiet")
    
    images = [
        f"cdps-productpage:g{team_id}",
        f"cdps-details:g{team_id}",
        f"cdps-ratings:g{team_id}",
        f"cdps-reviews:v1-g{team_id}",
        f"cdps-reviews:v2-g{team_id}",
        f"cdps-reviews:v3-g{team_id}"
    ]
    
    for image in images:
        # Etiquetar para GCR
        gcr_image = f"gcr.io/{project_id}/{image}"
        print(f"\n   Etiquetando {image} -> {gcr_image}")
        run_command(f"docker tag {image} {gcr_image}")
        
        # Subir a GCR
        print(f"   Subiendo {gcr_image}...")
        run_command(f"docker push {gcr_image}")
    
    print("\n✅ Todas las imágenes subidas a GCR")


def update_yaml_images(project_id, team_id="17"):
    """Actualiza los archivos YAML permanentemente para usar imágenes de GCR"""
    print(f"\n📝 Actualizando archivos YAML con imágenes de GCR...")
    
    # Mapeo de archivos y las imágenes que deben usar
    yaml_configs = [
        ("productpage.yaml", f"gcr.io/{project_id}/cdps-productpage:g{team_id}"),
        ("details.yaml", f"gcr.io/{project_id}/cdps-details:g{team_id}"),
        ("ratings.yaml", f"gcr.io/{project_id}/cdps-ratings:g{team_id}"),
        ("reviews-v1-deployment.yaml", f"gcr.io/{project_id}/cdps-reviews:v1-g{team_id}"),
        ("reviews-v2-deployment.yaml", f"gcr.io/{project_id}/cdps-reviews:v2-g{team_id}"),
        ("reviews-v3-deployment.yaml", f"gcr.io/{project_id}/cdps-reviews:v3-g{team_id}")
    ]
    
    for yaml_file, image in yaml_configs:
        yaml_path = os.path.join(KUBE_DIR, yaml_file)
        if os.path.exists(yaml_path):
            print(f"   Actualizando {yaml_file}...")
            
            with open(yaml_path, 'r') as f:
                content = f.read()
            
            # Reemplazar la línea de imagen
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'image:' in line and 'imagePullPolicy' not in line:
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + f'image: {image}')
                else:
                    new_lines.append(line)
            
            with open(yaml_path, 'w') as f:
                f.write('\n'.join(new_lines))
            print(f"   ✅ {yaml_file} actualizado")
        else:
            print(f"   ⚠️  Archivo no encontrado: {yaml_file}")
    
    print("✅ Archivos YAML actualizados permanentemente")


def create_cluster(project_id=None):
    """Crea el cluster de GKE"""
    print(f"\n🏗️  Creando cluster GKE '{CLUSTER_NAME}'...")
    
    cmd = f"gcloud container clusters create {CLUSTER_NAME} "
    cmd += f"--num-nodes={NUM_NODES} "
    cmd += f"--zone={ZONE} "
    cmd += "--no-enable-autoscaling "
    
    if project_id:
        cmd += f"--project={project_id} "
    
    run_command(cmd)
    print(f"✅ Cluster '{CLUSTER_NAME}' creado exitosamente")


def get_credentials():
    """Obtiene las credenciales del cluster"""
    print(f"\n🔐 Obteniendo credenciales del cluster...")
    cmd = f"gcloud container clusters get-credentials {CLUSTER_NAME} --zone={ZONE}"
    run_command(cmd)
    print("✅ Credenciales configuradas")


def verify_productpage_config():
    """Verifica que el archivo productpage.yaml esté configurado para IP pública"""
    print("\n📝 Verificando configuración del servicio productpage...")
    
    productpage_file = os.path.join(KUBE_DIR, "productpage.yaml")
    
    if not os.path.exists(productpage_file):
        print(f"❌ Archivo no encontrado: {productpage_file}")
        return False
    
    with open(productpage_file, 'r') as f:
        content = f.read()
    
    # Verificar que el tipo sea LoadBalancer
    if 'type: LoadBalancer' in content:
        print("✅ Servicio configurado como LoadBalancer (IP pública)")
        return True
    else:
        print("⚠️  El servicio no está configurado como LoadBalancer")
        return False


def deploy_namespace():
    """Crea el namespace"""
    print(f"\n📦 Creando namespace '{NAMESPACE}'...")
    namespace_file = os.path.join(KUBE_DIR, "cdps-namespace.yaml")
    
    if os.path.exists(namespace_file):
        run_command(f"kubectl apply -f {namespace_file}")
    else:
        # Crear namespace directamente si no existe el archivo
        run_command(f"kubectl create namespace {NAMESPACE}", check=False)
    
    print(f"✅ Namespace '{NAMESPACE}' creado")


def deploy_services():
    """Despliega todos los servicios"""
    print("\n🚢 Desplegando todos los servicios de Kubernetes...")
    
    yaml_files = [
        "details.yaml",
        "ratings.yaml",
        "reviews-svc.yaml",
        "reviews-v1-deployment.yaml",
        "reviews-v2-deployment.yaml",
        "reviews-v3-deployment.yaml",
        "productpage.yaml"
    ]
    
    for yaml_file in yaml_files:
        file_path = os.path.join(KUBE_DIR, yaml_file)
        if os.path.exists(file_path):
            print(f"  📄 Aplicando {yaml_file}...")
            run_command(f"kubectl apply -f {file_path}")
        else:
            print(f"  ⚠️  Archivo no encontrado: {yaml_file}")
    
    print("✅ Servicios desplegados")


def wait_for_deployment():
    """Espera a que los pods estén listos"""
    print(f"\n⏳ Esperando a que los pods estén listos...")
    
    deployments = ["productpage-v1", "details-v1", "ratings-v1"]
    
    for deployment in deployments:
        print(f"  Esperando deployment: {deployment}")
        cmd = f"kubectl wait --for=condition=available --timeout=300s deployment/{deployment} -n {NAMESPACE}"
        run_command(cmd, check=False)
    
    time.sleep(10)  # Esperar un poco más para asegurar
    print("✅ Pods listos")


def get_service_info():
    """Obtiene información de los servicios"""
    print(f"\n📊 Información de servicios en namespace '{NAMESPACE}':")
    run_command(f"kubectl get services -n {NAMESPACE}")
    
    print(f"\n📊 Pods desplegados:")
    run_command(f"kubectl get pods -n {NAMESPACE}")


def get_public_ip():
    """Obtiene la IP pública del servicio productpage"""
    print(f"\n🔍 Obteniendo IP pública del servicio productpage...")
    
    max_attempts = 12
    for attempt in range(max_attempts):
        ip = run_command(
            f"kubectl get service productpage-service -n {NAMESPACE} -o jsonpath='{{.status.loadBalancer.ingress[0].ip}}'",
            check=False,
            capture_output=True
        )
        
        if ip and ip != '':
            print(f"\n✅ IP PÚBLICA ASIGNADA: {ip}")
            print(f"🌐 Accede a la aplicación desde cualquier lugar en: http://{ip}:9080/productpage")
            return ip
        
        print(f"  Esperando asignación de IP... (intento {attempt + 1}/{max_attempts})")
        time.sleep(10)
    
    print("⚠️  No se pudo obtener la IP pública. Verifica manualmente con:")
    print(f"     kubectl get service productpage-service -n {NAMESPACE}")
    return None


def delete_cluster():
    """Elimina el cluster de GKE"""
    print(f"\n🗑️  Eliminando cluster '{CLUSTER_NAME}'...")
    cmd = f"gcloud container clusters delete {CLUSTER_NAME} --zone={ZONE} --quiet"
    run_command(cmd)
    print(f"✅ Cluster '{CLUSTER_NAME}' eliminado")


def main():
    parser = argparse.ArgumentParser(
        description="Desplegar aplicación bookinfo en GKE con IP pública"
    )
    parser.add_argument(
        "--project",
        help="ID del proyecto de Google Cloud",
        default=None
    )
    parser.add_argument(
        "--skip-cluster",
        action="store_true",
        help="Omitir creación del cluster (usar cluster existente)"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Eliminar el cluster en lugar de crearlo"
    )
    parser.add_argument(
        "--zone",
        help="Zona de GCP (default: us-central1-a)",
        default="us-central1-a"
    )
    parser.add_argument(
        "--team-id",
        help="ID del equipo (default: 17)",
        default="17"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Omitir construcción de imágenes Docker (usar imágenes existentes)"
    )
    parser.add_argument(
        "--only-build",
        action="store_true",
        help="Solo construir y subir imágenes, actualizar YAMLs (no crear cluster ni desplegar)"
    )
    
    args = parser.parse_args()
    
    global ZONE, NAMESPACE
    ZONE = args.zone
    NAMESPACE = f"cdps-{args.team_id}"
    
    print("=" * 60)
    print("🚀 DESPLIEGUE DE BOOKINFO EN GKE CON IP PÚBLICA")
    print("=" * 60)
    print(f"   Team ID: {args.team_id}")
    print(f"   Namespace: {NAMESPACE}")
    
    # Verificar prerequisitos
    check_prerequisites()
    
    if args.delete:
        delete_cluster()
        return
    
    # Obtener el project_id si no se proporciona
    if not args.project:
        print("\n📋 Obteniendo project ID de gcloud...")
        args.project = run_command("gcloud config get-value project", capture_output=True)
        print(f"   Project ID: {args.project}")
    
    if not args.project or args.project == "":
        print("❌ No se pudo obtener el project ID. Usa --project=tu-proyecto-id")
        sys.exit(1)
    
    # Construir imágenes Docker si no se omite
    if not args.skip_build:
        build_docker_images(args.team_id)
        push_images_to_gcr(args.project, args.team_id)
        update_yaml_images(args.project, args.team_id)
        
        if args.only_build:
            print("\n" + "=" * 60)
            print("✅ CONSTRUCCIÓN COMPLETADA")
            print("=" * 60)
            print("\n📝 Ahora puedes desplegar con:")
            print(f"   cd {KUBE_DIR}")
            print(f"   kubectl create namespace {NAMESPACE}")
            print(f"   kubectl apply -f .")
            print(f"   kubectl get pods -n {NAMESPACE}")
            print(f"   kubectl get service productpage-service -n {NAMESPACE}")
            return
    else:
        print("\n⏭️  Omitiendo construcción de imágenes Docker")
    
    # Crear cluster si no se omite
    if not args.skip_cluster:
        create_cluster(args.project)
    
    # Obtener credenciales
    get_credentials()
    
    # Verificar configuración de productpage
    verify_productpage_config()
    
    # Desplegar
    deploy_namespace()
    deploy_services()
    wait_for_deployment()
    get_service_info()
    
    # Obtener IP pública
    public_ip = get_public_ip()
    
    print("\n" + "=" * 60)
    print("✅ DESPLIEGUE COMPLETADO")
    print("=" * 60)
    if public_ip:
        print(f"\n🌐 URL PÚBLICA: http://{public_ip}:9080/productpage")
        print(f"   (Accesible desde cualquier navegador en Internet)")
    print(f"\n📝 Comandos útiles:")
    print(f"   Ver pods:     kubectl get pods -n {NAMESPACE}")
    print(f"   Ver services: kubectl get services -n {NAMESPACE}")
    print(f"   Logs:         kubectl logs <pod-name> -n {NAMESPACE}")
    print(f"\n   Para redesplegar:")
    print(f"   cd {KUBE_DIR}")
    print(f"   kubectl apply -f .")
    print(f"\n   Eliminar cluster: python3 deploy_gke.py --delete --team-id={args.team_id}")
    print()


if __name__ == "__main__":
    main()
