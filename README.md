# ServiceNow AI Assistant (`snassist`) 🚀

A powerful, serverless AI agent built with **AWS Bedrock AgentCore** and **ServiceNow Table API**. 

This agent allows you to manage IT incidents using natural language. It can list, summarize, and create incidents directly in your ServiceNow Personal Developer Instance (PDI).

---

## ✨ Features
- **One-Shot Action**: Responds and acts immediately when enough information is provided.
- **Natural Language Tooling**: Uses Llama 3.1 8B to decide when to call ServiceNow.
- **Cloud-Native**: Deployed as a managed container on AWS Bedrock AgentCore.
- **Secure**: Uses environment variables and `.gitignore` to protect credentials.

---

## 🏗️ Quick Start

### 1. Prerequisites
- **AWS CLI** configured with appropriate permissions.
- **Python 3.11+** and `venv` installed.
- **ServiceNow PDI** (Personal Developer Instance).
- **Bedrock AgentCore CLI**: `pip install amazon-bedrock-agentcore`.

### 2. Setup
1. Clone the repository and navigate to the directory.
2. Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your ServiceNow credentials.

### 3. Deployment
Deploy everything to AWS with a single command:
```cmd
agentcore launch
```

---

## ⌨️ Usage

Use the provided `chat.py` helper to interact with your cloud agent:

- **List Incidents**:
  ```cmd
  python chat.py "Show me my latest incidents"
  ```
- **Create Incident**:
  ```cmd
  python chat.py "Create a ServiceNow incident: My computer monitor is flickering"
  ```

---

## 📂 Project Structure
- `agent.py`: Core agent logic and tool definitions.
- `chat.py`: CLI helper script for easy interaction.
- `Dockerfile`: Container blueprint for AWS CodeBuild.
- `.bedrock_agentcore.yaml`: AWS deployment configuration.
- `PROJECT_GUIDE.md`: Detailed architecture and resource guide.

---

## 🧹 Maintenance
- **Check Status**: `agentcore status snassist`
- **View Logs**: `aws logs tail /aws/bedrock-agentcore/runtimes/snassist-AXlQfeFnCu-DEFAULT --follow`
- **Destroy Stack**: `agentcore destroy`

---

Built with ❤️ using **AWS Bedrock** and **ServiceNow**.
