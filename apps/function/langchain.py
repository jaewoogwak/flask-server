from openai import OpenAI
import re
client = OpenAI()    

prompt_setting = """
생성할 문제의 형식은 다음과 같습니다:
- 각 문제는 '문제명'으로 시작합니다. 문제 번호 라벨링은 하지 말아주세요.
- 객관식 문제의 경우, '입력'이라는 단어 다음에 선택지가 A), B), C), D)로 제시됩니다.
- 단답형 또는 서술형 문제의 경우, '입력: ____________________'이라는 텍스트와 함께 제시됩니다.
- 각 문제에는 해설이 포함됩니다.
- 문제 생성 이외에 텍스트는 작성하지 마세요. 오직 문제 형식대로만 출력되어야 합니다.
- 문제 생성 예시를 제공하니 그 예시의 형식대로 출력해주세요.

이 규칙을 따라서, 사용자가 제시한 내용을 기반으로 하는 문제를 생성해주세요. 문제 문항은 10개, 문제 유형은 랜덤으로 해주세요. 제공할 내용은 OCR을 거쳐 얻은
데이터로 특수문자(개행문자 등)나 관련 없는 내용이 포함되어 있는데 이를 제외한 내용에서 문제를 생성할 수 있도록 해주세요.
"""

output_template = """
문제 생성 예시는 다음과 같습니다.
문제 생성 예시(객관식):
문제명: 2x + 6 = 12의 해는 무엇인가요?
   입력:
   A) 2
   B) 3
   C) 4
   D) 5
   해설: 이 방정식을 풀기 위해서는, 먼저 양변에서 6을 빼고, 그 결과를 2로 나누어 x의 값을 찾습니다.
문제 생성 예시(서술형 및 단답형):
문제명: 2x + 6 = 12의 해는 무엇인가요?
   입력: ____________________
   해설: 이 방정식을 풀기 위해서는, 먼저 양변에서 6을 빼고, 그 결과를 2로 나누어 x의 값을 찾습니다. 따라서 답은 12입니다.
"""

def request_prompt(contents):
    # 문제 생성을 위한 프롬프트 설정
    message = [
        {"role": "system", "content": prompt_setting + output_template},
        {"role": "user", "content": contents}
    ]

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=message
    )
    
    print(completion.choices[0].message)
    response = completion.choices[0].message.content
    
    return response