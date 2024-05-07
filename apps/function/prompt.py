import json

# 문제 생성 프롬프트 정의 클래스
class make_problem_prompt:
    def __init__(self, text, num_multiple_choice=2, num_short_answer=2):
        self.input_data = text
        self.num_multiple_choice = num_multiple_choice
        self.num_short_answer = num_short_answer
    
    instruction = """
    Your role is as a study mentor who creates questions based on the data you enter. All questions you create must be validated based on the input data.
    Please return responses in JSON format.
    Questions should be organized into multiple choice {num_multiple_choice} questions and short answer {num_short_answer} questions.
    Each question must contain case, question, choices, correct_answer, explanation, and intent. Unify language in output
    """

    context = """
    The entire response should be organized into an array with the key quiz_questions.
    Multiple choice is the type of question, and short answer is the type where a keyword is the answer.
    case is the type of question, set to 0 for multiple choice questions and 1 for short answer questions.
    question is the name of the question you generate based on the input data.
    choice is the question choices, set to 4 for multiple choice and '빈칸' for short answer. Label multiple-choice statements (“1.”, “2.”, “3.”, “4.”).
    correct_answer is the correct answer to the question. For multiple choice, provide the correct answer choice number.
    explanation is an explanation for the correct answer.
    intent is the intent of the question. Describe what you're asking the person solving the question to do when you create it, and how the question is intended to be solved.
    """

    input_data = """"""

    output_template = """
    The following is an example of the return JSON format. Make sure to output to the JSON format you present.

    JSON FORMAT:
    {
        "quiz_questions": [
            {
                "case": 0, // integer
                "question": "",  // string

                "choices": ["1.", "2.", "3.", "4."], // array of strings
                "correct_answer": "", // integer
                "explanation": "", // string
                "intent": ""  // string
            },
            {
                "case": 1, // integer
                "question": "", // string
                "choices": "빈칸", // string
                "correct_answer": "", // string
                "explanation": "", // string
                "intent": "" // string
            }
        ]
    }
    """

    def set_num_questions(self, num_questions):
        self.num_multiple_choice = num_questions // 2
        self.num_short_answer = num_questions - self.num_multiple_choice

    def set_user_input(self, text):
        self.input_data = text
        
    def set_customize_context(self, user_prompt):
        self.context += user_prompt

    def get_system_prompt(self):
        return self.instruction.format(
            num_multiple_choice=self.num_multiple_choice,
            num_short_answer=self.num_short_answer
        ) + self.context + self.output_template

    def set_custom_prompt(self, user_prompt):
        if user_prompt.strip() :
            self.context += "\n\n문제 생성 중 추가적인 요구 : " + user_prompt
    
    def get_user_input(self):
        return self.input_data
 
 
 # 이미지 디텍팅 프롬프트 정의 클래스
class img_detecting_prompt:    
    def __init__(self, text):
        self.input_data = text
    instruction = """
    당신의 역할은 입력한 자료의 이미지를 기반으로 이미지의 내용에 대해 설명해주는 것입니다.
    표나 그래프, 다이어그램에 포함되지 않은 텍스트들은 그대로 출력해주세요.
    Never mention the numbers, examples, or words in the table, graph, or diagram.
    Never mention the node's name
    반드시 수치나 단어가 들어가지 않은, 어떤 개념을 다루는 표와 그래프인지만을 설명해야 합니다.
    응답은 JSON 형식으로 반환해주세요.
    응답은 text, image, explanation을 포함해야 합니다. 응답 생성은 한글로 해주세요.
    """

    context = """
    전체 응답은 image_detections라는 키를 가진 배열로 구성되어야 합니다.
    text는 문제의 텍스트 부분으로, 표나 그래프, 다이어그램 등의 내부에 있지 않은 순수한 텍스트들로만 구성되어야 합니다. 
    image는 절대로 그림 내부에 있는 구체적인 수치, 예시, 단어를 언급해서는 안되며, 어떤 개념을 설명하기 위한 그림인지에 대해서만 설명해야 합니다.
    explanation은 위 text와 image를 전체적으로 고려한, 해당 이미지가 전체적으로 어떠한 개념을 설명하고 있는지에 대해 전반적인 설명이 들어가야 합니다.
    """
    
    input_data = """"""

    output_template = """
    다음은 반환 JSON 포맷의 예시입니다. 제시하는 JSON 포맷에 맞게 출력해야 합니다.

    JSON FORMAT:
    {
        "image_detections": [
            {
                "text": ""                          //string
                "image": ""                         //string
                "explanation": ""                   //string
            },
            {
                "text": ""                          //string
                "image": ""                         //string
                "explanation": ""                   //string
            }
        ]
    }
    """
    def get_system_prompt(self):
        return self.instruction + self.context + self.output_template
    
    def get_user_input(self):
        return self.input_data
    
    def set_custom_prompt(self, user_prompt):
        if user_prompt.strip() :
            self.context += "\n\n이미지에 대한 추가적인 설명 : " + user_prompt
    
 
 # 문제 채점 및 피드백 정의 프롬프트
class marking_problem:
    objective_intro = """
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

    subjective_intro = """
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

    example = """
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

    start = """
        start now!

        Human: {question}
        You:
    """

    objective_final = """
        {intro}
    
        {example}

        {start}
    """

    subjective_final = """
        {intro}

        {start}
    """

    example_question1 = """{
            "index":0,
            "question":"다음 중 복합 리터럴을 정의하는 연산자를 지원하는 C의 버전은?",
            "choices":["1. C89","2. C99","3. C11","4. C++"],
            "correctAnswer":"2",
            "userAnswer":"3",
            "isCorrect":"False",
            "explanation":"복합 리터럴은 C99 규격에서 새롭게 도입된 기능입니다. 이를 통해 배열이나 구조체 같은 데이터 타입을 초기화할 수 있습니다.",
            "intent":"프로그래밍 언어의 버전별 특성과 변경사항을 이해하는 능력 검증"
    }"""
    
    example_answer1 = """{
            "index": 0,
            "feedback": "잘못 고른 선택지는 '3. C11'입니다. 복합 리터럴을 정의하는 연산자를 지원하는 C의 버전은 '2. C99'입니다. 복합 리터럴은 C99 규격에서 새롭게 도입된 기능으로, 배열이나 구조체와 같은 데이터 타입을 초기화할 수 있게 해줍니다. 이 문제는 프로그래밍 언어의 버전별 특성과 변경사항을 이해하는 능력을 검증하기 위해 출제되었습니다. C언어의 버전별 특성과 변경사항에 대해 더 공부해보는 것이 좋을 것 같습니다.",
            "isCorrect": 0
    }"""
    
    example_question2 = """{
            "index":4,
            "question":"어느 언어가 후위 증감 연산자 "++"와 "--"을 지원합니까?",
            "choices":["1. FORTRAN","2. Ada","3. C","4. Pascal"],
            "correctAnswer":"3",
            "userAnswer":"4",
            "isCorrect":"False",
            "explanation":"C 언어는 후위 증감 연산자 "++"와 "--"을 제공합니다. 이 연산자들은 변수의 값을 증가하거나 감소시킨 후 평가됩니다.",
            "intent":"후위 증감 연산자를 지원하는 언어에 대한 이해를 묻는 문제입니다."
    }"""

    example_answer2 = """{
            "index": 4,
            "feedback": "잘못 고른 선택지는 '4. Pascal'입니다. Pascal은 후위 증감 연산자를 제공하지 않습니다. 후위 증감 연산자 '++'와 '--'을 지원하는 언어는 '3. C'입니다. 이 연산자들은 변수의 값을 증가하거나 감소시킨 후 평가됩니다. 문제의 의도는 후위 증감 연산자를 지원하는 언어에 대한 이해를 확인하는 것입니다. 후위 증감 연산자에 대해 더 공부하시면 도움이 될 것입니다.",
            "isCorrect": 0
    }"""
    
    example_question3 = """{
            "index":5,
            "question":"어느 연산자가 C언어에서 우선순위가 가장 높습니까?",
            "choices":["1. +","2. /","3. sizeof","4. &&"],
            "correctAnswer":"3",
            "userAnswer":"2",
            "isCorrect":"False",
            "explanation":"C 언어에서 "sizeof" 연산자는 가장 높은 우선순위를 가지는 연산자 중 하나입니다. 이 연산자는 피연산자의 크기를 측정합니다.",
            "intent":"C 언어 연산자의 우선순위에 대한 이해를 평가하는 문제입니다."
    }"""

    example_answer3 = """{
            "index": 5,
            "feedback": "잘못 고른 선택지는 '2. /'입니다. '/'는 'sizeof' 연산자보다 우선순위가 낮습니다. 정답은 '3. sizeof'입니다. C언어에서 'sizeof' 연산자는 가장 높은 우선순위를 가지는 연산자 중 하나입니다. 이 연산자는 피연산자의 크기를 측정하는 기능을 합니다. 이 문제는 C언어 연산자의 우선순위에 대한 이해를 평가하기 위해 출제되었습니다. C언어의 연산자 우선순위에 대해 더 공부가 필요한 것 같습니다.",
            "isCorrect": 0
    }"""