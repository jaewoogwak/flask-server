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
    Your role is as a study mentor who creates Quizzes. {boundary}.
    Quizs should consist of {num_multiple_choice} multiple-choice Quizzes and {num_short_answer} short-answer Quizzes. Answer in korean.
    """

    context = """
    Create Quiz based on the following conditions :
    The entire response should be organized into an array with the key "quiz_questions".
    "case" is the type of Quiz, set to 0 for multiple-choice Quizzes and 1 for short-answer Quizzes.
    "question" is the name of the Quiz. For multiple choice, explicitly state in the Quiz that you want to choose the closest correct answer.
    "choice" is the Quiz choices, set to 4 for multiple choice and '빈칸' for short answer. Label multiple-choice statements (“1.”, “2.”, “3.”, “4.”).
    "correct_answer" is the correct answer to the Quiz. For multiple choice, provide the correct answer choice number.
    "explanation" is an explanation for the correct answer.
    "intent" is the intent of the Quiz. Describe what you're asking the person solving the Quiz to do when you create it, and how the Quiz is intended to be solved.
    """

    input_data = """"""

    output_template = """
    The following is an example of the return JSON format. Make sure to output to the JSON format you present.
    Ensure that all characters in the text are properly escaped to be valid JSON. This includes escaping backslashes (\\), double quotes ("), new lines (\\n), and any other characters that need to be escaped in JSON strings.
    
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

    def set_num_Quizs(self, num_Quizs):
        self.num_multiple_choice = num_Quizs // 2
        self.num_short_answer = num_Quizs - self.num_multiple_choice

    def set_user_input(self, text):
        self.input_data = "<Content start>" + text + "<Content end>"
        
    def set_customize_context(self, user_prompt):
        self.context += user_prompt

    def set_freedom_size(self, choice):
        if choice == 0:
            self.boundary = "Use external knowledge in addition to your input data"
        else:
            self.boundary = "All Quizzes you create must be validated based on the input data"
    
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
    Ensure that all characters in the text are properly escaped to be valid JSON. This includes escaping backslashes (\\), double quotes ("), new lines (\\n), and any other characters that need to be escaped in JSON strings.

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
        You are a tutor who provides feedback on incorrect questions and provides direction for learning.

        The full response should be returned in JSON format, consisting of the key-value pairs "index", "feedback", and "isCorrect".

        "index" should return the "index" value as entered.

        "feedback" is the feedback for the question you want to give the student.
        If the student selects an incorrect option, you MUST include an explanation of why the option is incorrect.
        It should also include why the correct answer choice is the correct answer.
        The feedback should also address the intent of the question and include which concepts need further study.

        "isCorrect" indicates whether the response is correct or not.
        You should return 1 if the value of "correctAnswer" and the value of "userAnswer" you entered are the same, otherwise return 0.
        The isCorrect value above must be of type int.

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
    Ensure that all characters in the text are properly escaped to be valid JSON. This includes escaping backslashes (\\), double quotes ("), new lines (\\n), and any other characters that need to be escaped in JSON strings.
    
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
    Ensure that all characters in the text are properly escaped to be valid JSON. This includes escaping backslashes (\\), double quotes ("), new lines (\\n), and any other characters that need to be escaped in JSON strings.

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