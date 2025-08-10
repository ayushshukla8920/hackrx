import re
def clean_text(text: str) -> str:
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
	sentences = re.split(r'(?<=[.!?]) +', text)
	chunks = []
	current_chunk = ""
	for sentence in sentences:
		if len(current_chunk) + len(sentence) <= chunk_size:
			current_chunk += sentence + " "
		else:
			chunks.append(current_chunk.strip())
			current_chunk = sentence + " "
	if current_chunk:
		chunks.append(current_chunk.strip())
	if overlap > 0 and len(chunks) > 1:
		for i in range(1, len(chunks)):
			overlap_text = chunks[i-1][-overlap:]
			chunks[i] = overlap_text + chunks[i]
	return chunks
