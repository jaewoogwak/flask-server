from ..function.langchain import request_prompt, embedding
from ..function.pdf_processing import generate_pdf_with_answers
from ..chatbot import routes
from concurrent.futures import ThreadPoolExecutor
import json
from typing import List, Dict, Any

# TODO: 병렬처리 코드가 필요 없어짐에 따라 병렬처리 함수(generate_parallel) 삭제 필요

# 병렬 처리를 이용한 GPT API 처리
def generate_parallel(text, options, output_file='output.pdf'):
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
    
    #print(results)    
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

# TODO: 사용자 별 vectordb 유지하는 방안으로 변경시 코드 수정 필요
def generate(text: str, options: Dict[str, Any] = None, output_file: str = 'output.pdf') -> List[Dict[str, Any]]:
    """
    입력된 학습자료 text를 기반으로 chatGPT를 사용하여 문제 생성을 하는 함수

    Args:
        text (str): _description_
        options (Dict[str, Any], optional): 문제 생성 옵션을 포함한 딕셔너리. Defaults to None.
        output_file (str, optional): 생성된 문제를 저장할 출력 파일 이름. Defaults to 'output.pdf'.

    Returns:
        List[Dict[str, Any]]: 생성된 문제와 관련 데이터의 리스트
    """
    # 사용자의 학습자료를 기반으로 vectordb 생성
    routes.retriever = embedding(text)

    # 텍스트를 한 덩어리로 처리, 사용자 커스텀 프롬프트 정보 전달
    result = request_prompt(text, options)
    result_str = json.dumps(result, ensure_ascii=False)
    
    # 생성한 문제도 vectordb에 추가
    routes.retriever = embedding(result_str)
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