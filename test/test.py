import argostranslate.package
import argostranslate.translate
from flask import Flask, jsonify, request
from flask_compress import Compress
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app)
Compress(app)

def update_package(fr, to):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    p2i = next(filter(lambda x: x.from_code == fr and x.to_code == to, available_packages))
    argostranslate.package.install_from_path(p2i.download())

@cache.cached(timeout=3600, key_prefix="from")
@app.route("/translate", methods=["GET"])
def translate():
    from_code = request.args.get("from")
    to_code = request.args.get("to")
    text = request.args.get("text")
    update_package(from_code, to_code)
    translatedText = argostranslate.translate.translate(text, from_code, to_code)
    return jsonify({"translatedText": translatedText})


app.run(port=5000)