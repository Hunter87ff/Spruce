from flask import Flask
from threading import Thread
ap = Flask("Status")
@ap.route("/")
def home():return "Status : Online"
def run():ap.run(host='0.0.0.0', port=8080)
def keep_alive():t = Thread(target=run); t.start() 
