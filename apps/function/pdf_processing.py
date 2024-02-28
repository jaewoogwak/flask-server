import pdfkit
import os
from config import wk_setting

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
                    @page { margin: 40px; }
                    body { font-family: "Arial", sans-serif; color: #333; }
                    .container { padding: 20px; background-color: #f9f9f9; }
                    .question { page-break-inside: avoid; }
                    .blank { height: 20px; }
                    .question-box { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    .question-header { color: #2a7ae2; margin-bottom: 10px; font-size: 20px; }
                    .question-content, .options { margin-bottom: 5px; font-size: 16px; }
                    .option { margin-left: 20px; }
                    .spacer { page-break-before: always; height: 25px; }
                    .answer { page-break-inside: avoid; }
                    .answer-box { background-color: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); page-break-inside: avoid;}
                    .answer-text { background-color: #e7f3ff; padding: 10px; border-left: 4px solid #2a7ae2; }
                </style>
            </head>
            <body>
                <div class="container">
                <h1>연습문제</h1>
    '''

    for idx, question in enumerate(questions, start=1):
        html_content += f'''
            <div class="question">
                <div class="blank"></div>
                <div class="question-box">
                    <div class="question-header">문제 {idx}</div>
                    <div class="question-content">{question}</div>
                    <div class="options">{choices[idx-1]}</div>
                </div>
            </div>
        '''

    if include_answers:
        html_content += '<div class="spacer"></div><h1>정답</h1>'
        for idx, answer in enumerate(answers, start=1):
            html_content += f'''
                <div class="answer">
                    <div class="blank"></div>
                    <div class="answer-box">
                        <div class="answer-text">{idx}. 정답: {answer}</div>
                    </div>
                </div>
            '''
        html_content += '</div>'

    html_content += '</div></body></html>'
    return html_content


def create_pdf_from_html(html_content, output_file):
    """
    HTML 내용으로부터 PDF 파일을 생성하는 함수
    """
    if wk_setting['OS'] == 'Windows':
        # Windows 환경에서의 설정 사용
        config = pdfkit.configuration(wkhtmltopdf=wk_setting['PATH'])
        pdfkit.from_string(html_content, output_file, configuration=config)
    elif wk_setting['OS'] == 'Darwin':
        # macOS 환경에서의 설정 사용
        pdfkit.from_string(html_content, output_file)
    elif wk_setting['OS'] == 'Linux':
        pass

def remove_pdf(file_path):
    """
    지정된 경로의 PDF 파일을 제거합니다.
    """
    try:
        os.remove(file_path)
        print(f"File {file_path} has been removed successfully.")
    except OSError as e:
        print(f"Error: {e.strerror} - {e.filename}")