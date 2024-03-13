from flask import Flask

app = Flask("testing")

@app.route("/")
def home():
    return "hello"

app.run()