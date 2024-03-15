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
from config import KEY, Groq_api_key
from groq import Groq

client = OpenAI()    

client_groq = Groq(
    api_key=Groq_api_key,
)

prompt_setting = """
생성할 문제의 형식은 다음과 같습니다:
- 각 문제는 '문제명'으로 시작합니다. 문제 번호 라벨링은 하지 말아주세요.
- 객관식 문제의 경우, '입력'이라는 단어 다음에 선택지가 A), B), C), D)로 제시됩니다.
- 단답형 또는 서술형 문제의 경우, '입력: ____________________'이라는 텍스트와 함께 제시됩니다.
- 각 문제에는 해설이 포함됩니다.
- 문제 생성 이외에 텍스트는 작성하지 마세요. 오직 문제 형식대로만 출력되어야 합니다.
- 문제 생성 예시를 제공하니 그 예시의 형식대로 출력해주세요.

이 규칙을 따라서, 사용자가 제시한 내용을 기반으로 하는 문제를 생성해주세요. 문제 문항은 3개, 문제 유형은 랜덤으로 해주세요. 제공할 내용은 OCR을 거쳐 얻은
데이터로 특수문자(개행문자 등)나 관련 없는 내용이 포함되어 있는데 이를 제외한 내용에서 문제를 생성할 수 있도록 해주세요.
"""

output_template = """
문제 생성 예시는 다음과 같습니다.
문제 생성 예시(객관식):
문제명: 2x + 6 = 12의 해는 무엇인가요?
   입력:
   A) 2
   B) 3
   C) 4
   D) 5
   해설: 이 방정식을 풀기 위해서는, 먼저 양변에서 6을 빼고, 그 결과를 2로 나누어 x의 값을 찾습니다.
문제 생성 예시(서술형 및 단답형):
문제명: 2x + 6 = 12의 해는 무엇인가요?
   입력: ____________________
   해설: 이 방정식을 풀기 위해서는, 먼저 양변에서 6을 빼고, 그 결과를 2로 나누어 x의 값을 찾습니다. 따라서 답은 12입니다.
"""

def request_prompt(contents):
    # 문제 생성을 위한 프롬프트 설정
    message = [
        {"role": "system", "content": prompt_setting + output_template},
        {"role": "user", "content": contents}
    ]

    # gpt 비활성화
    # completion = client.chat.completions.create(
    #     model="gpt-4-0125-preview",
    #     messages=message
    # )
    
    completion = client_groq.chat.completions.create(
        messages=message,
        model="mixtral-8x7b-32768",
    ) 
    
    print(completion.choices[0].message)
    response = completion.choices[0].message.content
    
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