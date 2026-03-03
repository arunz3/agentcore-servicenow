import os
import httpx
import boto3
import json
from dotenv import load_dotenv
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Load configuration (for local testing, cloud will use actual env variables)
load_dotenv()

app = BedrockAgentCoreApp()

# --- SERVICENOW CLIENT (Self-Contained) ---
class ServiceNowClient:
    def __init__(self):
        self.instance = os.getenv("SN_INSTANCE_URL", "").rstrip('/')
        self.user = os.getenv("SN_USERNAME")
        self.pwd = os.getenv("SN_PASSWORD")
        self.base_url = f"{self.instance}/api/now/table"
        self.auth = (self.user, self.pwd)

    async def list_incidents(self, limit=5):
        async with httpx.AsyncClient() as client:
            params = {"sysparm_limit": limit, "sysparm_query": "ORDERBYDESCsys_updated_on"}
            resp = await client.get(f"{self.base_url}/incident", auth=self.auth, params=params)
            resp.raise_for_status()
            data = resp.json().get("result", [])
            return [{"number": i.get("number"), "short_description": i.get("short_description"), "state": i.get("state")} for i in data]

    async def create_incident(self, short_description, description="Created via AI Agent"):
        async with httpx.AsyncClient() as client:
            payload = {"short_description": short_description, "description": description}
            resp = await client.post(f"{self.base_url}/incident", auth=self.auth, json=payload)
            resp.raise_for_status()
            return resp.json().get("result")

sn = ServiceNowClient()

# --- AGENT ENTRYPOINT ---
@app.entrypoint
async def handle_request(request):
    try:
        # Re-initialize client to ensure cloud env vars are loaded
        sn = ServiceNowClient()
        
        # Accept 'input' (our CLI) or 'prompt' (AWS Console)
        user_input = request.get("input") or request.get("prompt") or "Hello"
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.meta.llama3-1-8b-instruct-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        print(f"Agent Processing Cloud Request: '{user_input}'")

        client = boto3.client("bedrock-runtime", region_name=region)

        # 1. Define Tools
        tools = [{
            "toolSpec": {
                "name": "list_incidents",
                "description": "List recent incidents from ServiceNow",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Number of incidents to fetch"}
                        }
                    }
                }
            }
        }, {
            "toolSpec": {
                "name": "create_incident",
                "description": "Create a new incident in ServiceNow",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "short_description": {"type": "string", "description": "The title of the incident"},
                            "description": {"type": "string", "description": "The detailed description"}
                        },
                        "required": ["short_description"]
                    }
                }
            }
        }]

        system_prompt = (
            "You are a helpful ServiceNow IT Assistant. Your goal is to help the user manage their IT incidents. "
            "1. When listing incidents, always summarize the key details (Number, Short Description, State) clearly in your final response. "
            "2. When creating an incident, if the user provides a summary or short description, CALL the 'create_incident' tool IMMEDIATELY. "
            "3. Use the user's input for both 'short_description' and 'description' if only one is provided. Do NOT ask for more details or confirmation."
            "4. Confirm the results (like INC number) to the user after the tool call."
        )

        # Turn 1: Initial call
        messages = [{"role": "user", "content": [{"text": user_input}]}]
        response = client.converse(
            modelId=model_id,
            messages=messages,
            toolConfig={"tools": tools},
            system=[{"text": system_prompt}]
        )

        resp_msg = response['output']['message']
        messages.append(resp_msg)
        
        # Check for tool use
        tool_use_item = next((c['toolUse'] for c in resp_msg['content'] if 'toolUse' in c), None)
        
        if not tool_use_item:
            return {"output": resp_msg['content'][0].get('text', "")}

        # Execute Tool
        name = tool_use_item['name']
        tool_id = tool_use_item['toolUseId']
        args = tool_use_item['input']
        
        print(f"Executing cloud action: {name}({args})")
        
        if name == "list_incidents":
            result_data = await sn.list_incidents(limit=args.get("limit", 5))
        elif name == "create_incident":
            result_data = await sn.create_incident(args.get("short_description"), args.get("description", ""))
        else:
            result_data = "Error: Tool not found"

        # Turn 2: Finish conversation
        messages.append({
            "role": "user",
            "content": [{
                "toolResult": {
                    "toolUseId": tool_id,
                    "content": [{"json": {"result": result_data}}]
                }
            }]
        })

        final_response = client.converse(
            modelId=model_id,
            messages=messages,
            toolConfig={"tools": tools},  # Required in all turns if using tools
            system=[{"text": system_prompt}]
        )

        return {"output": final_response['output']['message']['content'][0].get('text', "")}

    except Exception as e:
        import traceback
        err_msg = f"Cloud Execution Error: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        return {"output": err_msg}

if __name__ == "__main__":
    app.run()
