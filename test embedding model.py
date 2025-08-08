import os
import requests
import json
import time

# --- Configuration ---
# Ensure these match your settings in pinecone_manager.py
AZURE_ENDPOINT = "https://models.github.ai/inference"
AZURE_MODEL_NAME = "openai/text-embedding-3-small"

# IMPORTANT: Make sure your GITHUB_TOKEN is set as an environment variable
try:
    AZURE_TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError:
    print("FATAL ERROR: The GITHUB_TOKEN environment variable is not set!")
    exit()

# --- Prepare the request ---
# The actual API path is typically '/embeddings'
request_url = f"{AZURE_ENDPOINT}/embeddings"

headers = {
    # The service expects a bearer token for authentication
    "Authorization": f"Bearer {AZURE_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "input": ["hello world"],
    "model": AZURE_MODEL_NAME
}

# --- Execute the request with explicit timeout and error handling ---
print(f"Attempting to call the embedding endpoint at: {request_url}")
print("This may take up to 60 seconds...")

try:
    start_time = time.time()
    # We set an explicit timeout of 60 seconds
    response = requests.post(request_url, headers=headers, data=json.dumps(payload), timeout=60)
    end_time = time.time()

    print(f"Received a response in {end_time - start_time:.2f} seconds.")
    print(f"HTTP Status Code: {response.status_code}")

    # Check for success or failure codes
    if response.ok:
        print("\n✅ Success! The endpoint is responding correctly.")
        print("Response JSON:")
        print(response.json())
    else:
        print("\n❌ Failure! The endpoint returned an error.")
        print("Response Text:")
        print(response.text)

except requests.exceptions.Timeout:
    print("\n❌ CRITICAL: Request timed out after 60 seconds.")
    print("This confirms the service is not responding in a timely manner. The issue is very likely with the endpoint itself (a severe cold start or service outage).")

except requests.exceptions.ConnectionError as e:
    print(f"\n❌ CRITICAL: Could not connect to the server.")
    print("This may indicate a network problem, a firewall blocking the request, or that the endpoint URL is incorrect or down.")
    print(f"Error details: {e}")

except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")