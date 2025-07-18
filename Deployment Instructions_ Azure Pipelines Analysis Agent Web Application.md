# Deployment Instructions: Azure Pipelines Analysis Agent Web Application

This guide provides comprehensive instructions on how to deploy your Azure Pipelines Analysis Agent web application. The application is designed as a full-stack solution, where the Flask backend not only handles the AI agent logic but also serves the React frontend.

## 1. Understanding the Application Architecture

The application is composed of two main parts:

*   **Backend (Flask Application):** This is the core of your agent, written in Python using the Flask framework. It contains the LangChain and LangGraph logic for interacting with Azure DevOps and various LLM providers. Crucially, it is also configured to serve the static files of the React frontend.
*   **Frontend (React Application):** This is the user interface, built with React. It provides an interactive chat interface for users to communicate with the AI agent, and now includes options to select and configure different LLM providers.

**Key Point:** You only need to run the Flask backend. When the Flask application starts, it will automatically make the React frontend accessible through its web server. You do **not** need to run a separate Node.js server for the React application on your deployment server.

## 2. Prerequisites

Before you begin the deployment process, ensure you have the following:

*   **Deployment Environment:** A server or virtual machine where you can host the application. This could be a cloud instance (e.g., Azure Virtual Machine, AWS EC2, Google Cloud VM) or a private server. Ensure it has sufficient resources (CPU, RAM) for your expected usage.
*   **Python 3.9+:** Installed on your deployment server. You can verify this by running `python3 --version`.
*   **pip:** The package installer for Python. It usually comes with Python installations.
*   **Azure DevOps Access:** You will need access to your Azure DevOps organization and a Personal Access Token (PAT) with the necessary permissions to read build and pipeline information. Ensure the PAT has at least 'Build (Read)' and 'Code (Read)' permissions for comprehensive analysis.
*   **LLM Provider Access:** Depending on the LLM provider you choose, you will need the corresponding API keys, endpoints, and deployment names. The application supports Azure OpenAI, OpenAI, and Ollama.

## 3. Getting the Application Files to Your Server

You have received two zip files: `azure-pipeline-agent-backend.zip` and `azure-pipeline-agent-frontend.zip`. For deployment, you primarily need the `azure-pipeline-agent-backend.zip` as it contains the pre-built frontend files within its `src/static/` directory.

1.  **Transfer the Backend Zip File:** Copy `azure-pipeline-agent-backend.zip` to your deployment server using a tool like `scp`, `rsync`, or an FTP client. For example:

    ```bash
    scp /path/to/local/azure-pipeline-agent-backend.zip user@your_server_ip:/path/to/remote/directory
    ```

2.  **Unzip the Backend Application:** Once the file is on your server, navigate to the desired deployment directory and unzip it:

    ```bash
    cd /path/to/remote/directory
    unzip azure-pipeline-agent-backend.zip
    cd azure-pipeline-agent-backend
    ```

    This will create a directory named `azure-pipeline-agent-backend` containing all the necessary files.

## 4. Server Setup and Configuration

### 4.1. Create and Activate Python Virtual Environment

It is highly recommended to use a Python virtual environment to manage dependencies and avoid conflicts with system-wide Python packages.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.2. Install Python Dependencies

Install all the required Python libraries listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4.3. Configure Environment Variables

Create a `.env` file in the root of your `azure-pipeline-agent-backend` directory (the same directory as `requirements.txt`). This file will store your sensitive API keys and configuration details. Use the provided `.env.example` as a template.

```dotenv
# .env
AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-organization" # Replace with your Azure DevOps organization URL
AZURE_DEVOPS_PAT="your-personal-access-token" # Replace with your Azure DevOps Personal Access Token

# LLM Configuration (Choose one and uncomment/fill in)

# Azure OpenAI Configuration
# LLM_PROVIDER=azure_openai
# LLM_MODEL_NAME=gpt-4o # This should be your Azure OpenAI deployment name
# AZURE_OPENAI_API_KEY=your-azure-openai-key
# AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
# AZURE_OPENAI_API_VERSION=2024-02-01

# OpenAI Configuration
# LLM_PROVIDER=openai
# LLM_MODEL_NAME=gpt-4o-mini # Example: gpt-3.5-turbo, gpt-4, gpt-4o-mini
# OPENAI_API_KEY=your-openai-api-key

# Ollama Configuration
# LLM_PROVIDER=ollama
# LLM_MODEL_NAME=llama3 # Example: llama2, mistral, phi3
# OLLAMA_BASE_URL=http://localhost:11434
```

**Security Note:** For production environments, storing secrets directly in `.env` files is generally not recommended. Consider more secure alternatives such as environment variables managed by your deployment platform (e.g., Azure App Service, Kubernetes Secrets) or a dedicated secret management service (e.g., Azure Key Vault, HashiCorp Vault).

## 5. Running the Application

### 5.1. Development Server (for testing and local development)

For quick testing or local development, you can run the Flask development server. This is not suitable for production.

```bash
python src/main.py
```

This command will start the Flask server, typically on `http://0.0.0.0:5000`. You can then access the web application from your browser by navigating to `http://<your-server-ip>:5000`.

### 5.2. Production Deployment (Recommended)

For a robust and scalable production environment, it is highly recommended to use a production-ready WSGI (Web Server Gateway Interface) server like Gunicorn or uWSGI, in conjunction with a web server like Nginx or Apache as a reverse proxy.

#### Example with Gunicorn and Nginx

This setup provides better performance, security, and process management.

1.  **Install Gunicorn:**

    ```bash
    pip install gunicorn
    ```

2.  **Run Gunicorn:**

    Start your Flask application using Gunicorn. The `--workers` flag determines the number of worker processes, and `--bind` specifies the IP address and port to listen on.

    ```bash
    gunicorn --workers 4 --bind 0.0.0.0:5000 src.main:app
    ```

    *Note: `src.main:app` refers to the `app` object within the `main.py` file inside the `src` directory.* This command will keep your Flask application running in the background.

3.  **Configure Nginx (Reverse Proxy):**

    Nginx will act as a reverse proxy, forwarding incoming web requests to your Gunicorn-served Flask application. This allows Nginx to handle static files, SSL termination, load balancing, and other web server functionalities.

    *   **Install Nginx:**

        ```bash
        sudo apt update
        sudo apt install nginx
        ```

    *   **Create Nginx Configuration:** Create a new Nginx configuration file for your application (e.g., `/etc/nginx/sites-available/azure_agent`).

        ```nginx
        server {
            listen 80;
            server_name your_domain_or_ip; # Replace with your server's IP address or domain name

            location / {
                proxy_pass http://127.0.0.1:5000; # This should match the Gunicorn bind address
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }

            # Optional: Serve static files directly via Nginx for better performance
            # This assumes your static files are in /path/to/your/app/src/static
            # location /static/ {
            #     alias /path/to/your/app/src/static/;
            #     expires 30d;
            #     add_header Cache-Control "public, no-transform";
            # }
        }
        ```

    *   **Enable Nginx Configuration and Restart:** Create a symbolic link to enable the configuration and then test and restart Nginx.

        ```bash
        sudo ln -s /etc/nginx/sites-available/azure_agent /etc/nginx/sites-enabled/
        sudo nginx -t # Test Nginx configuration for syntax errors
        sudo systemctl restart nginx
        ```

    With this setup, users can access your application via standard HTTP on port 80 (or 443 with SSL configured), and Nginx will seamlessly forward requests to your Gunicorn-served Flask application.

## 6. Accessing the Deployed Application

Once both Gunicorn and Nginx are running, you can access the web application by navigating to your server's IP address or domain name in a web browser.

## 7. Updating the Frontend (if you make changes to the React source)

If you decide to make modifications to the original React frontend source code (in the `azure-pipeline-agent-frontend` directory), you will need to rebuild it and copy the new static files to the Flask backend's `src/static/` directory. This process is typically done on your local development machine, and then the updated backend zip file is transferred to the server.

1.  **Navigate to Frontend Directory (Local Machine):**

    ```bash
    cd /path/to/your/local/azure-pipeline-agent-frontend
    ```

2.  **Install Node.js Dependencies (if needed):**

    ```bash
    npm install # or pnpm install or yarn install
    ```

3.  **Build the React Frontend:**

    ```bash
    npm run build # This will create a `dist` directory with optimized static files
    ```

4.  **Copy Built Files to Backend Static Directory:**

    ```bash
    cp -r dist/* ../azure-pipeline-agent-backend/src/static/
    ```

5.  **Re-zip and Transfer Backend:** After copying, re-zip the `azure-pipeline-agent-backend` directory (excluding `venv` and `node_modules`) and transfer it to your server, replacing the old version. Then, restart your Gunicorn process on the server for the changes to take effect.

    ```bash
    # On your local machine
    cd /path/to/your/local/
    zip -r azure-pipeline-agent-backend.zip azure-pipeline-agent-backend/ -x "*venv*" -x "*node_modules*"
    scp azure-pipeline-agent-backend.zip user@your_server_ip:/path/to/remote/directory

    # On your server
    cd /path/to/remote/directory
    unzip -o azure-pipeline-agent-backend.zip # -o flag overwrites existing files
    sudo systemctl restart gunicorn_service # Replace with your actual Gunicorn service restart command
    ```

This revised guide should provide a clearer understanding of the deployment process.

