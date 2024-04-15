class make_problem_prompt:
    instruction = """
    당신의 역할은 입력한 데이터를 기반으로 문제를 만들어주는 스터디 멘토입니다. 생성하는 모든 문제는 입력 데이터를 기반으로 검증된 내용이어야 합니다.
    응답은 JSON 형식으로 반환해주세요.
    문제는 총 {num_questions}문제를 생성하고 문제 구성은 객관식 {num_multiple_choice}문제, 단답형 {num_short_answer}문제로 구성해주세요.
    각 문제는 case, question, choices, correct_answer, explanation, intent을 포함해야 합니다.
    """

    context = """
    전체 응답은 quiz_questions이라는 키를 가진 배열로 구성되어야 합니다.
    case는 문제의 유형으로, 객관식 문제의 경우 0, 단답식 문제의 경우 1로 설정해주세요.
    question은 입력 데이터를 기반으로 생성한 문제 명입니다.
    choice는 문제 선택지로, 객관식인 경우 문제 선택지는 4개이고, 단답형의 경우 '빈칸'으로 표시합니다.
    correct_answer는 문제의 정답 입니다.
    explanation은 정답에 대한 해설입니다. 문제의 정답이 왜 그런지 설명해주세요.
    intent는 문제 출제 의도에 대한 내용입니다. 문제를 생성할 때 문제를 푸는 사람에게 요구하는 것, 문제의 의도된 해결 방식을 기술합니다.
    """

    input_data = """"""

    output_template = """
    다음은 반환 JSON 포맷의 예시입니다. 제시하는 JSON 포맷에 맞게 출력해야 합니다.

    JSON FORMAT:
    {
        "quiz_questions": [
            {
                "case": 0,                        // integer
                "question": "",                   // string

                "choices": ["", "", "", ""],      // array of strings
                "correct_answer": "",             // string
                "explanation": "",                // string
                "intent": ""                      // string
            },
            {
                "case": 0,                        // integer
                "question": "",                   // string
                "choices": ["", "", "", ""],      // array of strings
                "correct_answer": "",             // string
                "explanation": "",                // string
                "intent": ""                      // string
            },
            {
                "case": 1,                        // integer
                "question": "",                   // string
                "choices": "빈칸",                  // string

                "correct_answer": "",             // string
                "explanation": "",                // string
                "intent": ""                      // string
            },
            {
                "case": 1,                        // integer
                "question": "",                   // string
                "choices": "빈칸",                  // string
                "correct_answer": "",             // string
                "explanation": "",                // string
                "intent": ""                      // string
            }
        ]
    }
    """

    def __init__(self, text, num_questions=4, num_multiple_choice=2, num_short_answer=2):
        self.input_data = text
        self.num_questions = num_questions
        self.num_multiple_choice = num_multiple_choice
        self.num_short_answer = num_short_answer

    def set_num_questions(self, num_questions):
        self.num_questions = num_questions
        self.num_multiple_choice = num_questions // 2
        self.num_short_answer = num_questions - self.num_multiple_choice

    def set_user_input(self, text):
        self.input_data = text

    def get_system_prompt(self):
        return self.instruction.format(
            num_questions=self.num_questions,
            num_multiple_choice=self.num_multiple_choice,
            num_short_answer=self.num_short_answer
        ) + self.context + self.output_template

    def get_user_input(self):
        return self.input_data