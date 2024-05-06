from . import main
from flask import request, jsonify
from ..function.marking import feedback_main

@main.route('/', methods = ['POST'])
def feedback():
    # Json을 읽어 딕셔너리로 변환
    params = request.get_json()
    
    # 예시 입력 JSON 파싱
    if "FeedBackResults" in params:
        result = feedback_main(5, params["FeedBackResults"])

        return jsonify(result)
    
    return jsonify({"test" : "Error"})