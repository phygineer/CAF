# main.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import docker
import subprocess
import uuid
import tarfile
from io import BytesIO
from typing import List

import docker


router = APIRouter(prefix="/docker")

# Initialize the Docker client
# By default, this will connect to the Docker daemon using the environment variables
# or /var/run/docker.sock (on Linux/Mac) or npipe (on Windows).
docker_client = docker.from_env()

class BuildRequest(BaseModel):
    languages: List[str]

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

@router.post("/build")
def build_image(build_request: BuildRequest):
    """
    Build a custom Ubuntu image with the requested languages.
    Expects JSON body like: {"languages": ["python", "java"]}
    """
    # 1. Read the template Dockerfile from disk
    with open("templates/Dockerfile.template", "r") as f:
        dockerfile_template = f.read()

    # 2. Prepare a space-separated string for LANGUAGES
    build_arg_value = " ".join(build_request.languages)

    # 3. Create a unique tag for the new Docker image (to avoid collisions)
    image_tag = f"caf-ubuntu:{uuid.uuid4().hex[:6]}"

    # 4. Build a tar archive in-memory with our Dockerfile
    #    Docker Python SDK requires a "context" tar that contains the Dockerfile at the root level
    file_obj = BytesIO()
    with tarfile.open(fileobj=file_obj, mode="w") as tar:
        dockerfile_bytes = dockerfile_template.encode("utf-8")
        dockerfile_info = tarfile.TarInfo(name="Dockerfile")
        dockerfile_info.size = len(dockerfile_bytes)
        tar.addfile(dockerfile_info, BytesIO(dockerfile_bytes))

    # Reset the file pointer to the start of the stream
    file_obj.seek(0)

    try:
        # 5. Use Docker SDK to build the image
        #    - fileobj: pass our in-memory tar
        #    - custom_context: True because we've prepared our own context tar
        #    - buildargs: pass our LANGUAGES build arg
        #    - tag: assign the unique image tag
        image, build_logs = docker_client.images.build(
            fileobj=file_obj,
            custom_context=True,
            rm=True,
            buildargs={"LANGUAGES": build_arg_value},
            tag=image_tag,
            #decode=True,  # If True, build_logs will be a generator of dicts
        )

        # 6. Optionally gather build logs into a single string for returning
        logs_output = []
        for chunk in build_logs:
            if "stream" in chunk:
                logs_output.append(chunk["stream"])
        build_output_str = "".join(logs_output)

        return {
            "success": True,
            "image_tag": image_tag,
            "build_logs": build_output_str,
        }

    except docker.errors.BuildError as e:
        # The build failed; Docker returned an error
        return {
            "success": False,
            "error": str(e),
            "build_logs": e.build_log,  # might be helpful for debugging
        }
    except Exception as e:
        # Any other exception
        return {
            "success": False,
            "error": str(e),
        }