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
from config import KEY
import json

client = OpenAI()

def request_prompt(contents):
    prompt_setting = """
    사용자가 제공하는 텍스트를 기반으로 4개의 문제를 생성하고 JSON 형식으로 반환해주세요. 전체 응답은 quiz_questions이라는 키를 가진 배열로 구성되어야 하며, 
    각 문제는 case, question, choices, correct_answer, explanation을 포함해야 합니다. 
    case는 문제 유형으로 객관식 문제이면 0이, 주관식문제이면 1이 입력됩니다. 
    첫 2개의 문제는 객관식으로, 각 문제의 선택지는 4개이며, 정답과 해당 정답의 설명도 포함시켜주세요. 
    나머지 2개의 문제는 서술형으로, choices는 '빈칸'으로 표시하고, correct_answer와 explanation을 문제에 맞게 서술형 답변으로 제공해주세요.
    """

    output_template = """
    다음은 반환 JSON 포맷의 예시이다. 제시하는 JSON 포맷에 맞게 출력해야 한다.
    JSON FORMAT:
    {
    "quiz_questions": [
        {
        "case": 0,
        "question": "",
        "choices": [
            "",
            "",
            "",
            ""
        ],
        "correct_answer": "",
        "explanation": ""
        },
        {
        "case": 0,
        "question": "",
        "choices": [
            "",
            "",
            "",
            ""
        ],
        "correct_answer": "",
        "explanation": ""
        },
        {
        "case": 1,
        "question": "",
        "choices": "빈칸",
        "correct_answer": "",
        "explanation": ""
        },
        {
        "case": 1,
        "question": "",
        "choices": "빈칸",
        "correct_answer": "",
        "explanation": ""
        }
        ...(생략)
    ]
    }
    """
    
    # 문제 생성을 위한 프롬프트 설정
    message = [
        {"role": "system", "content": prompt_setting + output_template},
        {"role": "user", "content": contents}
    ]
    
    # JSON 모드를 사용하여 4개의 문제 생성 및 응답 받기
    response_json = client.chat.completions.create(
        model="gpt-4-0125-preview",
        response_format={"type": "json_object"},
          messages=message
    )

    # 응답에서 문제 추출 및 출력
    #print(response_json.choices[0].message.content)
    
    # JSON 문자열을 파이썬 딕셔너리로 변환
    response = json.loads(response_json.choices[0].message.content)
    
    return response

# 유저의 입력을 벡터화시키는 함수
def embedding(user_input):
    
    # input_data를 지정 위치에 저장함
    file_path = f"./.cache/files/test.txt"
    with open(file_path, "w") as f:
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