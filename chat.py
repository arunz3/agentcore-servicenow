import sys
import subprocess
import json

def chat():
    if len(sys.argv) < 2:
        print("Usage: python chat.py \"Your message here\"")
        return

    user_message = " ".join(sys.argv[1:])
    
    # Perfectly format the payload
    payload = json.dumps({"input": user_message})
    
    print(f"🚀 Sending to snassist: '{user_message}'...")
    
    # Run the invoke command safely
    subprocess.run(["agentcore", "invoke", payload], shell=True)

if __name__ == "__main__":
    chat()
