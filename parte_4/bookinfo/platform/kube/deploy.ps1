# Script de despliegue de la aplicación Bookinfo en Kubernetes (PowerShell)
# Instrucciones:
# 1. Reemplazar <TEAM_ID> con el ID de su equipo en todos los archivos YAML
# 2. Reemplazar <GROUP_NUMBER> con el número de grupo en todos los archivos YAML
# 3. Ejecutar: .\deploy.ps1

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Desplegando aplicación Bookinfo" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

# Verificar que kubectl está instalado
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "Error: kubectl no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar que el cluster está disponible
try {
    kubectl cluster-info | Out-Null
} catch {
    Write-Host "Error: No se puede conectar al cluster de Kubernetes" -ForegroundColor Red
    exit 1
}

# 1. Crear el namespace
Write-Host "`n[1/8] Creando namespace..." -ForegroundColor Green
kubectl apply -f cdps-namespace.yaml

# Esperar un momento para que el namespace se cree
Start-Sleep -Seconds 2

# 2. Desplegar Details (replicas: 4)
Write-Host "`n[2/8] Desplegando Details service..." -ForegroundColor Green
kubectl apply -f details.yaml

# 3. Desplegar Ratings (replicas: 3)
Write-Host "`n[3/8] Desplegando Ratings service..." -ForegroundColor Green
kubectl apply -f ratings.yaml

# 4. Desplegar Reviews service
Write-Host "`n[4/8] Desplegando Reviews service..." -ForegroundColor Green
kubectl apply -f reviews-svc.yaml

# 5. Desplegar Reviews v1
Write-Host "`n[5/8] Desplegando Reviews v1..." -ForegroundColor Green
kubectl apply -f reviews-v1-deployment.yaml

# 6. Desplegar Reviews v2
Write-Host "`n[6/8] Desplegando Reviews v2..." -ForegroundColor Green
kubectl apply -f reviews-v2-deployment.yaml

# 7. Desplegar Reviews v3
Write-Host "`n[7/8] Desplegando Reviews v3..." -ForegroundColor Green
kubectl apply -f reviews-v3-deployment.yaml

# 8. Desplegar Productpage (con LoadBalancer)
Write-Host "`n[8/8] Desplegando Productpage service..." -ForegroundColor Green
kubectl apply -f productpage.yaml

# Esperar a que los pods estén listos
Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "Esperando a que los pods estén listos..." -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Start-Sleep -Seconds 5

# Mostrar el estado de los pods
Write-Host "`nEstado de los pods:" -ForegroundColor Green
kubectl get pods -n cdps-17

# Mostrar los servicios
Write-Host "`nServicios desplegados:" -ForegroundColor Green
kubectl get services -n cdps-17

# Mostrar deployments
Write-Host "`nDeployments:" -ForegroundColor Green
kubectl get deployments -n cdps-17

# Obtener la IP externa del servicio productpage
Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "Obteniendo IP externa..." -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host "Para acceder a la aplicación, espera a que el LoadBalancer asigne una IP externa:" -ForegroundColor Green
Write-Host "kubectl get svc productpage-service -n cdps-17" -ForegroundColor Green
Write-Host "`nUna vez que tengas la EXTERNAL-IP, accede a: http://<EXTERNAL-IP>:9080" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Blue
Write-Host "Despliegue completado!" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
