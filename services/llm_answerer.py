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
    prompt = f"""You are a helpful assistant. Answer the user's question based on the provided context.
        You MUST follow this format for your response, using the exact headings 'Answer:' and 'Rationale:'.

        Context:
        ---
        {context}
        ---

        Question: {question}

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