import pdfkit
import os
import re

def generate_pdf(questions, choices, output_file='연습문제_정답없음.pdf'):
    """
    문제(questions)와 선택지(choices)만을 받아 PDF 파일을 생성합니다 (정답 없음).
    """
    # HTML 문자열 생성 시작
    html_content = create_html_content(questions, choices, include_answers=False)
    
    # PDF 파일 생성
    create_pdf_from_html(html_content, output_file)

def generate_pdf_with_answers(questions, choices, answers, output_file='연습문제_정답포함.pdf'):
    """
    문제(questions), 선택지(choices), 정답(answers)을 받아 PDF 파일을 생성합니다 (정답 포함).
    """
    # HTML 문자열 생성 시작
    html_content = create_html_content(questions, choices, answers, include_answers=True)
    
    # PDF 파일 생성
    create_pdf_from_html(html_content, output_file)

def create_html_content(questions, choices, answers=None, include_answers=False):
    """
    HTML 내용을 생성하는 함수
    """
    html_content = '''
<html>
<head>
    <title>연습문제</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: "Arial", sans-serif; margin: 40px; padding-top: 40px; background-color: #f9f9f9; color: #333; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .question-header { color: #2a7ae2; margin-bottom: 10px; font-size: 20px; }
        .question-content, .options { margin-bottom: 5px; font-size: 16px; }
        .option { margin-left: 20px; }
        .spacer { page-break-before: always; height: 40px; }
        .answers { background-color: #fff; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .answer-text { background-color: #e7f3ff; padding: 10px; border-left: 4px solid #2a7ae2; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>연습문제</h1>
    '''

    for idx, question in enumerate(questions, start=1):
        html_content += f'''
        <div class="container">
            <div class="question-header">문제 {idx}</div>
            <div class="question-content">{question}</div>
            <div class="options">{choices[idx-1]}</div>
        </div>
        '''

    if include_answers:
        html_content += '<div class="spacer"></div><div class="answers"><h2>정답</h2>'
        for idx, answer in enumerate(answers, start=1):
            html_content += f'<div class="answer-text">{idx}. 정답: {answer}</div>'
        html_content += '</div>'

    html_content += '</body></html>'
    return html_content


def create_pdf_from_html(html_content, output_file):
    """
    HTML 내용으로부터 PDF 파일을 생성하는 함수
    """
    # wkhtmltopdf 설치 후 경로 입력 필요(windows에서만 생기는 문제, 본인 경로에 맞게 수정, 서버(linux)에 올리는 경우는 테스트 필요)
    # config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    
    pdfkit.from_string(html_content, output_file)

def remove_pdf(file_path):
    """
    지정된 경로의 PDF 파일을 제거합니다.
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} has been removed successfully.")
    except OSError as e:
        print(f"Error: {e.strerror} - {e.filename}")