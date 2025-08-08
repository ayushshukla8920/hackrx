# test_accuracy.py

import requests
import os
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import sys

# --- SCRIPT SETUP ---
print("--- Final Hackathon Accuracy Test Script ---")
load_dotenv()

try:
    from services.pinecone_manager import get_embeddings
except (ImportError, ModuleNotFoundError):
    print("\n[FATAL ERROR] Could not import 'get_embeddings'. Make sure this script is in your project's root directory.")
    sys.exit(1)

# --- CONFIGURATION ---
API_ENDPOINT = "http://127.0.0.1:3200/api/v1/hackrx/run"
DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
SIMILARITY_THRESHOLD = 0.90

# --- GOLDEN DATASET (as provided) ---
QUESTIONS_TO_TEST = [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?",
    "What is the No Claim Discount (NCD) offered in this policy?",
    "Is there a benefit for preventive health check-ups?",
    "How does the policy define a 'Hospital'?",
    "What is the extent of coverage for AYUSH treatments?",
    "Are there any sub-limits on room rent and ICU charges for Plan A?"
]

EXPECTED_ANSWERS = [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
    "The policy has a specific waiting period of two (2) years for cataract surgery.",
    "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
    "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
    "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
    "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
    "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
    "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
]

def calculate_similarity(embedding1, embedding2):
    """Calculates the cosine similarity between two embeddings."""
    return cosine_similarity(np.array(embedding1).reshape(1, -1), np.array(embedding2).reshape(1, -1))[0][0]

def run_test():
    """Runs the full accuracy test suite by sending all questions at once."""
    passed_tests = 0
    total_tests = len(QUESTIONS_TO_TEST)

    print("\n--- Sending a single API request with all 10 questions ---")
    
    try:
        # 1. Call your API once with the full payload
        payload = {"documents": DOCUMENT_URL, "questions": QUESTIONS_TO_TEST}
        response = requests.post(API_ENDPOINT, json=payload, timeout=90) # Increased timeout for a large request
        response.raise_for_status()

        response_data = response.json()
        generated_answers = response_data["answers"]

        if len(generated_answers) != total_tests:
            print(f"\n❌ FATAL ERROR: The API returned {len(generated_answers)} answers, but {total_tests} were expected.")
            return

        print("\n--- Comparing each generated answer to the expected answer ---")
        # 2. Loop through the results to compare each answer
        for i, (gen_ans, exp_ans) in enumerate(zip(generated_answers, EXPECTED_ANSWERS)):
            print(f"\n--- Test {i+1}/{total_tests} ---")
            print(f"Question: {QUESTIONS_TO_TEST[i]}")
            print(f"  - Generated Answer: {gen_ans}")
            print(f"  - Expected Answer:  {exp_ans}")

            embeddings = get_embeddings([gen_ans, exp_ans])
            similarity_score = calculate_similarity(embeddings[0], embeddings[1])
            print(f"  - Semantic Similarity Score: {similarity_score:.4f}")

            if similarity_score >= SIMILARITY_THRESHOLD:
                print("  - Result: ✅ PASSED")
                passed_tests += 1
            else:
                print(f"  - Result: ❌ FAILED (Similarity is below the {SIMILARITY_THRESHOLD} threshold)")

    except requests.exceptions.Timeout:
        print("\n❌ FAILED (The API call timed out after 90 seconds)")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ FAILED (The API call failed: {e})")
        try:
            print(f"  - Server Response: {response.text}")
        except:
            pass
    except Exception as e:
        print(f"\n❌ FAILED (An unexpected error occurred: {e})")

    print("\n--- Test Suite Complete ---")
    print(f"Final Score: {passed_tests}/{total_tests} tests passed.")
    print("---------------------------")


if __name__ == "__main__":
    run_test()