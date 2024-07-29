# app.py: flask project 시작 파일

# config.py에 선언한 환경변수를 사용
from config import *
# flask framework 사용
from flask import Flask
# CORS(Cross-Origin Resource Sharing) 설정을 위한 확장 라이브러리
from flask_cors import CORS
# main, chatbot, feedback의 폴더를 각각 라우팅 단위로 관리
# 라우팅을 blueprint로 선언하기 위해 참조
from apps.main import main as main_blueprint
from apps.chatbot import main as chatbot_blueprint
from apps.feedback import main as feedback_blueprint

# Flask application instance를 생성
app = Flask(__name__)
# CORS 설정을 통해 다른 도메인(주소)의 접속을 허용
# TODO: Front-end에서만 접속 허용하도록 설정 추가 필요

CORS(app)

# Blueprint를 등록하여 URL의 라우팅을 관리
# main_blueprint, chatbot_blueprint, feedback_blueprint의 시작 라우팅 주소를 각각
# /upload, /chatbot, /feedback으로 설정
app.register_blueprint(main_blueprint, url_prefix = '/upload')
app.register_blueprint(chatbot_blueprint, url_prefix = '/chatbot')
app.register_blueprint(feedback_blueprint, url_prefix = '/feedback')

# flask가 요청을 받을 IP, 0.0.0.0으로 설정함으로서 모든 네트워크 주소에서 요청을 받도록 설정
address = '0.0.0.0'

if __name__ == '__main__':
    # Flask application 실행
    # 5000 port, debug=true(코드 변경시 자동 재시작) 설정
    # TODO: 배포 시 debug=False로 설정
    app.run(debug=True, host=address, port=5000)