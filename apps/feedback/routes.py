from . import main
from flask import request, jsonify
from ..function.marking import feedback_main

@main.route('/', methods = ['POST'])
def feedback():
    """
    POST /feeadback/
    입력한 문제의 채점 문제 피드백 내용을 반환

    Request Body:
        FeedBackResults = [
            {
                "case": int,                                # 문제 유형, 객관식일 경우 0, 주관식일 경우 1
                "question": "string",                       # 문제 명(이름)
                "choices": [array of string] or "string",   # 문제 선지, 객관식의 경우 4개의 선택지 배열, 주관식의 경우 "빈칸"
                "correct_answer": int or "string",          # 문제 정답, 객관식의 경우 선지 번호, 주관식의 경우 정답 string
                "explanation": "string",                    # 정답 설명
                "intent": "string"                          # 문제 생성 의도
            },
            {},
            ...
        ]
    
    Returns:
        array of json: 'index', 'isCorrect', 'feedback' key
        [
            {
                "index": int,           # index
                "isCorrect": int,       # 맞으면 1, 틀리면 0
                "feedback": "string"    # 문제 채점 후 피드백 내용
            },
            {},
            ...
        ]
        
    Exceptions:
        - {"test" : "Error"}: 'FeedBackResults' key가 Request Body에 없는 경우
    """
    # Json을 읽어 딕셔너리로 변환
    params = request.get_json()
    
    # 예시 입력 JSON 파싱
    if "FeedBackResults" in params:
        result = feedback_main(5, params["FeedBackResults"])

        return jsonify(result)
    
    return jsonify({"test" : "Error"})