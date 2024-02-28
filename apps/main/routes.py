from . import main
from flask import request, send_file
from ..function.ocr import OCRImage_Byte, OCRImages_Byte, OCRPDF
from ..function.langchain import request_prompt, embedding
from ..function.pdf_processing import generate_pdf_with_answers
from ..chatbot import routes
import re

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
        
        output_file = 'output.pdf'
        use_GPT_PDF_processing(text, output_file)
        return send_file(output_file, mimetype='application/pdf', as_attachment=True, download_name='custom_filename.pdf')

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
    text = OCRImages_Byte(images)
    output_file = 'output.pdf'
    use_GPT_PDF_processing(text, output_file)
    return send_file(output_file, mimetype='application/pdf', as_attachment=True, download_name='custom_filename.pdf')


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
        
        output_file = 'output.pdf'
        use_GPT_PDF_processing(text, output_file)
        return send_file(output_file, mimetype='application/pdf', as_attachment=True, download_name='custom_filename.pdf')

def use_GPT_PDF_processing(text, output_file='output.pdf'):
    # 사용자의 학습자료를 기반으로 vectordb 생성
    routes.retriever = embedding(text)
    
    prompt_result = request_prompt(text)
        
    questions = re.findall(r'문제명: (.+?)\n', prompt_result)
    # 모든 문제에 대해 choices 배열을 초기화합니다.
    choices = [""] * len(questions)  # 모든 문제에 대응하는 빈 선택지를 초기 설정

    # 객관식 문제의 선택지를 파싱합니다.
    choices_matches = re.findall(r'입력:\n((?:\s+[A-D]\) .+\n)+)', prompt_result)
    
    # 모든 문제에 대해 서술형 메시지 또는 객관식 선택지 추가
    for idx, question in enumerate(questions):
        if idx < len(choices_matches):
            # 각 선택지를 <br>로 구분하여 하나의 문자열로 합칩니다.
            choices[idx] = choices_matches[idx].strip().replace('\n', '<br>')
        else:
            # 서술형 또는 단답형 문제에 대한 기본 메시지 설정
            choices[idx] = "<br>____________________"

    answers = re.findall(r'해설: (.+?)(?:\n\n|\Z)', prompt_result, re.DOTALL)

    generate_pdf_with_answers(questions, choices, answers, output_file)