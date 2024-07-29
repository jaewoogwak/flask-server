from flask import Blueprint

# Blueprint 객체 생성, blueprint의 이름을 'feedback'으로 설정
# __name__을 통해 모듈이름 설정, __name__은 'apps/feedback'
# 현재 위치로 blueprint 설정하여 라우팅되었을 때 현재 파일의 정보를 사용
main = Blueprint('feedback', __name__)

# routes.py를 import하여 route 모듈을 사용
from .routes import *
