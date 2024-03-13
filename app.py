import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import subprocess
from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

# Database connection configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Gokul@sgr123"
DB_NAME = "firstproject"

def connect_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

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
    webbrowser.open('http://localhost:8000/')  # Open in default web browser
    httpd.serve_forever()

def authenticate():
    # Authentication successful, run the server
    run_server()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['newUsername']
        password = request.form['newPassword']
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        db.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    db.close()
    if user:
        # Authentication successful, run the server
        run_server()
        return redirect(url_for('success'))
    else:
        # Authentication failed, display error message
        return render_template('login.html', error="Invalid username or password")

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
