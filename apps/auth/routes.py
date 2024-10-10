from ..function.firebase_auth import token_required
from ..models import redis_client_auth_reader, redis_client_auth_primary
from . import main
from flask import request, jsonify
import smtplib
from email.mime.text import MIMEText
import random
import os

smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')

# mail로 인증번호를 보내는 로직
@main.route('/email', methods=['POST'])
#@token_required
def mail():
    # request body로부터 email parsing
    data = request.get_json()
    email = data.get('email')

    # email이 없는 경우 예외 반환
    if not email:
        return jsonify({'message': 'Email is required'}), 400

    # 6자리 난수 생성, Random lib 사용
    code = '{:06d}'.format(random.randint(0, 999999))

    # redis db에 email-code로 저장
    # TTL을 5분(300초)로 설정
    redis_client_auth_primary.setex(email, 300, code)

    # SMTP 서버 설정, google smtp server 사용
    # smtp port 587 사용
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # 인증 메일 내용 구성
    msg = MIMEText(f'Your verification code is: {code}')
    # 메일 제목
    msg['Subject'] = 'Study-mentor verification code'
    # 메일 송신자 email
    msg['From'] = 'study-mentor@gmail.com'
    # 메일 수신자 email
    msg['To'] = email

    try:
        # smtp를 통해 메일 전송 smtplib lib 사용
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, [email], msg.as_string())
        server.quit()
    except Exception as e:
        # smtp server를 통한 메일 전송에 문제가 생겼을 경우 예외 반환
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500

    # 메일 전송을 성공한 경우 200(status-code) 반환
    return jsonify({'message': 'Verification code sent successfully'}), 200

@main.route('/num', methods=['POST'])
#@token_required
def num():
    # request body에서 email과 auth code parsing
    data = request.get_json()
    email = data.get('email')
    user_code = data.get('authnum')
    
    if not email or not user_code:
        return jsonify({'message': 'Not enter email or verification code'}), 400
    
    # 이메일을 통해 전송된 번호와 사용자가 입력한 번호가 일치하는지 확인, 아닐 경우 예외 반환
    # redis에 내용이 없는 경우:
    # 1. 이전에 인증 메일을 보내지 않은 경우
    # 2. ttl을 넘겨 접근하려고 한 경우
    # 3. 이미 인증을 한 후 데이터가 삭제된 경우
    stored_code = redis_client_auth_reader.get(email)

    if not stored_code:
        return jsonify({'message': 'Email with expired or invalid credentials'}), 400
    
    # redis db에 사용자 이메일 정보가 있는 경우 저장된 인증 코드와 비교하여 검증
    stored_code = stored_code.decode('utf-8')

    # 입력한 코드와 저장된 코드가 다른 경우 예외 반환
    if user_code != stored_code:
        return jsonify({'message': 'Mismatched credentials'}), 400

    # redis db에서 인증 정보 삭제
    redis_client_auth_primary.delete(email)
    
    # 인증 코드 확인 로직이 잘 동작했다면 200(status-code) 반환
    return jsonify({'message': 'Verification is complete'}), 200
    