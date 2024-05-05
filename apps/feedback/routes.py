from . import main
from flask import request, jsonify
from concurrent.futures import ThreadPoolExecutor

@main.route('/', methods = ['POST'])
def feedback():
    # Json을 읽어 딕셔너리로 변환
    params = request.get_json()
    
    # 예시 입력 JSON 파싱
    if "FeedBackResults" in params:
        feedback_results = params["FeedBackResults"]

        # 각 문제 정보 출력
        # for info in feedback_results:
        #     index = info['index']
        #     question = info['question']
        #     choices = info['choices']
        #     correctAnswer = info['correctAnswer']
        #     user_answer = info['userAnswer']
        #     isCorrect = info['isCorrect']
        #     explanation = info['explanation']
        #     intent = info['intent']
            

        #     # 파싱된 정보 출력
        #     print(f"시험 문제 번호: {index}")
        #     print(f"시험 문제: {question}")
        #     print(f"사용자 응답: {user_answer}")
        #     print(f"정답 여부: {isCorrect}")
        #     print("---")

        return jsonify(params)
    
    return jsonify({"test" : "Error"})