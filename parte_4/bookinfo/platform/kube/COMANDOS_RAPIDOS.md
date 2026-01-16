# Comandos Rápidos - Kubernetes Bookinfo

## 🚀 Despliegue Inicial

### Opción 1: Script automatizado (Windows)
```powershell
cd bookinfo\platform\kube
.\deploy.ps1
```

### Opción 2: Script automatizado (Linux/Mac)
```bash
cd bookinfo/platform/kube
chmod +x deploy.sh
./deploy.sh
```

### Opción 3: Manual paso a paso
```bash
kubectl apply -f cdps-namespace.yaml
kubectl apply -f details.yaml
kubectl apply -f ratings.yaml
kubectl apply -f reviews-svc.yaml
kubectl apply -f reviews-v1-deployment.yaml
kubectl apply -f reviews-v2-deployment.yaml
kubectl apply -f reviews-v3-deployment.yaml
kubectl apply -f productpage.yaml
```

---

## 📊 Monitoreo

### Ver todos los pods
```bash
kubectl get pods -n cdps-<TEAM_ID>
```

### Ver pods en tiempo real (watch mode)
```bash
kubectl get pods -n cdps-<TEAM_ID> -w
```

### Ver deployments
```bash
kubectl get deployments -n cdps-<TEAM_ID>
```

### Ver servicios
```bash
kubectl get services -n cdps-<TEAM_ID>
```

### Ver todo junto
```bash
kubectl get all -n cdps-<TEAM_ID>
```

### Ver estado detallado de un pod
```bash
kubectl describe pod <pod-name> -n cdps-<TEAM_ID>
```

### Ver logs de un pod
```bash
kubectl logs <pod-name> -n cdps-<TEAM_ID>
```

### Ver logs en tiempo real
```bash
kubectl logs -f <pod-name> -n cdps-<TEAM_ID>
```

### Ver logs de todos los pods de un deployment
```bash
kubectl logs -l app=details -n cdps-<TEAM_ID> --tail=50
```

---

## 🔄 Escalado

### Escalar Details a 6 réplicas
```bash
kubectl scale deployment details-v1 --replicas=6 -n cdps-<TEAM_ID>
```

### Escalar Ratings a 5 réplicas
```bash
kubectl scale deployment ratings-v1 --replicas=5 -n cdps-<TEAM_ID>
```

### Escalar Productpage a 3 réplicas
```bash
kubectl scale deployment productpage-v1 --replicas=3 -n cdps-<TEAM_ID>
```

### Ver el estado del escalado
```bash
kubectl get deployments -n cdps-<TEAM_ID>
kubectl get pods -n cdps-<TEAM_ID> | grep details
```

---

## 🌐 Acceso a la Aplicación

### Obtener IP externa (GKE)
```bash
kubectl get svc productpage-service -n cdps-<TEAM_ID>
```

### Watch hasta que aparezca la IP externa
```bash
kubectl get svc productpage-service -n cdps-<TEAM_ID> -w
```

### Minikube - Opción 1: minikube service
```bash
minikube service productpage-service -n cdps-<TEAM_ID>
```

### Minikube - Opción 2: port-forward
```bash
kubectl port-forward svc/productpage-service 9080:9080 -n cdps-<TEAM_ID>
# Luego accede a: http://localhost:9080
```

### Minikube - Opción 3: tunnel (en otra terminal)
```bash
minikube tunnel
```

---

## 🐛 Troubleshooting

### Ver eventos del namespace
```bash
kubectl get events -n cdps-<TEAM_ID> --sort-by='.lastTimestamp'
```

### Ejecutar un shell dentro de un pod
```bash
kubectl exec -it <pod-name> -n cdps-<TEAM_ID> -- /bin/sh
```

### Probar conectividad entre servicios
```bash
kubectl exec -it <productpage-pod> -n cdps-<TEAM_ID> -- curl details-service:9080
kubectl exec -it <productpage-pod> -n cdps-<TEAM_ID> -- curl reviews-service:9080
kubectl exec -it <reviews-pod> -n cdps-<TEAM_ID> -- curl ratings-service:9080
```

### Ver recursos consumidos por los pods
```bash
kubectl top pods -n cdps-<TEAM_ID>
```

### Ver recursos del cluster
```bash
kubectl top nodes
```

### Reiniciar un deployment (rolling restart)
```bash
kubectl rollout restart deployment details-v1 -n cdps-<TEAM_ID>
```

### Ver historial de rollouts
```bash
kubectl rollout history deployment details-v1 -n cdps-<TEAM_ID>
```

### Ver información del cluster
```bash
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>
```

---

## 🔄 Actualización de Imágenes

### Actualizar imagen de un deployment
```bash
kubectl set image deployment/details-v1 details=<GROUP_NUMBER>/details:v2 -n cdps-<TEAM_ID>
```

### Ver estado de la actualización
```bash
kubectl rollout status deployment details-v1 -n cdps-<TEAM_ID>
```

### Revertir a la versión anterior
```bash
kubectl rollout undo deployment details-v1 -n cdps-<TEAM_ID>
```

---

## 📝 Edición

### Editar un deployment directamente
```bash
kubectl edit deployment details-v1 -n cdps-<TEAM_ID>
```

### Aplicar cambios desde archivo modificado
```bash
kubectl apply -f details.yaml
```

---

## 🧹 Limpieza

### Eliminar un deployment específico
```bash
kubectl delete deployment details-v1 -n cdps-<TEAM_ID>
```

### Eliminar un servicio específico
```bash
kubectl delete service details-service -n cdps-<TEAM_ID>
```

### Eliminar recursos por archivo
```bash
kubectl delete -f details.yaml
```

### Eliminar TODO el namespace (CUIDADO!)
```bash
kubectl delete namespace cdps-<TEAM_ID>
```

### Eliminar todos los recursos del namespace sin eliminar el namespace
```bash
kubectl delete all --all -n cdps-<TEAM_ID>
```

---

## 📦 Configuración Inicial (GKE)

### Crear cluster GKE con 3 nodos
```bash
gcloud container clusters create bookinfo-cluster \
  --num-nodes=3 \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --no-enable-autoscaling
```

### Conectarse al cluster
```bash
gcloud container clusters get-credentials bookinfo-cluster --zone=us-central1-a
```

### Ver contextos disponibles
```bash
kubectl config get-contexts
```

### Cambiar de contexto
```bash
kubectl config use-context <context-name>
```

---

## 📦 Configuración Inicial (Minikube)

### Iniciar Minikube
```bash
minikube start --nodes=3 --driver=docker
```

### Ver estado de Minikube
```bash
minikube status
```

### Acceder al dashboard
```bash
minikube dashboard
```

### Detener Minikube
```bash
minikube stop
```

### Eliminar Minikube
```bash
minikube delete
```

---

## 📊 Comandos para la Memoria

### Capturar estado completo del despliegue
```bash
# Pods
kubectl get pods -n cdps-<TEAM_ID> -o wide > pods-status.txt

# Deployments
kubectl get deployments -n cdps-<TEAM_ID> -o wide > deployments-status.txt

# Services
kubectl get services -n cdps-<TEAM_ID> -o wide > services-status.txt

# Todo junto
kubectl get all -n cdps-<TEAM_ID> > all-resources.txt

# Eventos
kubectl get events -n cdps-<TEAM_ID> --sort-by='.lastTimestamp' > events.txt
```

### Ver en formato YAML (para análisis)
```bash
kubectl get deployment details-v1 -n cdps-<TEAM_ID> -o yaml
kubectl get service details-service -n cdps-<TEAM_ID> -o yaml
```

### Ver en formato JSON
```bash
kubectl get pods -n cdps-<TEAM_ID> -o json
```

---

## 🎯 Tips Útiles

### Alias útiles (añadir a ~/.bashrc o ~/.zshrc)
```bash
alias k='kubectl'
alias kgp='kubectl get pods -n cdps-<TEAM_ID>'
alias kgs='kubectl get services -n cdps-<TEAM_ID>'
alias kgd='kubectl get deployments -n cdps-<TEAM_ID>'
alias kl='kubectl logs -n cdps-<TEAM_ID>'
alias kdesc='kubectl describe -n cdps-<TEAM_ID>'
```

### Autocompletado de kubectl (Bash)
```bash
source <(kubectl completion bash)
echo "source <(kubectl completion bash)" >> ~/.bashrc
```

### Autocompletado de kubectl (PowerShell)
```powershell
kubectl completion powershell | Out-String | Invoke-Expression
```

---

## 📱 Acceso Rápido

Una vez desplegado, accede a:

**GKE:**
```
http://<EXTERNAL-IP>:9080
```

**Minikube:**
```
http://localhost:9080  (con port-forward)
```

---

## ⚠️ Notas Importantes

1. Reemplaza `<TEAM_ID>` con tu ID de equipo en todos los comandos
2. Reemplaza `<GROUP_NUMBER>` con tu número de grupo en las imágenes Docker
3. Los comandos asumen que estás en el directorio `bookinfo/platform/kube`
4. Para Minikube, algunos comandos pueden requerir adaptación

---

**Última actualización:** Enero 2026
