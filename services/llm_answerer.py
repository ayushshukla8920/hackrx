import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    raise Exception("FATAL ERROR: GOOGLE_API_KEY environment variable not found.")
genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
  "temperature": 0.1,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}
model = genai.GenerativeModel(model_name="gemini-2.0-flash",generation_config=generation_config)
def generate_answer(question: str, context_chunks: list) -> tuple:
    context = "\n\n".join(context_chunks)
    prompt = f"""You are a highly intelligent routing agent and question-answering engine. Your primary task is to analyze the user's QUESTION and determine the correct action based on the rules below. You must follow these rules with absolute precision.

        ---
        **RULESET**

        1.  **Analyze the QUESTION first.** Determine if the question can be answered using ONLY the provided CONTEXT, or if it requires an external action (like accessing an external webpage, calling an API, or accessing a database).

        2.  **If the QUESTION requires an external action** (e.g., "Go to the link and get the secret token," "What is the weather today?"), you MUST respond with only the exact phrase: `handle_agentic_workflow()`. Do not provide any other text.

        3.  **If the QUESTION can be answered from the CONTEXT,** proceed with the following steps:
            a. Carefully read the CONTEXT to find the relevant information.
            b. If the answer is found, provide a direct and concise answer.
            c. **If the CONTEXT does not contain the answer, you are forbidden from using any external knowledge.** You MUST respond with the exact phrase: "The answer is not available in the provided document."

        4.  **Your final output must be in the specified format.** For cases where the answer is not found, the Rationale should be: 'The provided context did not contain information relevant to the question.'

        ---
        **FORMAT**

        Answer: [Your concise answer here OR "call Agentic function" OR "The answer is not available in the provided document."]
        Rationale: [Your explanation here.]

        ---
        **CONTEXT**
        {context}
        ---

        **QUESTION**
        {question}
        """
    try:
        response = model.generate_content(prompt)
        answer_text = response.text
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return "Error: Could not generate an answer.", str(e)
    if "Rationale:" in answer_text:
        parts = answer_text.split("Rationale:", 1)
        answer = parts[0].replace("Answer:", "").strip()
        rationale = parts[1].strip()
    else:
        answer = answer_text.replace("Answer:", "").strip()
        rationale = "Rationale not provided in the expected format."
    return answer, rationale