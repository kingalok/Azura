# How to Update the Frontend: Changing the Title and Rebuilding

This guide will walk you through the process of updating the frontend of your Azure Pipelines Analysis Agent, specifically changing the title displayed in the browser tab and rebuilding the React application. This process is typically done on your local development machine.

## 1. Prerequisites: Node.js and npm

To build the React frontend, you need Node.js and its package manager, `npm` (Node Package Manager), installed on your local machine. If you don't have them, you can download and install them from the official Node.js website:

*   **Download Node.js:** [https://nodejs.org/en/download/](https://nodejs.org/en/download/)

After installation, you can verify that Node.js and npm are correctly installed by opening your terminal or command prompt and running the following commands:

```bash
node -v
npm -v
```

These commands should output the installed versions of Node.js and npm, respectively.

## 2. Locate Your Frontend Project

First, navigate to the `azure-pipeline-agent-frontend` directory on your local machine. This is the directory that contains the source code for your React application.

```bash
cd /path/to/your/local/azure-pipeline-agent-frontend
```

Replace `/path/to/your/local/` with the actual path where you unzipped or cloned the `azure-pipeline-agent-frontend.zip` file.

## 3. Change the Title in `index.html`

The title displayed in the browser tab is located in the `index.html` file within the public directory of your React project. You will edit this file to change the title to "Azura - The Guardian of Pipelines".

1.  **Open `index.html`:** Use your preferred text editor (like VS Code, Sublime Text, Notepad++, etc.) to open the `index.html` file located at:

    ```
    /path/to/your/local/azure-pipeline-agent-frontend/index.html
    ```

2.  **Locate the `<title>` tag:** Inside the `<head>` section of the `index.html` file, find the `<title>` tag. It will look something like this:

    ```html
    <title>Azure Pipelines Analysis Agent</title>
    ```

3.  **Change the title:** Modify the content within the `<title>` tags to your desired new title:

    ```html
    <title>Azura - The Guardian of Pipelines</title>
    ```

4.  **Save the file:** Save the changes to `index.html`.

## 4. Install Node.js Dependencies (if needed)

If this is your first time working with the frontend project, or if you haven't installed the dependencies recently, you'll need to install them. Navigate to the `azure-pipeline-agent-frontend` directory in your terminal and run:

```bash
npm install
```

This command reads the `package.json` file and installs all the necessary JavaScript libraries and dependencies for the React project. This step only needs to be done once, or if you update the project's dependencies.

## 5. Build the React Frontend

After making changes to the source code (like `index.html` or any React components), you need to build the application. Building compiles your React code into optimized static files (HTML, CSS, JavaScript) that can be served by a web server.

While still in the `azure-pipeline-agent-frontend` directory in your terminal, run the build command:

```bash
npm run build
```

This command will create a `dist` directory (or `build` depending on the React setup) within your `azure-pipeline-agent-frontend` directory. This `dist` directory contains the optimized, production-ready static files of your frontend.

## 6. Copy Built Files to Backend Static Directory

Finally, you need to copy these newly built static files from the `dist` directory into the Flask backend's `src/static/` directory. This ensures that when your Flask application runs, it serves the updated frontend.

From your `azure-pipeline-agent-frontend` directory, execute the following command:

```bash
cp -r dist/* ../azure-pipeline-agent-backend/src/static/
```

*   `cp -r`: Copies directories recursively.
*   `dist/*`: Selects all files and subdirectories within the `dist` folder.
*   `../azure-pipeline-agent-backend/src/static/`: This is the destination path relative to your current `azure-pipeline-agent-frontend` directory.

## 7. Restart Your Flask Application

After copying the updated frontend files, you must restart your Flask application (or Gunicorn process if in production) for the changes to take effect. If you are running the development server, simply stop it (Ctrl+C) and start it again:

```bash
# Navigate to your backend directory
cd ../azure-pipeline-agent-backend

# Restart the Flask development server
python src/main.py
```

If you are using Gunicorn or another production WSGI server, you would restart that service. For example, if you configured a systemd service for Gunicorn, it might be:

```bash
sudo systemctl restart gunicorn_service_name
```

Once restarted, refresh your browser, and you should see "Azura - The Guardian of Pipelines" as the title in your browser tab!

