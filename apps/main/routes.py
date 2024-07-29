from . import main
from flask import request, jsonify, Response, request, stream_with_context
import time
from ..function.ocr import OCR_image_byte, OCR_images_byte, OCR_PDF
from .generate_problem import generate
from ..function.image_test import image_to_openai_response, images_to_openai_responses, PDF_to_openai_responses
import json

# TODO: 단일 이미지(/image)/다중 이미지(/images) 처리 통합, 기능적으로 동일
# /image routing으로 통일, 이후 해당 코드에 대한 주석 추가

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

@main.route('/pdf', methods=['POST'])
def upload_PDF():
    """
    POST /upload/pdf
    PDF 학습자료를 기반으로 문제 생성 및 vectordb 생성
    
    Request Body:
        {
            "file": "file object",  # 업로드된 PDF 파일
            "examSetting": "string" # JSON 형식의 시험 설정 옵션
        }
    
    Returns:
        json: 
        {
            "result": "object"  # 생성된 문제 및 기타 결과 데이터
        }
        
    Exceptions:
        400: 
            - {"error": "No file part"}: 요청에 'file' 부분이 없는 경우.
            - {"error": "No selected file"}: 파일이 선택되지 않은 경우.
            - {"error": "No examSetting found in the form data"}: 폼 데이터에 'examSetting'이 없는 경우.
            - {"error": "Invalid JSON format in examSetting"}: 'examSetting'이 유효한 JSON 형식이 아닌 경우.
    """
    
    # 요청에서 'file'이 포함되어 있는지 확인
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    # file 파싱
    file = request.files['file']
    
    # file 필드는 존재하나 파일을 선택하지 않았는지 확인
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # 'examSetting' 폼 데이터를 가져와 JSON으로 파싱
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    # 폼 데이터에 'examSetting' 키가 없는 경우
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    # 'examSetting'이 유효한 JSON 형식이 아닌 경우
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # PDF 파일의 내용을 읽음
    pdf_content = file.read()

    # 이미지 기반의 처리로 학습자료를 읽기(1)
    if user_option['isTextCentered'] == 1:
        text = PDF_to_openai_responses(pdf_content, user_option)
    # OCR 기능으로 학습자료를 읽기(0 or any) 
    else:
        text = OCR_PDF(pdf_content)
        
    # 학습자료를 읽은 내용을 기반으로 문제 생성
    result = generate(text, user_option)
    # 문제 생성 내용 반환
    return jsonify(result), 200