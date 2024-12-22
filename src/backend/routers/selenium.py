from fastapi import FastAPI,APIRouter,UploadFile, HTTPException, Form
from docker.errors import NotFound, BuildError
import docker
from docker.errors import NotFound

router = APIRouter(prefix="/selenium")

docker_client = docker.from_env()

# Customize these as needed
IMAGE_NAME = "caf-selenium-grid-hub:latest"  # Built from your Dockerfile.template
CONTAINER_NAME = "caf-selenium-grid-hub"
HOST_PORT = 4444
CONTAINER_PORT = 4444
GRID_URL = f"http://localhost:{HOST_PORT}"

@router.post("/start-grid")
def start_grid():
    """
    Start Selenium Grid Hub container. If the container doesn't exist, build the image
    from Dockerfile.template and then run the container. If it exists and is stopped,
    remove it, rebuild, and run.
    """
    # 1) Check if container already exists
    try:
        existing_container = docker_client.containers.get(CONTAINER_NAME)
        if existing_container.status == "running":
            # Container exists and is running
            return {
                "message": "Selenium Grid is already running.",
                "container_id": existing_container.id[:12],
                "grid_url": GRID_URL
            }
        else:
            # Container exists but is not running
            existing_container.remove(force=True)
            # We'll rebuild to ensure we have the latest changes
            _build_image()
            container = _run_container()
            return {
                "message": "Selenium Grid (container was stopped) rebuilt & started.",
                "container_id": container.id[:12],
                "grid_url": GRID_URL,
            }
    except NotFound:
        # 2) No container found => build image & run
        _build_image()
        container = _run_container()
        return {
            "message": "Selenium Grid built & started successfully.",
            "container_id": container.id[:12],
            "grid_url": GRID_URL,
        }
    
@router.post("/stop-grid")
def stop_grid():
    """
    Stops and removes the Selenium Grid Hub container if running.
    """
    try:
        container = docker_client.containers.get(CONTAINER_NAME)
        if container.status == "running":
            container.stop()
        container.remove()
        return {"message": "Selenium Grid stopped and removed."}
    except NotFound:
        return {"message": "No Selenium Grid container is running."}


@router.get("/grid-status")
def grid_status():
    """
    Returns the current status of the Grid container (running/stopped/not found).
    """
    try:
        container = docker_client.containers.get(CONTAINER_NAME)
        return {
            "container_id": container.id[:12],
            "status": container.status,
            "grid_url": GRID_URL if container.status == "running" else None
        }
    except NotFound:
        return {"message": "No Selenium Grid container found."}
    

def _build_image():
    """
    Builds the Selenium Grid Hub Docker image from Dockerfile.template.
    """
    try:
        # We assume Dockerfile.template is in the same dir as this script.
        # Using `path="."` and specifying `dockerfile="Dockerfile.template"`.
        # decode=True returns a generator of dictionaries for the build logs.
        image, build_logs = docker_client.images.build(
            path=".",
            dockerfile="templates/selenium/Dockerfile.template",
            tag=IMAGE_NAME,
            rm=True,
            #decode=True,
        )
        # Optional: You can parse or log the build_logs here if desired
        build_output = []
        for chunk in build_logs:
            if "stream" in chunk:
                build_output.append(chunk["stream"])
        # For demonstration, just printing:
        print("".join(build_output))
    except BuildError as e:
        # BuildError: Something went wrong during the Docker build
        raise RuntimeError(f"Build failed: {e.msg}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error building image: {e}") from e


def _run_container():
    """
    Runs the Selenium Grid Hub container from the built image.
    """
    return docker_client.containers.run(
        image=IMAGE_NAME,
        name=CONTAINER_NAME,
        detach=True,
        ports={f"{CONTAINER_PORT}/tcp": HOST_PORT},
    )
