from ..function.firebase_auth import token_required, get_uid
from . import main
from flask import request, jsonify
from ..function.langchain import search_answer, redis_client, get_cached_embeddings
from langchain.vectorstores import Chroma
import pickle

# retriever를 통해 vectordb를 생성하고 vectordb기반 질문응답이 가능함
@main.route('/question-answer', methods=['POST'])
@token_required
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
    
    # get_uid() 함수를 통해 사용자 ID 가져오기
    user_id = get_uid()
    
    # redis에 올라가 있는 docs 반환
    docs_pickled = redis_client.get(user_id)

    # 문서 역직렬화
    docs = pickle.loads(docs_pickled)

    # 벡터 데이터의 경로
    embedded_path = f"./.cache/embeddings/{user_id}.txt"

    # 벡터스토어 로드 이후 retriever 생성
    vectorstore = Chroma.from_documents(docs, get_cached_embeddings(user_id), persist_directory=embedded_path)
    retriever = vectorstore.as_retriever()

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