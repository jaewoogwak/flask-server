import json

# 문제 생성 프롬프트 정의 클래스
class make_problem_prompt:
    def __init__(self, text, num_multiple_choice=2, num_short_answer=2):
        self.input_data = text
        self.num_multiple_choice = num_multiple_choice
        self.num_short_answer = num_short_answer
        # 기본값 설정
        self.boundary = " " 
    
    instruction = """
    Your role is as a study mentor who creates questions based on the data you enter. {boundary}.
    Questions should consist of {num_multiple_choice} multiple-choice questions and {num_short_answer} short-answer questions.
    Each question must contain case, question, choices, correct_answer, explanation, and intent. Answer in korean.
    """

    context = """
    The entire response should be organized into an array with the key "quiz_questions".
    Multiple choice is the type of question, and short answer is the type where a keyword is the answer.
    "case" is the type of question, set to 0 for multiple choice questions and 1 for short answer questions.
    "question" is the name of the question you generate based on the input data. For multiple choice, explicitly state in the question that you want to choose the closest correct answer.
    "choice" is the question choices, set to 4 for multiple choice and '빈칸' for short answer. Label multiple-choice statements (“1.”, “2.”, “3.”, “4.”).
    "correct_answer" is the correct answer to the question. For multiple choice, provide the correct answer choice number.
    "explanation" is an explanation for the correct answer.
    "intent" is the intent of the question. Describe what you're asking the person solving the question to do when you create it, and how the question is intended to be solved.
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

    def set_freedom_size(self, choice):
        if choice == 0:
            self.boundary = "All questions you create must be validated based on the input data"
        else:
            self.boundary = "Use external knowledge in addition to your input data"
    
    def get_system_prompt(self):
        return self.instruction.format(
            boundary=self.boundary,
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
    Your job is to describe what's in the image based on the material you've entered.
    Please explain all texts that are not included in the table, graph, or diagram.
    Never mention the numbers, examples, or words in the table, graph, or diagram.
    Never mention the names of the nodes.
    You must only describe the table or graph, without numbers or words, and what concept it covers.
    Return the response in JSON format.
    The response should include text, images, and descriptions. Please generate responses in Korean.
    """

    context = """
    The entire response should consist of an array with the key image_detections.
    text is the text portion of the question and should consist of pure text only, not inside tables, graphs, diagrams, etc. 
    image should never refer to specific figures, examples, or words inside the picture, but only to what concept the picture is intended to illustrate.
    The explanation should be a general description of what concept the image is illustrating as a whole, taking into account the text above and the image as a whole.
    """
    
    input_data = """"""

    output_template = """
    The following is an example of the return JSON format. Make sure to output to the JSON format you present.

    JSON FORMAT:
    {
        "image_detections": [
            {
                "text": "",                          //string
                "image": "",                         //string
                "explanation": ""                   //string
            },
            {
                "text": "",                          //string
                "image": "",                         //string
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
            self.context += "\n\nAdditional description of the image : " + user_prompt


# 피드백 생성 프롬프트 정의 클래스
class marking_problem:
    objective_intro = """
        You are a tutor providing feedback on incorrect questions and pointing out learning directions.

        The full response should be returned in JSON format, consisting of the key-value pairs "index", "feedback", and "isCorrect".
        Except for the "index" value, the values of all other JSON keys must be enclosed in double quotes.

        "index" should return the value of "index" as entered.

        "feedback" is the feedback on the question to give to the student.
        If the question is incorrect, you must include an explanation of why the student's incorrect choice is incorrect.
        It should also include why the correct answer choice is correct.
        The feedback should also include the intent of the question and what further research is needed.

        "isCorrect" indicates whether the answer is correct or not.
        It should return 1 if the entered value of "correctAnswer" and the value of "userAnswer" are the same, and 0 otherwise.

        All feedback must be written in Korean.
        Feedback must be written on a single line with no line breaks.
    """

    subjective_intro = """
        You're an excellent tutor.
        Your job is to grade and provide feedback on students' answers to short-answer questions they submit.

        Below is a question, a student response, and a model answer. When you evaluate a student's response, consider these points when grading

        1. Accept an answer as correct if it includes the key concepts and keywords the question asks for, even if it's not identical to the model answer. 
        2. Even if the sentence structure or word choice is different from the model answer, accept the answer as correct if it conveys a similar message.
        3. Award extra credit if your answer goes into more detail and depth than the model answer.
        4. If you leave out key concepts or include irrelevant content, you may lose points.

        Based on the above criteria, carefully review students' responses and treat similar responses as correct, but award points based on how closely they match the model answer.

        The full response should be returned in JSON format with the key-value pairs "index", "feedback", and "isCorrect".
        All other JSON keys and values must be enclosed in double quotes, except for the value of "index". 

        "index" should return the value of "index" as it was entered.

        "feedback" is the feedback for the question that you want to give to the user.
        The feedback should mention the user's answer and tell them whether it's correct or incorrect.
        If the answer they entered is incorrect, the feedback should tell them why it is incorrect, what the correct answer is, and refer to the commentary provided.
        If incorrect, the feedback should also include the intent of the question and what additional study is needed.

        "isCorrect" is an indicator of whether the answer is correct, set to 1 if the user's answer is recognized as correct when compared to the answer in the question, and 0 otherwise.
        "isCorrect" must result in a value of either 1 or 0 and is strictly case sensitive.

        Answers must be in Korean.
    """

    start = """
        start now!

        Human: {question}
        You:
    """

    final = """
        {intro}

        {start}
    """


class make_objective:
    def __init__(self, text, num_multiple_choice=2):
        self.input_data = text
        self.num_multiple_choice = num_multiple_choice
    
    instruction = """
    Your role is as a study mentor who creates questions based on the data you enter. All questions you create must be validated based on the input data.
    Questions should be organized into multiple choice {num_multiple_choice} questions. Answer in korean.
    """

    context = """
    The entire response should be organized into an array with the key quiz_questions.
    case is the type of question, set to 0.
    question is the name of the question you generate based on the input data.
    choice is the question choices, set to 4 for multiple choice. Label multiple-choice statements (“1.”, “2.”, “3.”, “4.”).
    correct_answer is the correct answer to the question. Provide the correct answer choice number.
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
        ]
    }
    """
    
class make_subjective:
    def __init__(self, text, num_short_answer=2):
        self.input_data = text
        self.num_short_answer = num_short_answer
    
    instruction = """
    Your role is as a study mentor who creates questions based on the data you enter. All questions you create must be validated based on the input data.
    Questions should be organized into short answer {num_short_answer} questions. Answer in korean.
    """

    context = """
    The entire response should be organized into an array with the key quiz_questions.
    answer is the type where a keyword is the answer.
    case is the type of question, set to 1.
    question is the name of the question you generate based on the input data.
    choice is the question choices, set to '빈칸'.
    correct_answer is the correct answer to the question.
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
                "case": 1, // integer
                "question": "", // string
                "choices": "빈칸", // string
                "correct_answer": "", // string
                "explanation": "", // string
                "intent": "" // string
            },
        ]
    }
    """