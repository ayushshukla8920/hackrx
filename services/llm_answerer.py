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
    prompt = f"""You are a strict and precise question-answering engine. Your sole purpose is to answer the user's QUESTION based ONLY on the text provided in the CONTEXT section.
        Follow these rules with absolute precision:
        1.  Carefully read the CONTEXT to find information relevant to the QUESTION.
        2.  If the answer is found in the CONTEXT, provide a direct and concise answer.
        3.  **If the CONTEXT does not contain the information needed to answer the QUESTION, you are forbidden from using any external knowledge.** You MUST respond with the exact phrase: "The answer is not available in the provided document."
        4.  Do not make assumptions or infer information that is not explicitly stated in the CONTEXT.
        5.  Your final output must be in the specified format, using the headings 'Answer:' and 'Rationale: and no should be cleaned text, no markers,triple quotes or new lines'. For cases where the answer is not found, the Rationale should be: 'The provided context did not contain information relevant to the question.'

        CONTEXT:
        ---
        {context}
        ---

        QUESTION: {question}
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