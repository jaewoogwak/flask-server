import json

class make_problem_prompt:
    instruction = """
    당신의 역할은 입력한 데이터를 기반으로 문제를 만들어주는 스터디 멘토입니다. 생성하는 모든 문제는 입력 데이터를 기반으로 검증된 내용이어야 합니다.
    응답은 JSON 형식으로 반환해주세요.
    문제는 총 {num_questions}문제를 생성하고 문제 구성은 객관식 {num_multiple_choice}문제, 단답형 {num_short_answer}문제로 구성해주세요.
    각 문제는 case, question, choices, correct_answer, explanation, intent을 포함해야 합니다.
    """

    context = """
    전체 응답은 quiz_questions이라는 키를 가진 배열로 구성되어야 합니다.
    객관식은 선지를 고르는 유형, 단답형은 키워드가 답이되는 유형입니다.
    case는 문제의 유형으로, 객관식 문제의 경우 0, 단답식 문제의 경우 1로 설정해주세요.
    question은 입력 데이터를 기반으로 생성한 문제 명입니다. 객관식, 단답형에 맞게 알맞은 문제 제시로 설정되었는지 검증하여 설정해주세요.
    choice는 문제 선택지로, 객관식인 경우 문제 선택지는 4개이고, 단답형의 경우 '빈칸'으로 표시합니다. 객관식 선택지를 넘버링으로 시작해주세요("1.", "2.", "3.", "4.")
    correct_answer는 문제의 정답 입니다. 객관식의 경우 정답 선택 번호를 제시해주세요.
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

                "choices": ["1.", "2.", "3.", "4."],      // array of strings
                "correct_answer": "",             // integer
                "explanation": "",                // string
                "intent": ""                      // string
            },
            {
                "case": 0,                        // integer
                "question": "",                   // string
                "choices": ["1.", "2.", "3.", "4."],      // array of strings
                "correct_answer": "",             // integer
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
        
    def set_customize_context(self, user_prompt):
        self.context += user_prompt

    def get_system_prompt(self):
        return self.instruction.format(
            num_questions=self.num_questions,
            num_multiple_choice=self.num_multiple_choice,
            num_short_answer=self.num_short_answer
        ) + self.context + self.output_template

    def get_user_input(self):
        return self.input_data
    
class marking_problem:
    instruction = """
    너의 역할은 사용자가 풀이한 문제 대한 피드백을 해주는 멘토입니다. 응답은 JSON 형식으로 반환해주세요. 사용자가 풀이한 문제에 대한 정보를 입력으로 주어지면
    입력에 대한 피드백을 반환하세요. 사용자가 풀이한 문제에 대한 정보는 JSON 형식으로 제공됩니다.
    피드백의 개수는 입력한 문제 수와 동일합니다. 피드백 내용으로는 index, feedback, iscorrect으로 구성됩니다.
    """
    
    context = """
    전체 응답은 output이라는 키를 가진 배열로 구성되어야 합니다.
    index는 문제 번호로 입력 받은 문제의 번호와 동일합니다. 해당 인덱스와 입력된 문제가 매치되어 각 문제에 피드백이 정확히 들어갈 수 있도록 합니다.
    feedback은 사용자에게 줄 해당 문제에 대한 피드백입니다. 피드백 내용은 문제의 정답과 사용자가 선택한 정답을 비교하여 정답으로 인정될 수 있는지 검토합니다. 
    문제의 정답과 사용자가 입력한 답이 정답의 범주 내에 있다면 정답으로 간주하도록 합니다. 이 과정은 매우 엄격하게 이뤄져야 하며, 주어진 문제 맥락 및 정보를 파악하여 정답이 맞는지 검증합니다. 
    그리고 검증한 내용을 사용자에게 제시하며 문제의 의도, 문제 해설을 참고하여 사용자에게 다음에도 비슷한 문제를 맞출 수 있도록 조언해주는 내용을 피드백에 추가합니다.
    iscorrect는 정답 여부로, 사용자가 입력한 답과 문제의 답을 비교하였을 때 정답으로 인정된다면 1, 아니라면 0으로 설정합니다.
    """
    
    input_data = """"""
    
    output_template = """
    다음은 반환 JSON 포맷의 예시입니다. 제시하는 JSON 포맷에 맞게 출력해야 합니다.

    JSON FORMAT:
    {
        "output": [
            {
                "index": 1,                        // integer
                "feedback": ""                     // string
                "iscorrect": 0                     // integer
            },
            {
                "index": 3,                        // integer
                "feedback": "",                    // string
                "iscorrect": 1                     // integer
            }
        ]
    }
    """
    
    def __init__(self):
        pass
    
    def set_input_data(self, problems):
        # Json을 파싱한 사전 자료형(problems)을 텍스트로 변환
        self.input_data = json.dumps(problems, indent=4)