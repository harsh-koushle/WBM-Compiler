import asyncio
import tempfile
import shutil
import os
import traceback

async def run_in_sandbox(source_code: str):
    """
    Runs the given source code in a secure subprocess within the container.
    The container itself acts as the sandbox.
    """
    # Create a temporary directory to store the code file
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define the path for the source code file
        source_file_path = os.path.join(temp_dir, "test.lang")
        
        # Write the user's source code to the file
        with open(source_file_path, "w") as f:
            f.write(source_code)

        # The command to execute: run your compiler's main.py on the new file
        # We specify the full path to the python interpreter and the script
        command = [
            "python", 
            "compiler/main.py", 
            source_file_path
        ]

        # Create the subprocess
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to finish, with a 10-second timeout
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            
            return {
                "stdout": stdout.decode('utf-8', 'ignore'),
                "stderr": stderr.decode('utf-8', 'ignore'),
                "exit_code": proc.returncode
            }

        except asyncio.TimeoutError:
            # If it times out, kill the process
            proc.kill()
            await proc.wait()
            return {
                "stdout": "",
                "stderr": "Execution timed out after 10 seconds.",
                "exit_code": -1
            }

    except Exception as e:
        # Catch any other errors during setup
        return {
            "stdout": "",
            "stderr": f"An unexpected error occurred: {traceback.format_exc()}",
            "exit_code": -1
        }
    finally:
        # Clean up the temporary directory and file
        shutil.rmtree(temp_dir)
