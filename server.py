from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import subprocess

class CORSRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(r'C:\Users\Gokul Ramm\Desktop\pyexpo24\Speech to Text\templates\index.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        transcribed_text = json.loads(post_data.decode('utf-8'))['transcribedText']

        # Load medical-specific model and tokenizer
        model_name = "emilyalsentzer/Bio_ClinicalBERT"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        medical_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

        # Generate text based on the transcribed audio
        generated_text = medical_pipeline(transcribed_text, max_length=100)[0]["generated_text"]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'generatedText': generated_text}).encode('utf-8'))

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print('Server running at http://localhost:8000/')
    httpd.serve_forever()

def authenticate():
    # Authentication successful, run the server
    run_server()

if __name__ == '__main__':
    authenticate()
