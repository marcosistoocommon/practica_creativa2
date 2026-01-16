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
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Desplegando aplicación Bookinfo${NC}"
echo -e "${BLUE}========================================${NC}"

# Verificar que kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl no está instalado${NC}"
    exit 1
fi

# Verificar que el cluster está disponible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: No se puede conectar al cluster de Kubernetes${NC}"
    exit 1
fi

# 1. Crear el namespace
echo -e "\n${GREEN}[1/8] Creando namespace...${NC}"
kubectl apply -f cdps-namespace.yaml

# Esperar un momento para que el namespace se cree
sleep 2

# 2. Desplegar Details (replicas: 4)
echo -e "\n${GREEN}[2/8] Desplegando Details service...${NC}"
kubectl apply -f details.yaml

# 3. Desplegar Ratings (replicas: 3)
echo -e "\n${GREEN}[3/8] Desplegando Ratings service...${NC}"
kubectl apply -f ratings.yaml

# 4. Desplegar Reviews service
echo -e "\n${GREEN}[4/8] Desplegando Reviews service...${NC}"
kubectl apply -f reviews-svc.yaml

# 5. Desplegar Reviews v1
echo -e "\n${GREEN}[5/8] Desplegando Reviews v1...${NC}"
kubectl apply -f reviews-v1-deployment.yaml

# 6. Desplegar Reviews v2
echo -e "\n${GREEN}[6/8] Desplegando Reviews v2...${NC}"
kubectl apply -f reviews-v2-deployment.yaml

# 7. Desplegar Reviews v3
echo -e "\n${GREEN}[7/8] Desplegando Reviews v3...${NC}"
kubectl apply -f reviews-v3-deployment.yaml

# 8. Desplegar Productpage (con LoadBalancer)
echo -e "\n${GREEN}[8/8] Desplegando Productpage service...${NC}"
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

# Obtener la IP externa del servicio productpage
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Obteniendo IP externa...${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Para acceder a la aplicación, espera a que el LoadBalancer asigne una IP externa:${NC}"
echo -e "${GREEN}kubectl get svc productpage-service -n cdps-17${NC}"
echo -e "\n${GREEN}Una vez que tengas la EXTERNAL-IP, accede a: http://<EXTERNAL-IP>:9080${NC}"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Despliegue completado!${NC}"
echo -e "${BLUE}========================================${NC}"
