from . import main
from flask import request, send_file, jsonify
from ..function.ocr import OCR_image_Byte, OCR_images_Byte, OCR_PDF
from ..function.langchain import request_prompt, embedding
from ..function.pdf_processing import generate_pdf_with_answers
from ..chatbot import routes
from concurrent.futures import ThreadPoolExecutor

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
        text = OCR_image_Byte(image_content)
        
        output_file = 'output.pdf'
        result = use_GPT_PDF_processing(text, output_file)
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
    text = OCR_images_Byte(images)
    output_file = 'output.pdf'
    result = use_GPT_PDF_processing(text, output_file)
    return jsonify(result), 200

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
    if file:
        # PDF 파일의 내용을 읽음
        pdf_content = file.read()
        text = OCR_PDF(pdf_content)
        result = use_GPT_PDF_processing(text)
        return jsonify(result), 200

@main.route('/download', methods=['GET'])
def download_PDF():
    output_file = 'output.pdf'
    return send_file(output_file, mimetype='application/pdf', as_attachment=True, download_name='custom_filename.pdf')

def use_GPT_PDF_processing(text, output_file='output.pdf'):
    print(text)
    # 사용자의 학습자료를 기반으로 vectordb 생성
    routes.retriever = embedding(text)
    # 텍스트를 5개의 토큰으로 분할하고, 토큰이 맥락을 유지하도록 겹치게 분할
    tokens = []
    token_size = len(text) // 5
    overlap_size = token_size // 2  # 겹치는 텍스트의 크기 설정
    for i in range(5):
        if i == 0:
            start = 0
            end = token_size + overlap_size
        elif i == 4:
            start = i * token_size - overlap_size
            end = len(text)
        else:
            start = i * token_size - overlap_size
            end = (i + 1) * token_size + overlap_size
        tokens.append(text[start:end])
        
    # 병렬 처리를 사용하여 API에 5번 요청하여 문제 받아오기
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(request_prompt, tokens))
    
    print(results)    
    # 결과를 저장할 배열 초기화
    cases = []
    questions = []
    choices = []
    answers = []
    explanations = []
    intents = []

    # 결과를 저장할 리스트 초기화
    quiz_data = []
    # JSON 구조 파싱
    for result in results:
        for item in result["quiz_questions"]:
            cases.append(item["case"])
            questions.append(item["question"])
            choices.append(item["choices"])
            answers.append(item["correct_answer"])
            explanations.append(item["explanation"])
            intents.append(item["intent"])
            quiz_data.append({
                "case": item["case"],
                "question": item["question"],
                "choices": item["choices"],
                "correct_answer": item["correct_answer"],
                "explanation": item["explanation"],
                "intent": item["intent"]
            })
    # PDF 파일 생성
    generate_pdf_with_answers(cases, questions, choices, answers, explanations, output_file)
    return quiz_data

# def use_GPT_PDF_processing(text, output_file='output.pdf'):
#     print(text)
#     # 사용자의 학습자료를 기반으로 vectordb 생성
#     routes.retriever = embedding(text)

#     # 텍스트를 한 덩어리로 처리
#     result = request_prompt(text)

#     # 결과를 저장할 배열 초기화
#     cases = []
#     questions = []
#     choices = []
#     answers = []
#     explanations = []
#     intents = []

#     # 결과를 저장할 리스트 초기화
#     quiz_data = []

#     # JSON 구조 파싱
#     for item in result["quiz_questions"]:
#         cases.append(item["case"])
#         questions.append(item["question"])
#         choices.append(item["choices"])
#         answers.append(item["correct_answer"])
#         explanations.append(item["explanation"])
#         intents.append(item["intent"])
#         quiz_data.append({
#             "case": item["case"],
#             "question": item["question"],
#             "choices": item["choices"],
#             "correct_answer": item["correct_answer"],
#             "explanation": item["explanation"],
#             "intent": item["intent"]
#         })

#     # PDF 파일 생성
#     generate_pdf_with_answers(cases, questions, choices, answers, explanations, output_file)

#     return quiz_data