# Using Ollama as a Local LLM for Azure Pipelines Analysis Agent

This guide provides instructions on how to set up Ollama on your local machine or server and configure your Azure Pipelines Analysis Agent to use a local Large Language Model (LLM) via Ollama. Using a local LLM can help reduce API token consumption and offers more control over your data.

## 1. What is Ollama?

Ollama allows you to run open-source large language models, such as Llama 2, Mistral, and many others, locally on your machine. It bundles model weights, configuration, and data into a single package, with a simple API and command-line interface for easy interaction.

## 2. Installing Ollama

Ollama is available for Linux, macOS, and Windows. Choose the installation method appropriate for your operating system.

### 2.1. Linux Installation

To install Ollama on Linux, you can use the following one-line command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This script will download and install Ollama, setting it up as a systemd service. You can verify the installation by running:

```bash
ollama --version
```

### 2.2. macOS Installation

For macOS, Ollama provides a native application. Download the installer from the official website:

*   **Download Ollama for macOS:** [https://ollama.com/download/mac](https://ollama.com/download/mac)

After downloading, open the `.dmg` file and drag the Ollama application to your Applications folder. Once installed, Ollama will run in the background.

### 2.3. Windows Installation

For Windows, Ollama also provides a native installer. Download it from the official website:

*   **Download Ollama for Windows:** [https://ollama.com/download/windows](https://ollama.com/download/windows)

Run the installer and follow the on-screen prompts. Ollama will start automatically after installation.

## 3. Downloading LLM Models with Ollama

Once Ollama is installed, you need to download the LLM models you wish to use. Ollama provides a command-line interface to pull models from its registry. For example, to download the `llama3` model, open your terminal or command prompt and run:

```bash
ollama pull llama3
```

You can find a list of available models and their names on the Ollama models page:

*   **Ollama Models:** [https://ollama.com/library](https://ollama.com/library)

Choose a model that suits your needs and system resources. Popular choices include `llama2`, `mistral`, `phi3`, etc.

## 4. Configuring the Azure Pipelines Analysis Agent to Use Ollama

Your Azure Pipelines Analysis Agent is already designed to support Ollama. You just need to update its configuration.

1.  **Locate Your Backend Directory:** Navigate to the `azure-pipeline-agent-backend` directory on your server or local machine where your Flask application is deployed.

    ```bash
    cd /path/to/your/azure-pipeline-agent-backend
    ```

2.  **Edit the `.env` file:** Open the `.env` file in this directory using a text editor. If you don't have one, create it based on the `.env.example` file provided with the project.

    Find the section for LLM Configuration and modify it as follows:

    ```dotenv
    # .env
    # ... (your Azure DevOps configuration)

    # Ollama Configuration
    LLM_PROVIDER=ollama
    LLM_MODEL_NAME=llama3 # Replace with the model you pulled (e.g., mistral, phi3)
    OLLAMA_BASE_URL=http://localhost:11434 # Default Ollama API URL. Change if Ollama is running on a different host/port.

    # Comment out or remove other LLM configurations (Azure OpenAI, OpenAI) if you are exclusively using Ollama
    # AZURE_OPENAI_API_KEY=
    # AZURE_OPENAI_ENDPOINT=
    # AZURE_OPENAI_API_VERSION=
    # AZURE_OPENAI_DEPLOYMENT_NAME=
    # OPENAI_API_KEY=
    ```

    *   **`LLM_PROVIDER=ollama`**: This tells the backend to use the Ollama integration.
    *   **`LLM_MODEL_NAME=llama3`**: This should match the exact name of the model you pulled using `ollama pull` (e.g., `llama2`, `mistral`, `phi3`).
    *   **`OLLAMA_BASE_URL=http://localhost:11434`**: This is the default API endpoint for Ollama. If you installed Ollama on a different machine or configured it to run on a different port, update this URL accordingly. For example, if Ollama is running on a server with IP `192.168.1.100`, you would set `OLLAMA_BASE_URL=http://192.168.1.100:11434`.

3.  **Save the `.env` file.**

4.  **Restart Your Flask Application:** For the changes in the `.env` file to take effect, you must restart your Flask application. If you are running the development server, stop it (Ctrl+C) and start it again:

    ```bash
    # Navigate to your backend directory
    cd /path/to/your/azure-pipeline-agent-backend

    # Restart the Flask development server
    python src/main.py
    ```

    If you are using Gunicorn or another production WSGI server, you would restart that service (e.g., `sudo systemctl restart gunicorn_service_name`).

## 5. Interacting with the Agent via Frontend

Once Ollama is running and your backend is configured, you can access the web application through your browser. In the LLM Configuration section of the frontend, you should see "Ollama" as the selected provider and your chosen model name. You can then start interacting with the agent, and it will use your local Ollama instance for LLM inferences.

This setup allows you to leverage local LLMs for your Azure Pipelines analysis, providing flexibility and potentially reducing costs associated with cloud-based LLM APIs.


