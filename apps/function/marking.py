from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from concurrent.futures import ThreadPoolExecutor
from config import KEY
from .prompt import marking_problem

chat = ChatOpenAI(
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

    # 객관식 문제일 경우
    if "isCorrect" in input_json:

        # 2-0. 객관식 문제가 맞았을 경우 -> 빈 피드백 리턴
        if input_json["isCorrect"] == "True":
            feedback = {
                "index": input_json["index"],
                "feedback": " ",
                "isCorrect": 1
            }
            return feedback

        # 2-1. 객관식 문제가 틀렸을 경우 -> 피드백 생성
        else:
            return feedback_objective(input_json)
        
    # 주관식 문제일 경우
    else:
        # 2-2. 주관식 채점 및 피드백 생성
        return feedback_subjective(input_json)


# 2-1. 객관식 문제 피드백 생성
def feedback_objective(input_json):
    feedback = marking_problem()

    prompts = [
        ("intro", PromptTemplate.from_template(feedback.objective_intro)),
        ("example", PromptTemplate.from_template(feedback.example)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]

    full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.objective_final),
        pipeline_prompts=prompts
    )

    chain = full_prompt | chat

    result = chain.invoke({
        "example_question1": feedback.example_question1,
        "example_answer1": feedback.example_answer1,
        "example_question2": feedback.example_question2,
        "example_answer2": feedback.example_answer2,
        "example_question3": feedback.example_question3,
        "example_answer3": feedback.example_answer3,
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
        final_prompt=PromptTemplate.from_template(feedback.subjective_final),
        pipeline_prompts=prompts
    )

    chain = full_prompt | chat

    result = chain.invoke({
        "question": input_json
        }
    )

    return result.content