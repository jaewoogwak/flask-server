from . import main
from flask import Flask, request, jsonify, send_file
from ..main.function.ocr import OCRImage_Byte, OCRImages_Byte, OCRPDF
from ..main.function.langchain import request_prompt
from ..main.function.pdf_processing import generate_pdf
from PIL import Image
import io
import re
import os

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

    # 파일을 바이트 컨텐츠로 변환
    images = [file.read() for file in files]
    
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
        
        # GPT API에 문제 생성 요청 및 응답 받음
        prompt_result = request_prompt(text)
        
        questions = re.findall(r'문제명: (.+?)\n', prompt_result)
        # 모든 문제에 대해 choices 배열을 초기화합니다.
        choices = [""] * len(questions)  # 모든 문제에 대응하는 빈 선택지를 초기 설정

        # 객관식 문제의 선택지를 파싱합니다.
        choices_matches = re.findall(r'입력:\n((?:\s+[A-D]\) .+\n)+)', prompt_result)
        for idx, match in enumerate(choices_matches):
            # 각 선택지를 <br>로 구분하여 하나의 문자열로 합칩니다.
            choices[idx] = match.strip().replace('\n', '<br>')

        answers = re.findall(r'해설: (.+?)(?:\n\n|\Z)', prompt_result, re.DOTALL)

        # 서술형 또는 단답형 문제에 대한 처리가 필요한 경우
        # 예시: 모든 빈 선택지에 "서술형 문제입니다." 메시지를 추가
        for idx in range(len(choices)):
            if choices[idx] == "":
                choices[idx] = "<br>____________________"
        
        output_file = 'output.pdf'
        generate_pdf(questions, choices, output_file)
        return send_file(output_file, as_attachment=True, download_name='custom_filename.pdf')