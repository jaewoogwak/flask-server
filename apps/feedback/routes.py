from . import main
from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor

@main.route('/', methods = ['POST'])
def feedback():
    params = request.get_json()
    
    # 예시 입력 JSON 파싱
    if 'FeedBackResults' in params:
        feedback_results = params['FeedBackResults']

        # 각 문제 정보 출력
        for question_info in feedback_results:
            index = question_info['index']
            question = question_info['question']
            user_answer = question_info['userAnswer']
            is_correct = question_info['isCorrect']

            # 파싱된 정보 출력
            print(f"시험 문제 번호: {index}")
            print(f"시험 문제: {question}")
            print(f"사용자 응답: {user_answer}")
            print(f"정답 여부: {is_correct}")
            print("---")

        return jsonify({"test": "OK"})
    
    return jsonify({"test" : "Error"})