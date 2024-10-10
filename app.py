# config.py에 선언한 환경변수를 사용
from config import *
# flask framework 사용
from flask import Flask, jsonify
# CORS(Cross-Origin Resource Sharing) 설정을 위한 확장 라이브러리
from flask_cors import CORS
# main, chatbot, feedback의 폴더를 각각 라우팅 단위로 관리
# 라우팅을 blueprint로 선언하기 위해 참조
from apps.main import main as main_blueprint
from apps.chatbot import main as chatbot_blueprint
from apps.feedback import main as feedback_blueprint
from apps.auth import main as auth_blueprint
# WSGI to ASGI 변환을 위한 미들웨어
from asgiref.wsgi import WsgiToAsgi

# Flask application instance를 생성
app = Flask(__name__)
# CORS 설정을 통해 다른 도메인(주소)의 접속을 허용
CORS(app, resources={r"/*": {"origins":"*"}})

# Blueprint를 등록하여 URL의 라우팅을 관리
app.register_blueprint(main_blueprint, url_prefix = '/upload')
app.register_blueprint(chatbot_blueprint, url_prefix = '/chatbot')
app.register_blueprint(feedback_blueprint, url_prefix = '/feedback')
app.register_blueprint(auth_blueprint, url_prefix = '/auth')

@app.route('/', methods=['GET'])
def health():
    return "good", 200

# WSGI를 ASGI로 변환
asgi_app = WsgiToAsgi(app)

# main 함수 제거, Uvicorn을 통해 실행하도록 변경