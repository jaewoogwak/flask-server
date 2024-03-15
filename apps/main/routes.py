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
    print(text)
    
    # 사용자의 학습자료를 기반으로 vectordb 생성
    routes.retriever = embedding(text)
    
    # API의 결과 JSON을 파싱하여 맵으로 할당
    prompt_result = request_prompt(text)
    
    # 결과를 저장할 배열 초기화
    cases = []
    questions = []
    choices = []
    answers = []
    explanations = []

    # JSON 구조 파싱
    for item in prompt_result["quiz_questions"]:
        cases.append(item["case"])
        questions.append(item["question"])
        choices.append(item["choices"])
        answers.append(item["correct_answer"])
        explanations.append(item["explanation"])

    generate_pdf_with_answers(cases, questions, choices, answers, explanations, output_file)