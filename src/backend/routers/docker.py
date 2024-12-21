# main.py
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import docker

router = APIRouter()

# Initialize the Docker client
# By default, this will connect to the Docker daemon using the environment variables
# or /var/run/docker.sock (on Linux/Mac) or npipe (on Windows).
docker_client = docker.from_env()

class ContainerCreateRequest(BaseModel):
    name: str | None = None  # optional: container name

@router.get("/docker-check")
def docker_check():
    """
    Simple endpoint to check if Docker daemon is reachable.
    """
    try:
        docker_client.ping()  # If Docker is unreachable, this will raise an exception
        return {"status": "Docker daemon is up and running."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/containers")
def list_containers(all_containers: bool = False):
    """
    List containers. If all_containers=True, includes stopped containers as well.
    """
    try:
        containers = docker_client.containers.list(all=all_containers)
        return [
            {
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags or [container.image.short_id],
            }
            for container in containers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/containers")
def create_container(request: ContainerCreateRequest):
    """
    Create (run) an Alpine container. 
    Optionally set a name (if provided).
    """
    try:
        container = docker_client.containers.run(
            "alpine",
            name=request.name,
            command="sleep 3600",  # just keep the container running
            detach=True,
        )
        return {
            "message": "Alpine container created successfully!",
            "id": container.short_id,
            "name": container.name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/containers/{container_id}")
def get_container_details(container_id: str):
    """
    Retrieve a single container's details by ID or name.
    """
    try:
        container = docker_client.containers.get(container_id)
        return {
            "id": container.short_id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags or [container.image.short_id],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/containers/{container_id}/stop")
def stop_container(container_id: str):
    """
    Stop a running container by ID or name.
    """
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return {"message": f"Container '{container.short_id}' stopped."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/containers/{container_id}")
def remove_container(container_id: str):
    """
    Remove (delete) a container by ID or name.
    """
    try:
        container = docker_client.containers.get(container_id)
        container.remove(force=True)
        return {"message": f"Container '{container.short_id}' removed."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
