from . import main
from flask import Flask, request, jsonify, send_file
from ..function.ocr import OCRImage_Byte, OCRImages_Byte, OCRPDF
from ..function.langchain import request_prompt
from ..function.pdf_processing import generate_pdf, generate_pdf_with_answers

# 학습자료 기반의 vectorDB 생성
@main.route('/generate', methods=['POST'])
def generate_vectorDB():
    return 0

# 학습자료 기반의 질문 답변(어떻게 학습자료를 특정할지 미정)
@main.route('/answer', methods=['POST'])
def answer_question():
    return 0