from . import main
from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor

@main.route('/', methods = ['POST'])
def feedback():
    params = request.get_json()
    print(params)
    return jsonify({"test" : "OK"})