from . import main
from flask import render_template, url_for
from flask import jsonify

# 메인화면 라우트
@main.route('/')
def index():
    return jsonify(message='Hello, this is main Page')
