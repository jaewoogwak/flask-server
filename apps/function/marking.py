from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from concurrent.futures import ThreadPoolExecutor
from config import KEY
from .prompt import marking_problem
from langchain_core.output_parsers import JsonOutputParser

chat = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=KEY,
    temperature=0.1,
    streaming=True
)

def initialize_feedback():
    feedback = marking_problem()
    
    objective_prompts = [
        ("intro", PromptTemplate.from_template(feedback.objective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]
    
    subjective_prompts = [
        ("intro", PromptTemplate.from_template(feedback.subjective_intro)),
        ("start", PromptTemplate.from_template(feedback.start))
    ]

    objective_full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=objective_prompts
    )
    
    subjective_full_prompt = PipelinePromptTemplate(
        final_prompt=PromptTemplate.from_template(feedback.final),
        pipeline_prompts=subjective_prompts
    )

    output_parser = JsonOutputParser()
    
    return objective_full_prompt, subjective_full_prompt, output_parser

def feedback_main(thread_count, input_json):
    # 초기 설정 수행
    objective_full_prompt, subjective_full_prompt, output_parser = initialize_feedback()

    # 문제 수만큼 응답 생성
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        response = list(executor.map(lambda x: feedback_split(x, objective_full_prompt, subjective_full_prompt, output_parser), input_json))
        
    return response

def feedback_split(input_json, objective_full_prompt, subjective_full_prompt, output_parser):
    # 2-1. 단답형 문제 채점
    if input_json["choices"] == "빈칸":
        return feedback_subjective(input_json, subjective_full_prompt, output_parser)
        
    # 2-2. 객관식 문제 채점
    else:
        return feedback_objective(input_json, objective_full_prompt, output_parser)

def feedback_objective(input_json, full_prompt, output_parser):
    chain = full_prompt | chat
    result = chain.invoke({"question": input_json})
    
    parsed_response = output_parser.parse(result.content)
    return parsed_response

def feedback_subjective(input_json, full_prompt, output_parser):
    chain = full_prompt | chat
    result = chain.invoke({"question": input_json})
    parsed_response = output_parser.parse(result.content)
    return parsed_response