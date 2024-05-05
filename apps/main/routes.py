from . import main
from flask import request, send_file, jsonify
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
    
    # json을 str로 읽음
    user_option_str = request.form['examSetting']
    # str을 딕셔너리로 변환
    user_option = json.loads(user_option_str)
    
    if file:
        # 이미지 파일의 내용을 읽음
        image_content = file.read()
        text = image_to_openai_response(image_content) if user_option['image'] == "true" else OCR_image_byte(image_content)
        
        output_file = 'output.pdf'
        result = generate(text, output_file)
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
    # json을 str로 읽음
    user_option_str = request.form['examSetting']
    # str을 딕셔너리로 변환
    user_option = json.loads(user_option_str)
    
    if not files or any(file.filename == '' for file in files):
        return 'No selected files', 400

    # 파일을 바이트 컨텐츠로 변환
    images = [file.read() for file in files]

    # 이미지 OCR 처리
    text = images_to_openai_responses(images) if user_option['image'] == "true" else OCR_images_byte(images)
    output_file = 'output.pdf'
    result = generate(text, output_file)
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
        user_option = json.loads(user_option_str)
        print(user_option)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # PDF 파일의 내용을 읽음
    pdf_content = file.read()
    text = OCR_PDF(pdf_content)
    if user_option['image'] == "true":
        text = PDF_to_openai_responses(pdf_content)
    else:
        text = OCR_PDF(pdf_content)
    result = generate(text, user_option)
    return jsonify(result), 200