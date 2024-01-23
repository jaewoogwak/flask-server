from . import main
from flask import Flask, request, jsonify
from ..main.function.ocr import OCRImage_Byte, OCRImages_Byte, OCRPDF
from PIL import Image  
import io

@main.route('/image', methods=['POST'])
def UploadImage():
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
        text = OCRImage_Byte(image_content)
        return jsonify({'extracted_text': text})

@main.route('/images', methods=['POST'])
def UploadImages():
    """
    여러 이미지를 처리할 엔드포인트
    """
    if 'files' not in request.files:
        return 'No files part', 400
    
    files = request.files.getlist('files')
    
    if not files or any(file.filename == '' for file in files):
        return 'No selected files', 400

    images = [Image.open(io.BytesIO(file.read())) for file in files]
    
    # 이미지 OCR 처리
    texts = OCRImages_Byte(images)
    
    # 결과를 JSON 형식으로 클라이언트에 반환
    return jsonify({'extracted_text' : texts})

@main.route('/pdf', methods=['POST'])
def UploadPDF():
    """
    PDF 파일을 처리할 엔드포인트
    """
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # PDF 파일의 내용을 읽음
        pdf_content = file.read()
        text = OCRPDF(pdf_content)
        return jsonify({'extracted_text': text})
