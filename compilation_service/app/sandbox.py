# compilation_service/app/sandbox.py
import docker
import tempfile
import shutil
import os
import traceback

# Initialize the Docker client
try:
    docker_client = docker.from_env()
except docker.errors.DockerException:
    print("Error: Docker is not running or not installed properly.")
    print("Please make sure Docker Desktop is running.")
    docker_client = None

async def run_in_sandbox(source_code: str):
    """
    Runs the given source code in a secure, isolated Docker container.
    """
    if not docker_client:
        return {
            "stdout": "",
            "stderr": "Docker service is not available on the server.",
            "exit_code": -1
        }

    # Create a temporary directory on the host machine
    host_temp_dir = tempfile.mkdtemp()
    
    try:
        # Write the user's source code to a file inside the temp directory
        source_file_path = os.path.join(host_temp_dir, "test.lang")
        with open(source_file_path, "w") as f:
            f.write(source_code)

        # Define the volume mapping
        volumes = {host_temp_dir: {'bind': '/src', 'mode': 'ro'}}
        
        # The command to run inside the container
        command_to_run = ["python", "main.py", "/src/test.lang"]

        container = None
        try:
            container = docker_client.containers.run(
                image="compiler-image:latest", 
                command=command_to_run,
                volumes=volumes,
                network_disabled=True, 
                mem_limit="256m",
                # The 'cpus' argument was removed from the line below to ensure compatibility
                detach=True
            )

            # Wait for the container to finish, with a 10-second timeout
            result = container.wait(timeout=10)
            exit_code = result.get('StatusCode', -1)

            stdout = container.logs(stdout=True, stderr=False).decode('utf-8', 'ignore')
            stderr = container.logs(stdout=False, stderr=True).decode('utf-8', 'ignore')

            return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}

        except docker.errors.ContainerError as e:
            return {"stdout": "", "stderr": str(e), "exit_code": e.exit_status}
        except Exception as e:
            if container:
                container.kill()
            return {"stdout": "", "stderr": f"Execution timed out or failed: {traceback.format_exc()}", "exit_code": -1}
        finally:
            if container:
                container.remove(force=True)
    finally:
        shutil.rmtree(host_temp_dir)