import os
import threading
from dotenv import load_dotenv, dotenv_values
from flask import Flask, request
from PDFSummarizer import PDFSummarizer

load_dotenv()

app = Flask(__name__)

@app.route('/health')
def index():
	return 'Healthy'

@app.route('/summarize', methods=['POST'])
def summarize():
	file = request.files.get('file')
	page_start = int(request.form.get('pageStart'))
	page_end = int(request.form.get('pageEnd'))

	if not file or not page_start or not page_end:
		return {'error': 'Missing file or content boundaries'}, 400

	pdfSummarizer = PDFSummarizer()
	threading.Thread(target=pdfSummarizer.summarize, args=(file, page_start, page_end)).start()

	return {'data': 'Summarization started'}, 202

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=5002)