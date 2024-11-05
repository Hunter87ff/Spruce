from flask import Flask
from threading import Thread
ap = Flask(__name__)
ap.config['WTF_CSRF_ENABLED'] = False
@ap.route("/")
def home():return "Status : Online"
def run():ap.run(host='0.0.0.0', port=8080)
def keep_alive():t = Thread(target=run); t.start() 