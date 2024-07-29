from . import main
from flask import Flask, request, jsonify
from ..function.ocr import OCR_image_byte
from ..function.langchain import embedding, search_answer

# retriever를 통해 vectordb를 생성하고 vectordb기반 질문응답이 가능함
# 일단 편리를 위해 전역변수로 설정하나 추후 필요시 수정이 필요함
# TODO: 사용자를 구분하여 retriever 기능을 구현하도록 변경
retriever = None

# 학습자료(단일 이미지) 기반의 vectorDB 생성
# 테스트 용도, 기존 /upload 에 정의된 기능들 중간에 들어갈 내용
# TODO: front-end에 사용되지 않으므로 확인 후 배포시에 해당 코드 주석처리
@main.route('/generate', methods=['POST'])
def generate_vectorDB():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # 이미지 파일의 내용을 읽음
        image_content = file.read()
        text = OCR_image_byte(image_content)
        
        global retriever
        retriever = embedding(text)
        return jsonify({"result" : "success"})

# TODO: /generate 함수 주석처리 및 사용자별 retriever 설정 이후 함수 내용 변경
@main.route('/question-answer', methods=['POST'])
def answer_question():
    """
    POST /chatbot/question-answer
    학습자료 기반의 질문에 대한 답변 내용 반환

    Request Body:
        {
            "question": "string"    # 질문 내용
        }
    
    Returns:
        json: 'answer' key
        example:
        {
            "answer": "string"  # 질문에 대한 답변 내용
        }
        
    Exceptions:
    """
    
    # retriever가 None이 아닌, 한 번이라도 vectordb를 생성한 경우
    if retriever is not None:
        question_data = request.json
        # json body의 "question"을 읽어옴
        question_text = question_data.get('question')
        
        # 답변 생성
        answer_text = search_answer(question_text, retriever)
        
        # 답변 반환
        return jsonify({"answer" : answer_text})
    else:
        # /generate가 선행되지 않았을 경우
        return jsonify({"answer" : "error"})