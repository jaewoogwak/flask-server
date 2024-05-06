from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from concurrent.futures import ThreadPoolExecutor
from config import KEY

chat = ChatOpenAI(
            openai_api_key= KEY,
            temperature=0.1,
            streaming=True
        )
             
# 1. 문제 생성 멀티스레드 처리
def feedback_main(self):

    # 문제 수만큼 응답 생성
    with ThreadPoolExecutor(max_workers=10) as executor:
        response = list(executor.map(self.feedback_split, self.input_json))
    
    return response


# 2. 문제 객관식, 단답형 분할
def feedback_split(self, input_json: list):
    
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
            return self.feedback_objective(input_json)
    
    # 주관식 문제일 경우
    else:
        # 2-2. 주관식 채점 및 피드백 생성
        return self.feedback_subjective(input_json)


# 2-1. 객관식 문제 피드백 생성
def feedback_objective(self, input_json: list):
    intro = PromptTemplate.from_template(
        """
        You are a tutor who gives feedback on the wrong question and tells you the direction to study.

        The full response must be returned in JSON format consisting of key-value pairs "index", "feedback", and "isCorrect".
        Any other JSON key except all "index" values, values must be double-quoted.

        "index" should return the value of the entered "index".

        "feedback" is a feedback on the problem to give to the user.
        You should give feedback by referring to the commentary presented to see why the wrong option is wrong and why the right option is correct.
        In addition, the intention of the problem and what additional studies are needed should be included in the feedback.

        "isCorrect" indicates correct answer.
        You must return 1 if the value of "isCorrect" entered is "True" or 0 if "False".

        All feedback must be in Korean.
        The feedback should be in one line without changing the line.
        """
    )

    example = PromptTemplate.from_template(
        """
        This are some examples of how you talk:
    
        Example 1
        Human: {example_question1}
        You: {example_answer1}

        Example 2
        Human: {example_question2}
        You: {example_answer2}

        Example 3
        Human: {example_question3}
        You: {example_answer3}
        """
    )

    start = PromptTemplate.from_template(
        """
        Start now!

        Human: {question}
        You:
        """
    )

    final = PromptTemplate.from_template(
        """
        {intro}

        {example}

        {start}
    """
    )

    prompts = [
        ("intro", intro),
        ("example", example),
        ("start", start)
    ]

    full_prompt = PipelinePromptTemplate(
        final_prompt=final,
        pipeline_prompts=prompts
    )

    chain = full_prompt | self.chat

    result = chain.invoke({
        "example_question1":"""{
            "index":0,
            "question":"다음 중 복합 리터럴을 정의하는 연산자를 지원하는 C의 버전은?",
            "choices":["1. C89","2. C99","3. C11","4. C++"],
            "correctAnswer":"2",
            "userAnswer":"3",
            "isCorrect":"False",
            "explanation":"복합 리터럴은 C99 규격에서 새롭게 도입된 기능입니다. 이를 통해 배열이나 구조체 같은 데이터 타입을 초기화할 수 있습니다.",
            "intent":"프로그래밍 언어의 버전별 특성과 변경사항을 이해하는 능력 검증"
            }""",
            
        "example_answer1": """{
            "index": 0,
            "feedback": "잘못 고른 선택지는 '3. C11'입니다. 복합 리터럴을 정의하는 연산자를 지원하는 C의 버전은 '2. C99'입니다. 복합 리터럴은 C99 규격에서 새롭게 도입된 기능으로, 배열이나 구조체와 같은 데이터 타입을 초기화할 수 있게 해줍니다. 이 문제는 프로그래밍 언어의 버전별 특성과 변경사항을 이해하는 능력을 검증하기 위해 출제되었습니다. C언어의 버전별 특성과 변경사항에 대해 더 공부해보는 것이 좋을 것 같습니다.",
            "isCorrect": 0
            }""",

        "example_question2":"""{
            "index":4,
            "question":"어느 언어가 후위 증감 연산자 "++"와 "--"을 지원합니까?",
            "choices":["1. FORTRAN","2. Ada","3. C","4. Pascal"],
            "correctAnswer":"3",
            "userAnswer":"4",
            "isCorrect":"False",
            "explanation":"C 언어는 후위 증감 연산자 "++"와 "--"을 제공합니다. 이 연산자들은 변수의 값을 증가하거나 감소시킨 후 평가됩니다.",
            "intent":"후위 증감 연산자를 지원하는 언어에 대한 이해를 묻는 문제입니다."
            }""",
            
        "example_answer2": """{
            "index": 4,
            "feedback": "잘못 고른 선택지는 '4. Pascal'입니다. Pascal은 후위 증감 연산자를 제공하지 않습니다. 후위 증감 연산자 '++'와 '--'을 지원하는 언어는 '3. C'입니다. 이 연산자들은 변수의 값을 증가하거나 감소시킨 후 평가됩니다. 문제의 의도는 후위 증감 연산자를 지원하는 언어에 대한 이해를 확인하는 것입니다. 후위 증감 연산자에 대해 더 공부하시면 도움이 될 것입니다.",
            "isCorrect": 0
            }""",

        "example_question3":"""{
            "index":5,
            "question":"어느 연산자가 C언어에서 우선순위가 가장 높습니까?",
            "choices":["1. +","2. /","3. sizeof","4. &&"],
            "correctAnswer":"3",
            "userAnswer":"2",
            "isCorrect":"False",
            "explanation":"C 언어에서 "sizeof" 연산자는 가장 높은 우선순위를 가지는 연산자 중 하나입니다. 이 연산자는 피연산자의 크기를 측정합니다.",
            "intent":"C 언어 연산자의 우선순위에 대한 이해를 평가하는 문제입니다."
            }""",
            
        "example_answer3": """{
            "index": 5,
            "feedback": "잘못 고른 선택지는 '2. /'입니다. '/'는 'sizeof' 연산자보다 우선순위가 낮습니다. 정답은 '3. sizeof'입니다. C언어에서 'sizeof' 연산자는 가장 높은 우선순위를 가지는 연산자 중 하나입니다. 이 연산자는 피연산자의 크기를 측정하는 기능을 합니다. 이 문제는 C언어 연산자의 우선순위에 대한 이해를 평가하기 위해 출제되었습니다. C언어의 연산자 우선순위에 대해 더 공부가 필요한 것 같습니다.",
            "isCorrect": 0
            }""",


        "question": input_json
        }
    )
    
    return result.content


# 2-2. 주관식 문제 채점 및 피드백 작성
def feedback_subjective(self, input_json: list):
    intro = PromptTemplate.from_template(
        """
        You are a strict teacher.
        All you have to do is score and give feedback on the answers to the short answer questions written by the student.

        The full response must be returned in JSON format consisting of key-value pairs "index", "feedback", and "isCorrect".
        Any other JSON key except all "index" values, values must be double-quoted. 

        "index" can be returned to the value of the input "index".

        "feedback" is a feedback on the problem to give to the user.
        The feedback should include both whether it can be recognized as a correct answer and feedback to advise the user to solve similar problems next time.
        Whether or not the correct answer is recognized is reviewed by comparing the correct answer in the question with the correct answer selected by the user.
        The correct answer to the question is "correctAnswer" and the user's correct answer is "userAnswer".
        If the correct answer to the question and the answer entered by the user fall within the category of the correct answer, consider it as the correct answer.
        This process should be very strict, and the given context and information should be identified, verified, and presented to the user. 
        And if the answer entered by the student is wrong, you should give feedback by referring to why it is wrong, what is the correct answer, and the commentary presented.
        Also, the intention of the problem and what additional studies are needed should be included in the feedback.

        "isCorrect" is the correct answer, and when comparing the answer entered by the user with the answer of the question, it is set to 1 if it is recognized as the correct answer, or 0 if not.
        "isCorrect" must be either 1 or 0 and must be strictly case sensitive.

        Please make sure to answer in Korean.
        """
    )

    start = PromptTemplate.from_template(
        """
        Start now!

        Human: {question}
        You:
        """
    )

    final = PromptTemplate.from_template(
        """
        {intro}

        {start}
    """
    )

    prompts = [
        ("intro", intro),
        ("start", start)
    ]

    full_prompt = PipelinePromptTemplate(
        final_prompt=final,
        pipeline_prompts=prompts
    )

    chain = full_prompt | self.chat

    result = chain.invoke({
        "question": input_json
        }
    )

    return result.content