from flask import Flask
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    return f'''
    <html>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #1a2a4a; color: white;">
            <h1>Hello Thales</h1>
            <p>SRE CloudOps — wmjay</p>
            <p>Server: {hostname}</p>
            <p>Status: Running</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {"status": "healthy", "host": socket.gethostname()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)