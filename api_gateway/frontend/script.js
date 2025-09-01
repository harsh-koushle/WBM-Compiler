document.addEventListener("DOMContentLoaded", () => {
    // 1. Setup CodeMirror Editor
    const editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
        lineNumbers: true,
        mode: "text/x-csharp", // C-style syntax highlighting is a good fit
        theme: "dracula",
        autoCloseBrackets: true,
    });

    // 2. Setup Playground Controls
    const runButton = document.getElementById("run-btn");
    const stopButton = document.getElementById("stop-btn");
    const saveButton = document.getElementById("save-btn");
    const outputElement = document.getElementById("output");

    // --- NEW: Backend API Configuration ---
    const API_BASE_URL = 'http://127.0.0.1:8000'; // Or an empty string '' for deployment

    /**
     * Polls the backend for the result of a compilation job.
     * @param {string} jobId - The ID of the job to poll.
     * @returns {Promise<object>} The final result of the job.
     */
    const pollForResult = async (jobId) => {
        // This function will check the job status every second until it's complete
        while (true) {
            try {
                const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/output`);
                if (response.status === 200) {
                    return await response.json(); // Success! Return the result.
                } else if (response.status === 400 || response.status === 404) {
                    // Job not ready yet, wait a second and try again.
                    await new Promise(resolve => setTimeout(resolve, 1000));
                } else {
                    // An unexpected server error occurred.
                    const errorData = await response.json();
                    return { error: `Server error: ${errorData.detail || response.statusText}` };
                }
            } catch (error) {
                return { error: `Network error while polling: ${error.message}` };
            }
        }
    };

    // --- UPDATED: "Run" Button Event Listener ---
    runButton.addEventListener("click", async () => {
        const code = editor.getValue();
        if (!code.trim()) {
            outputElement.textContent = "Please write some code before running.";
            return;
        }

        // Provide user feedback
        runButton.disabled = true;
        runButton.textContent = "Compiling...";
        outputElement.style.color = 'var(--text-secondary)';
        outputElement.textContent = "Sending code to the compiler...";

        try {
            // Step 1: Submit the job to the backend
            const submitResponse = await fetch(`${API_BASE_URL}/jobs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source_code: code }),
            });

            if (!submitResponse.ok) {
                throw new Error(`Failed to submit job. Server responded with status: ${submitResponse.status}`);
            }

            const { job_id } = await submitResponse.json();
            outputElement.textContent = `Job submitted successfully! Waiting for result...\nJob ID: ${job_id}`;

            // Step 2: Poll for the result
            const result = await pollForResult(job_id);

            // Step 3: Display the final result
            if (result.error) {
                // Display errors in a distinct color
                outputElement.style.color = '#ff8a8a'; // A light red for errors
                outputElement.textContent = result.error;
            } else {
                // Display success output
                outputElement.style.color = 'var(--text-primary)';
                // Combine standard output and standard error for a complete picture
                const finalOutput = result.stdout + (result.stderr ? `\n--- ERRORS ---\n${result.stderr}` : '');
                outputElement.textContent = finalOutput.trim() ? finalOutput : "[No output produced]";
            }

        } catch (error) {
            outputElement.style.color = '#ff8a8a';
            outputElement.textContent = `An error occurred: ${error.message}`;
        } finally {
            // Re-enable the button
            runButton.disabled = false;
            runButton.textContent = "▶ Run";
        }
    });

    // --- Mock Functionality (Unchanged) ---
    stopButton.addEventListener("click", () => {
        outputElement.textContent = "Execution stopped by user.";
        console.log("Stop button clicked");
    });

    saveButton.addEventListener("click", () => {
        const code = editor.getValue();
        outputElement.textContent = `Code saved! (mock)\n\n${code}`;
        console.log("Saved code:", code);
    });

    // --- "Copy" button functionality (Unchanged) ---
    const copyButtons = document.querySelectorAll(".copy-btn");
    copyButtons.forEach(button => {
        button.addEventListener("click", () => {
            const codeBlock = button.closest(".code-block");
            const code = codeBlock.querySelector("pre > code").innerText;
            navigator.clipboard.writeText(code).then(() => {
                button.classList.add("copied");
                setTimeout(() => button.classList.remove("copied"), 2000);
            }).catch(err => console.error("Failed to copy text: ", err));
        });
    });
});
