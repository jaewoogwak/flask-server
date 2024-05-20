from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from .prompt import make_problem_prompt, img_detecting_prompt
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
from config import KEY
import os

def request_prompt(contents, options=None):
    if options is None:
        return {"error": "Options are missing. Please provide options."}
    
    mutiple_num = options["multipleChoice"]
    short_num = options["shortAnswer"]
    custom_prompt = options["custom_prompt"]
    LectureOnly = options["isLectureOnly"]
    
    llm = ChatOpenAI(
            model_name="gpt-4o", 
            temperature=0.7,
            streaming = False,
            
        )
    
    prompt = make_problem_prompt(contents, mutiple_num, short_num)
    prompt.set_custom_prompt(custom_prompt)
    prompt.set_freedom_size(LectureOnly)
    
    system_prompt = prompt.get_system_prompt()
    user_input = prompt.get_user_input()

    output_parser = JsonOutputParser()

    prompt_template = PromptTemplate(
        template="{system_prompt}\n\n{format_instructions}\n\n{user_input}",
        input_variables=["system_prompt", "user_input"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    _prompt = prompt_template.format(system_prompt=system_prompt, user_input=user_input)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=_prompt)
    ]

    response = llm(messages)
    parsed_response = output_parser.parse(response.content)

    return parsed_response

def request_prompt_img_detecting(contents, options=None):
    if options is None:
        return {"error": "Options are missing. Please provide options."}
    
    custom_prompt = options["custom_prompt"]

    llm = ChatOpenAI(
            model_name="gpt-4o", 
            temperature=0.2,
            streaming = False,
    )

    prompt = img_detecting_prompt(contents)
    prompt.set_custom_prompt(custom_prompt)
    system_prompt = prompt.get_system_prompt()
    user_input = prompt.get_user_input()

    output_parser = JsonOutputParser()
    
    # 문제 생성을 위한 프롬프트 설정
    message = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=[
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{user_input}"}}
        ])
    ]
    
    response = llm(message)
    parsed_response = output_parser.parse(response.content)
    
    return parsed_response

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