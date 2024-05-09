from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from concurrent.futures import ThreadPoolExecutor
from config import KEY
from .prompt import marking_problem
import json

chat = ChatOpenAI(
            model_name="gpt-4-turbo",
            openai_api_key= KEY,
            temperature=0.1,
            streaming=True
        )


# 1. 문제 생성 멀티스레드 처리
def feedback_main(thread_count, input_json):
    # 문제 수만큼 응답 생성
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        response = list(executor.map(feedback_split, input_json))
        
    return response


# 2. 문제 객관식, 단답형 분할
def feedback_split(input_json):

    # 2-1. 단답형 문제 채점
    if input_json["choices"] == "빈칸":
        return feedback_subjective(input_json)
        
    # 2-2. 객관식 문제 채점
    else:
        return feedback_objective(input_json)


# 2-1. 객관식 문제 피드백 생성
def feedback_objective(input_json):
    feedback = marking_problem()

    prompts = [
        ("intro", PromptTemplate.from_template(feedback.objective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]

    full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=prompts
    )

    chain = full_prompt | chat

    result = chain.invoke({
        "question": input_json
    })

    return result.content


# 2-2. 주관식 문제 채점 및 피드백 작성
def feedback_subjective(input_json):
    feedback = marking_problem()

    prompts = [
        ("intro", PromptTemplate.from_template(feedback.subjective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]

    full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=prompts
    )

    chain = full_prompt | chat

    result = chain.invoke({
        "question": input_json
    })

    return result.content