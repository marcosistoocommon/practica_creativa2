import subprocess
import os
import sys

DOCKER_USER = "marcosistoocommon"
TAG = "latest"
TEAM_ID = "17"
NAMESPACE = f"cdps-{TEAM_ID}"
PROJECT_ID = "perfect-obelisk-480209-b2"
ZONE = "europe-west1-b"
CLUSTER_NAME = "bookinfo-cluster"
NUM_NODES = 3
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print("Uso: python script_4.py [create|build|run|delete|stop] [v1|v2|v3]")
    sys.exit(1)

cmd = sys.argv[1].lower()
version = sys.argv[2] if len(sys.argv) > 2 else "v1"
kube_path = os.path.join(BASE_PATH, "bookinfo", "platform", "kube")


try:
    subprocess.run("gcloud auth print-access-token", shell=True, check=True)
except subprocess.CalledProcessError:
    print("No hay sesión activa en gcloud. Ejecutando autenticación...")
    subprocess.run("gcloud auth login", shell=True, check=True)

try :
    subprocess.run("docker login", shell=True, check=True)
except subprocess.CalledProcessError:
    print("No hay sesión activa en Docker. Ejecutando autenticación...")
    subprocess.run("docker login", shell=True, check=True)


if cmd == "create":
    subprocess.run(f"gcloud config set project {PROJECT_ID}", shell=True, check=True)
    subprocess.run(f"gcloud config set compute/zone {ZONE}", shell=True, check=True)
    subprocess.run(f"gcloud container clusters create {CLUSTER_NAME} --num-nodes={NUM_NODES} --no-enable-autoscaling", shell=True, check=True)
    subprocess.run(f"gcloud container clusters get-credentials {CLUSTER_NAME}", shell=True, check=True)

elif cmd == "build":
    subprocess.run(f"docker build -t {DOCKER_USER}/details:{TAG} -f Dockerfile.details .", shell=True, check=True, cwd=BASE_PATH)
    subprocess.run(f"docker push {DOCKER_USER}/details:{TAG}", shell=True, check=True)
    subprocess.run(f"docker build -t {DOCKER_USER}/productpage:{TAG} -f Dockerfile.productpage .", shell=True, check=True, cwd=BASE_PATH)
    subprocess.run(f"docker push {DOCKER_USER}/productpage:{TAG}", shell=True, check=True)
    subprocess.run(f"docker build -t {DOCKER_USER}/ratings:{TAG} -f Dockerfile.ratings .", shell=True, check=True, cwd=BASE_PATH)
    subprocess.run(f"docker push {DOCKER_USER}/ratings:{TAG}", shell=True, check=True)
    reviews_path = os.path.join(BASE_PATH, "bookinfo", "src", "reviews")
    subprocess.run(f'docker run --rm -u root -v "{reviews_path}":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build', shell=True, check=True)
    dockerfile_dir = os.path.join(reviews_path, "reviews-wlpcfg")
    for v in ["v1", "v2", "v3"]:
        image = f"reviews-{v}"
        subprocess.run(f"docker build -t {DOCKER_USER}/{image}:{TAG} -f Dockerfile .", shell=True, check=True, cwd=dockerfile_dir)
        subprocess.run(f"docker push {DOCKER_USER}/{image}:{TAG}", shell=True, check=True)

elif cmd == "run":
    # Delete any active reviews pod and service before applying the reviews yaml
    subprocess.run(f"kubectl delete pods -l app=reviews -n {NAMESPACE} --ignore-not-found=true", shell=True, check=True)
    subprocess.run(f"kubectl delete svc reviews-svc -n {NAMESPACE} --ignore-not-found=true", shell=True, check=True)
    yamls = [
        "cdps-namespace.yaml",
        "details.yaml",
        "productpage.yaml",
        "ratings.yaml",
        "reviews-svc.yaml",
        f"reviews-{version}-deployment.yaml",
    ]
    for y in yamls:
        subprocess.run(f"kubectl apply -f {os.path.join(kube_path, y)}", shell=True, check=True)
    subprocess.run(f"kubectl get pods -n {NAMESPACE}", shell=True, check=True)
    subprocess.run(f"kubectl get services -n {NAMESPACE}", shell=True, check=True)
    subprocess.run(f"kubectl get deployments -n {NAMESPACE}", shell=True, check=True)
    # Wait for external IP
    import time
    import yaml as pyyaml
    svc_name = "productpage-service"
    external_ip = None
    print("Waiting for external IP...")
    for _ in range(60):  # wait up to 5 minutes
        svc = subprocess.run(f"kubectl get svc {svc_name} -n {NAMESPACE} -o yaml", shell=True, capture_output=True, text=True)
        if svc.returncode == 0:
            svc_yaml = pyyaml.safe_load(svc.stdout)
            status = svc_yaml.get('status', {})
            if status:
                ingress = status.get('loadBalancer', {}).get('ingress', [])
                if ingress and 'ip' in ingress[0]:
                    external_ip = ingress[0]['ip']
                    break
        time.sleep(5)
    if external_ip:
        print(f"\nLa URL de la aplicación es: http://{external_ip}:9080/")
    else:
        print("No se obtuvo una IP externa para el servicio productpage-service tras 5 minutos.")

elif cmd == "delete":
    subprocess.run(f"gcloud container clusters delete {CLUSTER_NAME} --zone {ZONE} --quiet", shell=True, check=True)

elif cmd == "stop":
    subprocess.run(f"kubectl delete namespace {NAMESPACE} --ignore-not-found=true", shell=True, check=True)

else:
    print("Comando no reconocido. Usa: create, build, run, delete, stop [v1|v2|v3]")
    sys.exit(1)

