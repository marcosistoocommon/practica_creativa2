import subprocess
import os

DOCKER_USER = "marcosistoocommon"
TAG = "latest"
TEAM_ID = "17"
NAMESPACE = f"cdps-{TEAM_ID}"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ID = "perfect-obelisk-480209-b2"  # ID de proyecto actualizado
ZONE = "europe-west1-b"
CLUSTER_NAME = "bookinfo-cluster"
NUM_NODES = 3

# Helper to run shell commands
def run(cmd, cwd=None):
    print(f"\n>>> Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"Error ejecutando: {cmd}")

# Crear cluster en GKE
def create_gke_cluster():
    run(f"gcloud config set project {PROJECT_ID}")
    run(f"gcloud config set compute/zone {ZONE}")
    run(f"gcloud container clusters create {CLUSTER_NAME} --num-nodes={NUM_NODES} --no-enable-autoscaling")
    run(f"gcloud container clusters get-credentials {CLUSTER_NAME}")

# Build y push details
def build_and_push_details():
    run(f"docker build -t {DOCKER_USER}/details:{TAG} -f Dockerfile.details .", BASE_PATH)
    run(f"docker push {DOCKER_USER}/details:{TAG}")

# Build y push productpage
def build_and_push_productpage():
    run(f"docker build -t {DOCKER_USER}/productpage:{TAG} -f Dockerfile.productpage .", BASE_PATH)
    run(f"docker push {DOCKER_USER}/productpage:{TAG}")

# Build y push ratings
def build_and_push_ratings():
    run(f"docker build -t {DOCKER_USER}/ratings:{TAG} -f Dockerfile.ratings .", BASE_PATH)
    run(f"docker push {DOCKER_USER}/ratings:{TAG}")

# Build reviews (gradle) y push reviews-v1, v2, v3
def build_and_push_reviews():
    reviews_path = os.path.join(BASE_PATH, "bookinfo", "src", "reviews")
    # Gradle build
    run(f'docker run --rm -u root -v "{reviews_path}":/home/gradle/project -w /home/gradle/project gradle:4.8.1 gradle clean build')
    dockerfile_path = os.path.join(reviews_path, "reviews-application", "Dockerfile")
    for version in ["v1", "v2", "v3"]:
        image = f"reviews-{version}"
        run(f"docker build -t {DOCKER_USER}/{image}:{TAG} -f {dockerfile_path} .", BASE_PATH)
        run(f"docker push {DOCKER_USER}/{image}:{TAG}")

# Añadir namespace y replicas a los manifiestos yaml
def patch_yaml_files():
    import yaml
    kube_path = os.path.join(BASE_PATH, "bookinfo", "platform", "kube")
    yamls = [
        ("details.yaml", 4),
        ("productpage.yaml", 1),
        ("ratings.yaml", 3),
        ("reviews-v1-deployment.yaml", 1),
        ("reviews-v2-deployment.yaml", 1),
        ("reviews-v3-deployment.yaml", 1),
    ]
    for yml, replicas in yamls:
        yml_path = os.path.join(kube_path, yml)
        with open(yml_path, 'r') as f:
            docs = list(yaml.safe_load_all(f))
        for doc in docs:
            if doc.get('kind') == 'Deployment':
                doc['metadata']['namespace'] = NAMESPACE
                doc['spec']['replicas'] = replicas
            elif doc.get('kind') == 'Service':
                doc['metadata']['namespace'] = NAMESPACE
        with open(yml_path, 'w') as f:
            yaml.dump_all(docs, f)

# Despliegue en Kubernetes
def deploy_k8s():
    kube_path = os.path.join(BASE_PATH, "bookinfo", "platform", "kube")
    yamls = [
        "cdps-namespace.yaml",  # Aplica el namespace primero
        "details.yaml",
        "productpage.yaml",
        "ratings.yaml",
        "reviews-svc.yaml",
        "reviews-v1-deployment.yaml",
        "reviews-v2-deployment.yaml",
        "reviews-v3-deployment.yaml",
    ]
    for y in yamls:
        run(f"kubectl apply -f {os.path.join(kube_path, y)}")

# Monitorización básica
def monitor():
    run(f"kubectl get pods -n {NAMESPACE}")
    run(f"kubectl get services -n {NAMESPACE}")
    run(f"kubectl get deployments -n {NAMESPACE}")

if __name__ == "__main__":
    create_gke_cluster()
    build_and_push_details()
    build_and_push_productpage()
    build_and_push_ratings()
    build_and_push_reviews()
    patch_yaml_files()
    deploy_k8s()
    monitor()

