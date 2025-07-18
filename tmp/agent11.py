from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import os
import requests
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

load_dotenv()

agent_bp = Blueprint("agent", __name__)
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL")
AZURE_DEVOPS_PROJECT = os.getenv("AZURE_DEVOPS_PROJECT")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")

llm = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

@tool
def get_failed_step_logs_from_url(project: str, build_id: str) -> str:
    timeline_url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/builds/{build_id}/timeline?api-version=7.1-preview.1"
    timeline_response = requests.get(timeline_url, auth=("", AZURE_DEVOPS_PAT))
    if timeline_response.status_code != 200:
        return f"Failed to get timeline: {timeline_response.text}"
    timeline_data = timeline_response.json()
    failed_logs = []
    for record in timeline_data.get("records", []):
        if record.get("result") == "failed":
            log_url = record.get("log", {}).get("url")
            if log_url:
                log_response = requests.get(log_url, auth=("", AZURE_DEVOPS_PAT))
                if log_response.status_code == 200:
                    failed_logs.append(log_response.text)
                else:
                    failed_logs.append(f"Could not fetch log: {log_response.text}")
    return "\n\n".join(failed_logs)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a DevOps assistant. Use the tools available to get pipeline failure logs."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

tools = [get_failed_step_logs_from_url]
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@agent_bp.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    content = request.json
    input_text = content.get("input")
    result = agent_executor.invoke({"input": input_text})
    return jsonify(result)

@agent_bp.route("/projects", methods=["GET"])
@cross_origin()
def get_projects():
    url = f"{AZURE_DEVOPS_ORG_URL}/_apis/projects?api-version=7.1-preview.4"
    try:
        response = requests.get(
            url,
            auth=("", AZURE_DEVOPS_PAT),
            headers={"Content-Type": "application/json"}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Failed to fetch projects: {str(e)}"})

@tool
def get_failed_step_logs(project: str, build_id: str) -> str:
    url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/builds/{build_id}/timeline?api-version=7.1-preview.1"
    try:
        response = requests.get(url, auth=("", AZURE_DEVOPS_PAT))
        response.raise_for_status()
        timeline_data = response.json()
        failed_steps = []
        for record in timeline_data.get("records", []):
            if record.get("result") == "failed":
                failed_steps.append(record.get("name"))
        if not failed_steps:
            return f"No failed steps in build {build_id}."
        logs = []
        for step in failed_steps:
            log_url = f"{AZURE_DEVOPS_ORG_URL}/{project}/_apis/build/builds/{build_id}/logs/{step}?api-version=7.1-preview.1"
            res = requests.get(log_url, auth=("", AZURE_DEVOPS_PAT))
            logs.append(res.text)
        return "\n".join(logs)
    except Exception as e:
        return f"Error while fetching failed step logs: {str(e)}"

def extract_error_context(log_text: str, error_marker: str = "##[error]") -> list:
    lines = log_text.split("\n")
    error_indices = [i for i, line in enumerate(lines) if error_marker in line]
    context_snippets = []
    window = 3
    for index in error_indices:
        start = max(0, index - window)
        end = min(len(lines), index + window + 1)
        snippet = "\n".join(lines[start:end])
        context_snippets.append(snippet)
    return context_snippets