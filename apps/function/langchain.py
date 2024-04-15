from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from openai import OpenAI
from .prompt import make_problem_prompt
from config import KEY
import json
import os

client = OpenAI()

def request_prompt(contents, num_questions=4):
    prompt = make_problem_prompt(contents, num_questions=num_questions)

    # 문제 생성을 위한 프롬프트 설정
    message = [
        {"role": "system", "content": prompt.get_system_prompt()},
        {"role": "user", "content": prompt.get_user_input()}
    ]

    # JSON 모드를 사용하여 num_questions개의 문제 생성 및 응답 받기
    response_json = client.chat.completions.create(
        model="gpt-4-turbo",  
        # model="gpt-4-0125-preview",
        response_format={"type": "json_object"},
        messages=message
    )

    # JSON 문자열을 파이썬 딕셔너리로 변환
    response = json.loads(response_json.choices[0].message.content)
    return response

# 유저의 입력을 벡터화시키는 함수
def embedding(user_input):
    
    # 파일 경로 설정
    file_path = "./.cache/files/test.txt"
    directory = os.path.dirname(file_path)

    # 디렉토리가 존재하지 않는 경우 생성
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 파일 쓰기
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(user_input)

    # splitter, loader 생성
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)

    # document split 과정 - 입력이 너무 클 때를 대비한 과정. 스킵해도 상관 X.
    docs = loader.load_and_split(text_splitter=splitter)

    # cache에서 임베딩(벡터화한 데이터) 가져오기
    cache_dir = LocalFileStore(f"./.cache/embeddings/test.txt")
    embeddings = OpenAIEmbeddings(openai_api_key=KEY)
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    # 주어진 문서에 대한 Vector 생성
    vectorstore = Chroma.from_documents(docs, cached_embeddings)


    retriever = vectorstore.as_retriever()

    return retriever

# 줄 관리 함수
def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

def search_answer(user_question, retriever):
    # 기본 설정
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Answer the question using only the following context. If you don't know the answer
         just say you don't know. DON'T make anything up.
         Context: {context}"""),
        ("human", "{question}")
    ])

    llm = ChatOpenAI(
        temperature=0.1,
        streaming=True,
        callbacks=[BaseCallbackHandler()],
        openai_api_key=KEY
    )

    # Langchain 부분
    chain = (
                {
                    "context": retriever | RunnableLambda(format_docs),
                    "question": RunnablePassthrough()
                }
                | prompt
                | llm
            )

    result = chain.invoke(user_question)

    print(result.content)
    return result.content