from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import os
import requests
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

load_dotenv()

agent_bp = Blueprint('agent', __name__)

# Azure DevOps configuration
AZURE_DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

# Azure OpenAI configuration
llm = None
agent_executor = None

def initialize_agent():
    global llm, agent_executor
    if llm is None:
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0,
        )
        
        # Define the tools
        tools = [list_builds, get_build_logs, get_pipeline_definitions]
        
        # Create the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that analyzes Azure Pipeline builds. 
            You can help users understand build failures, analyze logs, and provide insights about their pipelines.
            When analyzing build logs, focus on identifying error messages, failed steps, and potential root causes.
            Provide clear, actionable recommendations when possible."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

@tool
def list_builds(project: str, definition_id: int = None, status_filter: str = None, top: int = 5) -> dict:
    """Lists builds for a given project, with optional filters for definition ID and status. If no project name given then take the default project name as UBS"""
    if not AZURE_DEVOPS_ORG_URL or not AZURE_DEVOPS_PAT:
        return {"error": "Azure DevOps configuration not found"}
    
    url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/builds?api-version=7.1"
    if definition_id:
        url += f"&definitions={definition_id}"
    if status_filter:
        url += f"&statusFilter={status_filter}"
    url += f"&$top={top}"

    try:
        response = requests.get(
            url,
            auth=("", AZURE_DEVOPS_PAT),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch builds: {str(e)}"}

@tool
def get_build_logs(project: str, build_id: int) -> str:
    """Gets the logs for a specific build."""
    if not AZURE_DEVOPS_ORG_URL or not AZURE_DEVOPS_PAT:
        return "Azure DevOps configuration not found"
    
    url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/builds/{build_id}/logs?api-version=7.1"
    
    try:
        response = requests.get(
            url,
            auth=("", AZURE_DEVOPS_PAT),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        logs_data = response.json()

        full_log_content = ""
        for log_item in logs_data.get("value", []):
            log_url = log_item.get("url")
            if log_url:
                log_response = requests.get(
                    log_url,
                    auth=("", AZURE_DEVOPS_PAT),
                    headers={"Content-Type": "application/json"}
                )
                if log_response.status_code == 200:
                    full_log_content += f"=== Log {log_item.get('id', 'Unknown')} ===\n"
                    full_log_content += log_response.text + "\n---\n"

        return full_log_content if full_log_content else "No logs found."
    except Exception as e:
        return f"Failed to fetch build logs: {str(e)}"

@tool
def get_pipeline_definitions(project: str, top: int = 10) -> dict:
    """Gets pipeline definitions for a project. if no project name given then take UBS as the project name"""
    if not AZURE_DEVOPS_ORG_URL or not AZURE_DEVOPS_PAT:
        return {"error": "Azure DevOps configuration not found"}
    
    url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/definitions?api-version=7.1&$top={top}"
    
    try:
        response = requests.get(
            url,
            auth=("", AZURE_DEVOPS_PAT),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Failed to fetch pipeline definitions: {str(e)}"}

@agent_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    """Handle chat requests with the Azure DevOps agent."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Initialize agent if not already done
        initialize_agent()
        
        if agent_executor is None:
            return jsonify({"error": "Agent not properly initialized"}), 500
        
        # Process the message with the agent
        response = agent_executor.invoke({"input": user_message})
        
        return jsonify({
            "response": response.get('output', 'No response generated'),
            "success": True
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

@agent_bp.route('/config', methods=['GET'])
@cross_origin()
def get_config():
    """Get configuration status."""
    config_status = {
        "azure_devops_configured": bool(AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PAT),
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY")),
        "org_url": AZURE_DEVOPS_ORG_URL if AZURE_DEVOPS_ORG_URL else "Not configured"
    }
    return jsonify(config_status)

@agent_bp.route('/projects', methods=['GET'])
@cross_origin()
def get_projects():
    """Get list of projects from Azure DevOps."""
    if not AZURE_DEVOPS_ORG_URL or not AZURE_DEVOPS_PAT:
        return jsonify({"error": "Azure DevOps configuration not found"}), 400
    
    url = f"{AZURE_DEVOPS_ORG_URL}/_apis/projects?api-version=7.1"
    
    try:
        response = requests.get(
            url,
            auth=("", AZURE_DEVOPS_PAT),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Failed to fetch projects: {str(e)}"}), 500

