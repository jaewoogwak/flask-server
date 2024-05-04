from . import main
from flask import request, send_file, jsonify
from ..function.ocr import OCR_image_byte, OCR_images_byte, OCR_PDF
from .generate_problem import generate
from ..function.image_test import process_pdf_to_openai_responses
import json

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

    if file:
        # 이미지 파일의 내용을 읽음
        image_content = file.read()
        text = OCR_image_byte(image_content)
        
        output_file = 'output.pdf'
        result = generate(text, output_file)
        return jsonify(result), 200

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

    # 파일을 바이트 컨텐츠로 변환
    images = [file.read() for file in files]

    # 이미지 OCR 처리
    text = OCR_images_byte(images)
    output_file = 'output.pdf'
    result = generate(text, output_file)
    return jsonify(result), 200

@main.route('/pdf', methods=['POST'])
def upload_PDF():
    """
    PDF 파일을 처리할 엔드포인트
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    user_option_str = request.form['examSetting']
    user_option = json.loads(user_option_str)
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # PDF 파일의 내용을 읽음
    pdf_content = file.read()
    text = process_pdf_to_openai_responses(pdf_content) if user_option["image"] == "true" else OCR_PDF(pdf_content)
    result = generate(text, user_option)
    return jsonify(result), 200