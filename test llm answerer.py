import os
import sys
from dotenv import load_dotenv

# --- SCRIPT SETUP ---
print("--- Testing LLM Answerer Module ---")

# 1. Load environment variables from a .env file
load_dotenv()

# 2. Crucial check for the API key
if "GITHUB_TOKEN" not in os.environ:
    print("\n[FATAL ERROR] GITHUB_TOKEN environment variable not found.")
    print("Please ensure you have a .env file in the same directory as this script,")
    print("with your API key like this: GITHUB_TOKEN='your_key_here'")
    sys.exit(1) # Exit the script if the key is not found
else:
    print("\n[INFO] GITHUB_TOKEN loaded successfully.")

# We import the function *after* checking for the key.
from services.llm_answerer import generate_answer

# --- TEST DATA ---
# This simulates the data that would normally come from your other services.
test_question = "What is the grace period for premium payments?"

test_context_chunks = [
    "Clause 5.1 states that the Insured Person must pay the premium on the due date.",
    "A grace period of thirty (30) days is provided for payment of the premium after the due date specified in the Schedule, to renew or continue the policy without loss of continuity benefits.",
    "During the grace period, the Company shall not be liable to pay for any claim for an event that occurs, for which the signs or symptoms first occur or treatment is first sought.",
    "Pre-existing diseases are covered only after a waiting period of 36 months of continuous coverage has elapsed since the inception of the first policy."
]

print(f"\n[INFO] Test Question: '{test_question}'")
print("[INFO] Test Context: A list of 4 text chunks has been prepared.")


# --- RUN THE TEST ---
print("\n[INFO] Calling the generate_answer() function. This may take a moment...")
try:
    # Call the function with the test data
    answer, rationale = generate_answer(test_question, test_context_chunks)

    # --- PRINT RESULTS ---
    print("\n--------------------")
    print("✅  SUCCESS: Received a response from the LLM.")
    print("--------------------")

    print("\n[Answer Parsed]")
    print(f"{answer}")

    print("\n[Rationale Parsed]")
    print(f"{rationale}")
    print("\n--------------------")
    print("Test complete.")

except Exception as e:
    print("\n--------------------")
    print(f"❌  FAILURE: An error occurred while calling the LLM.")
    print("--------------------")
    print(f"Error details: {e}")
    print("\nThis could be due to an invalid API key, a service outage, or a rate limit error.")