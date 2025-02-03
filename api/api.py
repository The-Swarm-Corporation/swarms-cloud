#!/usr/bin/env python
"""
This FastAPI application exposes endpoints to create, update, delete, and fetch “swarms”.
A swarm corresponds to a user deployment: a Kubernetes Deployment (with Service and HPA)
that is built from a Docker Hub image.

Users must supply their API key via the `x-api-key` header, and they can only manage
deployments that belong to them.

Endpoints:
  - POST   /swarms/       Create a new swarm (deployment)
  - GET    /swarms/       List all swarms for the user
  - GET    /swarms/{id}   Get details of a swarm
  - PUT    /swarms/{id}   Update a swarm’s configuration
  - DELETE /swarms/{id}   Delete a swarm

Each swarm includes a name, description, Docker Hub image, and autoscaling parameters.
"""

import atexit
import os
import shutil
import tempfile
import time
import uuid
from typing import Dict, List, Optional

import docker
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pydantic import BaseModel, Field
from loguru import logger
import uvicorn
from dotenv import load_dotenv

load_dotenv()



# Configure environment variables to disable TLS.
os.environ["DOCKER_HOST"] = "unix:///var/run/docker.sock"
os.environ["DOCKER_TLS_VERIFY"] = "0"



# Load sensitive certificate data from environment variables.
CLIENT_CERT = os.environ.get("DOCKER_CLIENT_CERT") 
CLIENT_KEY = os.environ.get("DOCKER_CLIENT_KEY")
CA_CERT = os.environ.get("DOCKER_CA_CERT")


# ------------------------------------------------------------------------------
# Kubernetes Functions (Using our earlier code as building blocks)
# ------------------------------------------------------------------------------

CA_CERT = os.environ.get("DOCKER_CA_CERT")            # Your CA certificate

def create_temp_cert_dir() -> str:
    """
    Create a temporary directory with restricted permissions to hold certificate files.
    The directory will be automatically removed when the process exits.
    
    Returns:
        str: Path to the temporary directory.
    """
    temp_dir = tempfile.mkdtemp(prefix="docker_certs_", dir="/tmp")
    # Set directory permissions to 0700 so that only the owner can access it.
    os.chmod(temp_dir, 0o700)
    # Ensure the directory is removed on exit.
    atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
    logger.info("Created temporary certificate directory: {}", temp_dir)
    return temp_dir

def write_cert_file(directory: str, filename: str, content: str) -> str:
    """
    Write certificate content to a file with restricted permissions.
    
    Args:
        directory (str): The directory in which to create the file.
        filename (str): The filename.
        content (str): The PEM-encoded certificate or key.
    
    Returns:
        str: The full path to the file.
    """
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as f:
        f.write(content)
    # Set file permissions to 0600 so that only the owner can read/write.
    os.chmod(file_path, 0o600)
    logger.info("Wrote {} to {}", filename, file_path)
    return file_path

def create_docker_client_from_env_cert() -> docker.DockerClient:
    """
    Automates TLS certificate file creation from environment variables and creates
    a Docker client configured for TLS.
    
    Expects the following environment variables to be set:
      - DOCKER_CLIENT_CERT: PEM data for the client certificate.
      - DOCKER_CLIENT_KEY: PEM data for the client private key.
      - DOCKER_CA_CERT: PEM data for the CA certificate.
      - DOCKER_HOST: The Docker host URL (if not set, defaults to a provided value).
    
    Returns:
        docker.DockerClient: The configured Docker client.
    """
    # Ensure all required certificate data is available.
    if not (CLIENT_CERT and CLIENT_KEY and CA_CERT):
        logger.error("One or more certificate environment variables are missing.")
        raise ValueError("Missing certificate environment variables.")
    
    # Create a temporary directory for our cert files.
    cert_dir = create_temp_cert_dir()
    cert_path = write_cert_file(cert_dir, "cert.pem", CLIENT_CERT)
    key_path = write_cert_file(cert_dir, "key.pem", CLIENT_KEY)
    ca_cert_path = write_cert_file(cert_dir, "ca.pem", CA_CERT)
    
    # Set environment variables expected by docker.from_env()
    os.environ["DOCKER_CERT_PATH"] = cert_dir
    os.environ["DOCKER_TLS_VERIFY"] = "1"
    # Ensure DOCKER_HOST is set; if not, use a default.
    os.environ.setdefault("DOCKER_HOST", "tcp://your.docker.host:2376")
    
    try:
        # Create the Docker client using the temporary cert files.
        client = docker.from_env(client_cert=(cert_path, key_path))
        logger.info("Successfully created Docker client with TLS from temporary cert files.")
        return client
    except Exception as e:
        logger.exception("Failed to create Docker client: {}", e)
        raise


def pull_docker_image(image: str) -> None:
    """
    Pulls the specified Docker image from Docker Hub.
    """
    logger.info(f"Pulling image '{image}' from Docker Hub...")
    docker_client = create_docker_client_from_env_cert()
    logger.info(f"Docker client: {docker_client}")
    try:
        docker_client.images.pull(image)
        logger.success(f"Successfully pulled image '{image}'.")
    except docker.errors.APIError as e:
        print(f"Failed to pull image '{image}': {e}")
        raise
    
def create_deployment(deployment_name: str, image: str, container_port: int = 8080) -> None:
    """
    Creates a Kubernetes Deployment using the specified Docker Hub image.
    """

    # Load kubeconfig and initialize client
    logger.info(f"Creating deployment '{deployment_name}' with image '{image}'")
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()

    container = client.V1Container(
        name=deployment_name,
        image=image,
        ports=[client.V1ContainerPort(container_port=container_port)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "128Mi"},
            limits={"cpu": "500m", "memory": "512Mi"}
        )
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
        spec=client.V1PodSpec(containers=[container])
    )

    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": deployment_name}),
        template=template
    )

    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=spec
    )

    try:
        apps_v1_api.create_namespaced_deployment(
            namespace="default",
            body=deployment
        )
        logger.success(f"Successfully created deployment '{deployment_name}'")
    except ApiException as e:
        logger.error(f"Failed to create deployment '{deployment_name}': {e}")
        raise

def create_service(service_name: str, deployment_name: str, service_port: int = 80, target_port: int = 8080) -> None:
    """
    Creates a Kubernetes Service to expose the deployment externally.
    """
    config.load_kube_config()
    core_v1_api = client.CoreV1Api()

    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector={"app": deployment_name},
            ports=[client.V1ServicePort(
                port=service_port,
                target_port=target_port
            )],
            type="LoadBalancer"
        )
    )

    try:
        core_v1_api.create_namespaced_service(
            namespace="default",
            body=service
        )
        print(f"Service '{service_name}' created.")
    except ApiException as e:
        print(f"Error creating service: {e}")
        raise

def create_horizontal_pod_autoscaler(deployment_name: str, min_replicas: int, max_replicas: int,
                                       target_cpu_utilization_percentage: int) -> None:
    """
    Creates a Horizontal Pod Autoscaler (HPA) for the deployment.
    """
    config.load_kube_config()
    autoscaling_v1_api = client.AutoscalingV1Api()

    hpa_spec = client.V1HorizontalPodAutoscalerSpec(
        scale_target_ref=client.V1CrossVersionObjectReference(
            api_version="apps/v1",
            kind="Deployment",
            name=deployment_name
        ),
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        target_cpu_utilization_percentage=target_cpu_utilization_percentage
    )

    hpa = client.V1HorizontalPodAutoscaler(
        api_version="autoscaling/v1",
        kind="HorizontalPodAutoscaler",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=hpa_spec
    )

    try:
        autoscaling_v1_api.create_namespaced_horizontal_pod_autoscaler(
            namespace="default",
            body=hpa
        )
        print(f"HPA for '{deployment_name}' created.")
    except ApiException as e:
        print(f"Error creating HPA: {e}")
        raise

def delete_k8s_resource(api_function, name: str, resource: str) -> None:
    """
    Generic deletion for Kubernetes resources in the default namespace.
    """
    try:
        logger.info(f"Deleting {resource} '{name}' in namespace 'default'")
        api_function(name=name, namespace="default")
        logger.success(f"{resource} '{name}' deleted.")
    except ApiException as e:
        logger.error(f"Error deleting {resource} '{name}': {e}")
        raise

def delete_deployment(deployment_name: str) -> None:
    """
    Deletes a Kubernetes Deployment.
    """
    logger.info(f"Deleting deployment '{deployment_name}' in namespace 'default'")
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    delete_k8s_resource(apps_v1_api.delete_namespaced_deployment, deployment_name, "Deployment")

def delete_service(service_name: str) -> None:
    """
    Deletes a Kubernetes Service.
    """
    logger.info(f"Deleting service '{service_name}' in namespace 'default'")
    config.load_kube_config()
    core_v1_api = client.CoreV1Api()
    delete_k8s_resource(core_v1_api.delete_namespaced_service, service_name, "Service")

def delete_horizontal_pod_autoscaler(hpa_name: str) -> None:
    """
    Deletes a Kubernetes Horizontal Pod Autoscaler.
    """
    logger.info(f"Deleting HPA '{hpa_name}' in namespace 'default'")
    config.load_kube_config()
    autoscaling_v1_api = client.AutoscalingV1Api()
    delete_k8s_resource(autoscaling_v1_api.delete_namespaced_horizontal_pod_autoscaler, hpa_name, "HPA")

# ------------------------------------------------------------------------------
# API Models and In-Memory Stores
# ------------------------------------------------------------------------------

class SwarmBase(BaseModel):
    name: str = Field(..., description="Unique name for the swarm")
    description: Optional[str] = Field(None, description="Description of the swarm")
    dockerhub_image: str = Field(..., description="Docker Hub image (e.g., dockerhubuser/agent:latest)")
    min_replicas: int = Field(1, description="Minimum number of replicas for autoscaling")
    max_replicas: int = Field(5, description="Maximum number of replicas for autoscaling")
    target_cpu: int = Field(50, description="Target CPU utilization percentage for autoscaling")

class SwarmCreate(SwarmBase):
    pass

class SwarmUpdate(BaseModel):
    description: Optional[str] = None
    dockerhub_image: Optional[str] = None
    min_replicas: Optional[int] = None
    max_replicas: Optional[int] = None
    target_cpu: Optional[int] = None

class Swarm(SwarmBase):
    id: str
    owner: str  # API key of the owner
    endpoint: Optional[str] = None  # Could store the external service URL

# In-memory store for swarms: mapping swarm id to Swarm data.
swarm_store: Dict[str, Swarm] = {}

# In-memory user store: mapping API key to user information.
# In a real app, use a database and proper authentication/authorization.
users: Dict[str, Dict] = {
    "user-api-key-123": {"name": "Alice"},
    "user-api-key-456": {"name": "Bob"},
}

# ------------------------------------------------------------------------------
# API Key Dependency
# ------------------------------------------------------------------------------

def get_current_user(x_api_key: str = Header(..., alias="x-api-key")) -> str:
    """
    Validates the API key and returns the associated user ID.
    """
    if x_api_key not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return x_api_key

# ------------------------------------------------------------------------------
# FastAPI Application and Endpoints
# ------------------------------------------------------------------------------

app = FastAPI(
    title="Swarm Deployment API",
    description="API to deploy, update, and delete swarms (agent deployments) on Kubernetes.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/swarms/", response_model=Swarm, status_code=status.HTTP_201_CREATED)
def create_swarm(swarm_data: SwarmCreate, current_user: str = Depends(get_current_user)) -> Swarm:
    """
    Create a new swarm deployment. This will:
      1. Pull the Docker image from Docker Hub.
      2. Create a Kubernetes Deployment, Service, and HPA.
    """
    logger.info(f"Creating swarm with data: {swarm_data}")
    swarm_id = str(uuid.uuid4())
    deployment_name = f"swarm-{swarm_id}"
    service_name = f"svc-{swarm_id}"

    # Pull the Docker image
    pull_docker_image(swarm_data.dockerhub_image)

    # Create Kubernetes resources
    create_deployment(deployment_name, swarm_data.dockerhub_image)
    create_service(service_name, deployment_name)
    # Allow some time for deployment registration.
    time.sleep(5)
    create_horizontal_pod_autoscaler(
        deployment_name,
        min_replicas=swarm_data.min_replicas,
        max_replicas=swarm_data.max_replicas,
        target_cpu_utilization_percentage=swarm_data.target_cpu
    )

    # In a real-world scenario, you might fetch the external endpoint (e.g., from the Service status)
    endpoint = f"http://{service_name}.example.com"  # Placeholder

    swarm = Swarm(
        id=swarm_id,
        name=swarm_data.name,
        description=swarm_data.description,
        dockerhub_image=swarm_data.dockerhub_image,
        min_replicas=swarm_data.min_replicas,
        max_replicas=swarm_data.max_replicas,
        target_cpu=swarm_data.target_cpu,
        owner=current_user,
        endpoint=endpoint
    )
    swarm_store[swarm_id] = swarm
    return swarm

@app.get("/swarms/", response_model=List[Swarm])
def list_swarms(current_user: str = Depends(get_current_user)) -> List[Swarm]:
    """
    List all swarms that belong to the current user.
    """
    return [swarm for swarm in swarm_store.values() if swarm.owner == current_user]

@app.get("/swarms/{swarm_id}", response_model=Swarm)
def get_swarm(swarm_id: str, current_user: str = Depends(get_current_user)) -> Swarm:
    """
    Get details of a specific swarm.
    """
    swarm = swarm_store.get(swarm_id)
    if not swarm or swarm.owner != current_user:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return swarm

@app.put("/swarms/{swarm_id}", response_model=Swarm)
def update_swarm(swarm_id: str, swarm_update: SwarmUpdate, current_user: str = Depends(get_current_user)) -> Swarm:
    """
    Update a swarm's configuration. For simplicity, this example only supports updating
    metadata and scaling parameters. To update the image, you might need to perform a rolling update.
    """
    swarm = swarm_store.get(swarm_id)
    if not swarm or swarm.owner != current_user:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    # Update local record
    update_data = swarm_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(swarm, key, value)
    
    # For a full update, you might perform additional Kubernetes API calls to patch/update
    # the Deployment, Service, and HPA accordingly.
    swarm_store[swarm_id] = swarm
    return swarm

@app.delete("/swarms/{swarm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_swarm(swarm_id: str, current_user: str = Depends(get_current_user)) -> None:
    """
    Delete a swarm, including its Kubernetes resources.
    """
    swarm = swarm_store.get(swarm_id)
    if not swarm or swarm.owner != current_user:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    # Delete Kubernetes resources.
    deployment_name = f"swarm-{swarm_id}"
    service_name = f"svc-{swarm_id}"
    
    delete_deployment(deployment_name)
    delete_service(service_name)
    delete_horizontal_pod_autoscaler(deployment_name)

    # Remove from local store.
    del swarm_store[swarm_id]



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
# ------------------------------------------------------------------------------
# To run the application:
#
#   uvicorn main:app --reload
#
# Then use an HTTP client (or Swagger UI at http://127.0.0.1:8000/docs) to interact.
# ------------------------------------------------------------------------------
