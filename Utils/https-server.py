#!/usr/bin/env python3
from flask import Flask, request
import os
app = Flask(__name__)
app.secret_key = "sumango3"
@app.route('/')
def main():
    with open('log.txt', 'a') as f:
        f.write(str(request.__dict__))
        f.write('<br><br>')
    with open('log.txt','r') as f:
        return f.read()
if __name__ == "__main__":
      app.run(debug=True, host='0.0.0.0', port=1234, ssl_context='adhoc')
