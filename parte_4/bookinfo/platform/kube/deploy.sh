#!/bin/bash

##################################################################################################
# Script de despliegue de la aplicación Bookinfo en Kubernetes
# Instrucciones:
# 1. Reemplazar <TEAM_ID> con el ID de su equipo en todos los archivos YAML
# 2. Reemplazar <GROUP_NUMBER> con el número de grupo en todos los archivos YAML
# 3. Ejecutar: chmod +x deploy.sh && ./deploy.sh
##################################################################################################

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Inicializando y desplegando Bookinfo${NC}"
echo -e "${BLUE}========================================${NC}"

# Guardar el directorio actual (parte_4/bookinfo/platform/kube)
SCRIPT_DIR="$(pwd)"

# Verificar que kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl no está instalado${NC}"
    exit 1
fi

# Detectar si estamos en Minikube
IS_MINIKUBE=false
if kubectl config current-context 2>/dev/null | grep -q "minikube"; then
    IS_MINIKUBE=true
    echo -e "${GREEN}Detectado entorno Minikube${NC}"
    
    # Construir imágenes dentro de Minikube
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Construyendo imágenes en Minikube...${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Configurar entorno Docker de Minikube
    eval $(minikube docker-env)
    
    # Navegar a la raíz de parte_4 (donde están los Dockerfiles)
    cd "$SCRIPT_DIR/../../.." || { echo -e "${RED}Error: No se encuentra la raíz de parte_4${NC}"; exit 1; }
    
    echo -e "${GREEN}Construyendo imagen productpage...${NC}"
    docker build -f Dockerfile.productpage -t 17/productpage . || { echo -e "${RED}Error construyendo productpage${NC}"; }
    
    echo -e "${GREEN}Construyendo imagen details...${NC}"
    docker build -f Dockerfile.details -t 17/details . || { echo -e "${RED}Error construyendo details${NC}"; }
    
    echo -e "${GREEN}Construyendo imagen ratings...${NC}"
    docker build -f Dockerfile.ratings -t 17/ratings . || { echo -e "${RED}Error construyendo ratings${NC}"; }
    
    echo -e "${GREEN}Construyendo imágenes de reviews (esto puede tardar)...${NC}"
    cd bookinfo/src/reviews
    
    # Compilar con Gradle usando contenedor si no existe gradle localmente
    if [ ! -f "reviews-application/build/libs/reviews-application-1.0.war" ]; then
        echo -e "${BLUE}Compilando aplicación Java con Gradle...${NC}"
        if command -v gradle &> /dev/null; then
            gradle clean build
        else
            echo -e "${YELLOW}Gradle no instalado, usando contenedor Docker...${NC}"
            docker run --rm -u root -v "$(pwd)":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build

    fi
    
    cd ../../..
    
    echo -e "${GREEN}Construyendo reviews...${NC}"
    docker build -t 17/reviews --build-arg service_version=v1 --build-arg enable_ratings=false bookinfo/src/reviews/reviews-wlpcfg || { echo -e "${RED}Error construyendo reviews${NC}"; }
    
    # Volver al directorio del script
    cd "$SCRIPT_DIR"
    
    echo -e "${GREEN}✓ Imágenes construidas exitosamente${NC}"
fi

# 0. Inicializar el cluster de Kubernetes (solo para Play with Kubernetes)
if [ "$IS_MINIKUBE" = false ]; then
    echo -e "\n${GREEN}[0/11] Verificando cluster...${NC}"
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${BLUE}Ejecutando kubeadm init...${NC}"
        kubeadm init --apiserver-advertise-address $(hostname -i) --pod-network-cidr 10.5.0.0/16
        
        # Configurar kubeconfig
        echo -e "${BLUE}Configurando kubeconfig...${NC}"
        mkdir -p $HOME/.kube
        cp /etc/kubernetes/admin.conf $HOME/.kube/config
        chown $(id -u):$(id -g) $HOME/.kube/config
        
        # Instalar kube-router para networking
        echo -e "${BLUE}Instalando kube-router (CNI)...${NC}"
        kubectl apply -f https://raw.githubusercontent.com/cloudnativelabs/kube-router/master/daemonset/kubeadm-kuberouter.yaml
        
        # Esperar a que el cluster esté listo
        echo -e "${BLUE}Esperando a que el cluster esté listo...${NC}"
        sleep 10
    fi
fi

# Verificar que el cluster está disponible
echo -e "\n${GREEN}Verificando conexión al cluster...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: No se puede conectar al cluster de Kubernetes${NC}"
    exit 1
fi
echo -e "${GREEN}Cluster encontrado correctamente${NC}"

# 1. Crear el namespace
echo -e "\n${GREEN}[1/11] Creando namespace...${NC}"
kubectl apply -f cdps-namespace.yaml

# Esperar un momento para que el namespace se cree
sleep 2

# 2. Desplegar Details (replicas: 4)
echo -e "\n${GREEN}[2/11] Desplegando Details service...${NC}"
kubectl apply -f details.yaml

# 3. Desplegar Ratings (replicas: 3)
echo -e "\n${GREEN}[3/11] Desplegando Ratings service...${NC}"
kubectl apply -f ratings.yaml

# 4. Desplegar Reviews service
echo -e "\n${GREEN}[4/11] Desplegando Reviews service...${NC}"
kubectl apply -f reviews-svc.yaml

# 5. Desplegar Reviews v1
echo -e "\n${GREEN}[5/11] Desplegando Reviews v1...${NC}"
kubectl apply -f reviews-v1-deployment.yaml

# 6. Desplegar Reviews v2
echo -e "\n${GREEN}[6/11] Desplegando Reviews v2...${NC}"
kubectl apply -f reviews-v2-deployment.yaml

# 7. Desplegar Reviews v3
echo -e "\n${GREEN}[7/11] Desplegando Reviews v3...${NC}"
kubectl apply -f reviews-v3-deployment.yaml

# 8. Desplegar Productpage (con LoadBalancer)
echo -e "\n${GREEN}[8/11] Desplegando Productpage service...${NC}"
kubectl apply -f productpage.yaml

# Esperar a que los pods estén listos
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Esperando a que los pods estén listos...${NC}"
echo -e "${BLUE}========================================${NC}"
sleep 5

# Mostrar el estado de los pods
echo -e "\n${GREEN}Estado de los pods:${NC}"
kubectl get pods -n cdps-17

# Mostrar los servicios
echo -e "\n${GREEN}Servicios desplegados:${NC}"
kubectl get services -n cdps-17

# Mostrar deployments
echo -e "\n${GREEN}Deployments:${NC}"
kubectl get deployments -n cdps-17

