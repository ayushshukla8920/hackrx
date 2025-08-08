
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
	endpoint=endpoint,
	credential=AzureKeyCredential(token),
)

def generate_answer(question: str, context_chunks: list) -> tuple:
	context = "\n\n".join(context_chunks)
	prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer with a concise response and a rationale citing relevant clauses."
	response = client.complete(
		messages=[
			SystemMessage("") ,
			UserMessage(prompt),
		],
		temperature=1,
		top_p=1,
		model=model
	)
	answer_text = response.choices[0].message.content
	if "Rationale:" in answer_text:
		parts = answer_text.split("Rationale:", 1)
		answer = parts[0].strip()
		rationale = parts[1].strip()
	else:
		answer = answer_text.strip()
		rationale = "Rationale not found."
	return answer, rationale
