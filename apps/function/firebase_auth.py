from flask import jsonify, request
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from functools import wraps

# Firebase Admin SDK 초기화
# flask project 시작 시 처음에만 적용
cred = credentials.Certificate('chat-8d7b2-firebase-adminsdk-xkof8-dc3fc2b5ae.json')
firebase_admin.initialize_app(cred)
def token_required(f):
    """
    Firebase 인증 토큰이 유효한지 확인하는 데코레이터

    주어진 route function에 데코레이터를 추가하여 client가 제공한 Firebase 인증 토큰이 유효한지 검증
    토큰이 유효하지 않거나 만료된 경우, 401 Unauthorized 응답을 반환

    Args:
        f (function): 데코레이터가 적용될 route function

    Returns:
        function: 인증이 성공적으로 완료된 경우, 원래의 route function이 호출되며, 그렇지 않으면 401 응답을 반환
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # Authorization 헤더에서 토큰 파싱
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        # 토큰이 존재하지 않는 경우, 401 응답을 반환
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Firebase를 사용하여 토큰을 검증
            decoded_token = firebase_auth.verify_id_token(token)
            # 사용자 정보를 요청 객체에 첨부
            request.user = decoded_token
        except Exception as e:
            # 토큰이 유효하지 않거나 만료된 경우, 401 응답을 반환
            return jsonify({'message': 'Token is invalid or expired!'}), 401

        # 인증이 성공하면 원래의 라우트 함수를 호출
        return f(*args, **kwargs)

    return decorator

def get_uid():
    """
    Firebase uid를 가져오기 위한 함수

    Args:
    Returns:
        str: user를 구분하기 위한 uid
    """
    token = None
    # Authorization 헤더에서 토큰 파싱
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]

    # 토큰이 존재하지 않는 경우, 401 응답을 반환
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    try:
        # Firebase를 사용하여 토큰을 검증
        decoded_token = firebase_auth.verify_id_token(token)
        # 사용자 정보를 요청 객체에 첨부
        request.user = decoded_token
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        # 토큰이 유효하지 않거나 만료된 경우, 401 응답을 반환
        return jsonify({'message': 'Token is invalid or expired!'}), 401