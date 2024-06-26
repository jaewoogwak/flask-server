from . import main
from flask import request, send_file, jsonify, Response, request, stream_with_context
import time
from ..function.ocr import OCR_image_byte, OCR_images_byte, OCR_PDF
from .generate_problem import generate
from ..function.image_test import image_to_openai_response, images_to_openai_responses, PDF_to_openai_responses
import json

# 단일 이미지 처리
@main.route('/image', methods=['POST'])
def upload_image():
    """
    단일 이미지를 처리할 엔드포인트
    """
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # 이미지 파일의 내용을 읽음
    image_content = file.read()
        
    if user_option['isTextCentered'] == 1:
        text = image_to_openai_response(image_content, user_option)
    else:
        text = OCR_image_byte(image_content)
        
        result = generate(text, user_option)
        return jsonify(result), 200

# 이미지 여러 장 처리
@main.route('/images', methods=['POST'])
def upload_images():
    """
    여러 이미지를 처리할 엔드포인트
    """
    if 'files' not in request.files:
        return 'No files part', 400
    
    files = request.files.getlist('files')
    
    if not files or any(file.filename == '' for file in files):
        return 'No selected files', 400
    
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # 파일을 바이트 컨텐츠로 변환
    images = [file.read() for file in files]

    if user_option['isTextCentered'] == 1:
        text = images_to_openai_responses(images, user_option)
    else:
        text = OCR_images_byte(images)
        
    result = generate(text, user_option)
    return jsonify(result), 200

# PDF 파일 처리 라우팅
@main.route('/pdf', methods=['POST'])
def upload_PDF():
    """
    PDF 파일을 처리할 엔드포인트
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        user_option_str = request.form['examSetting']
        # print(user_option_str)
        user_option = json.loads(user_option_str)
        # print(user_option)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # PDF 파일의 내용을 읽음
    pdf_content = file.read()

    if user_option['isTextCentered'] == 1:
        text = PDF_to_openai_responses(pdf_content, user_option)
    else:
        text = OCR_PDF(pdf_content)
        
    result = generate(text, user_option)
    return jsonify(result), 200

@main.route('/progress', methods=['GET'])
def progress():
    """
    로직 수행 내용 생략, 프로그레스바 테스트 용도
    """
    return Response(stream_with_context(generate_progress()), mimetype='text/event-stream')

def generate_progress():
    progress = 0
    while progress <= 100:
        yield f"data:{progress}\n\n"
        progress += 10
        time.sleep(1)  # 프로그레스 업데이트 간격 (예: 1초)
        
    # 프로그레스가 100에 도달하면 종료 이벤트 전송
    yield "data:complete\n\n"