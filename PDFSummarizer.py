import fitz
from transformers import pipeline
import re
import os
import requests
from io import BytesIO

class PDFSummarizer:
	_summarizer = None

	@classmethod
	def get_summarizer(cls):
		if cls._summarizer is None:
			cls._summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
		return cls._summarizer

	def summarize_text(self, text):
		summarizer = self.get_summarizer()
		return summarizer(text, max_length=150, min_length=30, do_sample=False)

	def summarize(self, file, start_page, end_page):
		extracted_text = self.extract_text_from_pdf(file, start_page, end_page)
		extracted_text = re.sub(r"(\r\n|\n|\r)", " ", extracted_text).strip()

		chunks = self.split_text_into_chunks(extracted_text)
		summarized_chunks = []

		for chunk in chunks:
			summary = self.summarize_text(chunk)
			summarized_chunks.append(summary[0]["summary_text"])

		self.save_to_file("\n".join(summarized_chunks), "output.txt")

		# learning_trail_url = os.getenv("LEARNING_TRAIL_API_URL")
		# response = requests.post(learning_trail_url, json={"sections": summarized_chunks})

		# if response.status_code != 200:
		# 	raise Exception(f"Failed to post summary: {response.status_code} - {response.text}")

	def extract_text_from_pdf(self, file, start_page, end_page):
		stream = BytesIO(file.read())
		doc = fitz.open(stream=stream)
		text = ""

		for page_num in range(start_page - 1, end_page):
			page = doc.load_page(page_num)
			text += page.get_text() + "\n"

		doc.close()
		self.save_to_file(text, "text.txt")
		return text

	def split_text_into_chunks(self, text, max_chunk_length=2048): # TODO 2048 caracteres, e não tokens, rever
		sentences = re.split(r"(?<=[.!?]) +", text)
		chunks = []
		current_chunk = []

		for sentence in sentences:
			if len(" ".join(current_chunk + [sentence])) <= max_chunk_length:
				current_chunk.append(sentence)
			else:
				chunks.append(" ".join(current_chunk))
				current_chunk = [sentence]

		if current_chunk:
			chunks.append(" ".join(current_chunk))

		return chunks

	def save_to_file(self, text, filename="output.txt"):
		with open(filename, "w") as file:
			file.write(text)