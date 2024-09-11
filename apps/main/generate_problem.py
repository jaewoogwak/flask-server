from ..function.langchain import request_prompt, embedding
from ..chatbot import routes
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict, Any

# TODO: 사용자 별 vectordb 유지하는 방안으로 변경시 코드 수정 필요
def generate(text: str, options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    입력된 학습자료 text를 기반으로 chatGPT를 사용하여 문제 생성을 하는 함수

    Args:
        text (str): 학습자료 내용
        options (Dict[str, Any], optional): 문제 생성 옵션을 포함한 딕셔너리. Defaults to None.

    Returns:
        List[Dict[str, Any]]: 생성된 문제와 관련 데이터의 리스트
    """
    # 사용자의 학습자료를 기반으로 vectordb 생성
    embedding(text)

    # 텍스트를 한 덩어리로 처리, 사용자 커스텀 프롬프트 정보 전달
    result = request_prompt(text, options)
    result_str = json.dumps(result, ensure_ascii=False)
    
    # 생성한 문제도 vectordb에 추가
    embedding(result_str)
    # 결과를 저장할 리스트 초기화
    quiz_data = []

    # JSON 구조 파싱
    for item in result["quiz_questions"]:
        quiz_data.append({
            "case": item["case"],
            "question": item["question"],
            "choices": item["choices"],
            "correct_answer": item["correct_answer"],
            "explanation": item["explanation"],
            "intent": item["intent"]
        })

    # LIST형으로 생성한 문제(DICT)들을 반환
    return quiz_data