import re

## 응답 텍스트
response_text = """
문제명: 사용자 인터페이스 설계에서 가치를 두어야 하는 원칙은 무엇인가요?
   입력:
   A) 비용 절감
   B) 직관성
   C) 복잡성 
   D) 제작 용이성
   해설: 사용자 인터페이스 설계에서는 사용자가 누구나 쉽게 이해하고 사용할 수 있도록 하기 위해 직관성에 가치를 두어야 합니다.

문제명: 사용자 인터페이스(UI) 개발에서 필요한 기능은 무엇인가요?
   입력:
   A) 사용자 입력 검증
   B) 매출 분석
   C) 서버 최적화
   D) 병렬 처리
   해설: UI 개발에서는 사용자로부터 받은 입력값이 유효한지 검증하는 기능이 필수적입니다. 이를 통하여 사용자가 올바른 정보를 입력하도록 유도하고 에러를 최소화할 수 있습니다.

문제명: UI 설계 도구 중 페이지의 개략적인 레이아웃을 나타내는 단계에서 사용하는 것은?
   입력: ____________________
   해설: 와이어프레임(Wireframe)은 UI 설계의 초기 단계에서 페이지 레이아웃이나 UI 요소 등의 기본 구조를 설계하기 위해 사용되는 도구입니다.
"""

# 정규 표현식을 사용하여 문제, 선택지, 해설을 파싱합니다.
# questions = re.findall(r'문제명: (.+?)\n', response_text)
# choices_matches = re.findall(r'입력:\n((?:\s+[A-D]\) .+\n)+)', response_text)
# choices = []
# for match in choices_matches:
#     choice_dict = {line.split(')')[0].strip(): line.split(')')[1].strip() for line in match.strip().split('\n')}
#     choices.append(choice_dict)
# answers = re.findall(r'해설: (.+?)(?:\n\n|\Z)', response_text, re.DOTALL)

# 문제, 선택지, 해설을 파싱합니다.
# questions = re.findall(r'문제명: (.+?)\n', response_text)
# # 모든 문제에 대해 choices 배열을 초기화합니다.
# choices = [""] * len(questions)  # 모든 문제에 대응하는 빈 선택지를 초기 설정

# # 객관식 문제의 선택지를 파싱합니다.
# choices_matches = re.findall(r'입력:\n((?:\s+[A-D]\) .+\n)+)', response_text)
# for idx, match in enumerate(choices_matches):
#     # 각 선택지를 <br>로 구분하여 하나의 문자열로 합칩니다.
#     choices[idx] = match.strip().replace('\n', '<br>')

# answers = re.findall(r'해설: (.+?)(?:\n\n|\Z)', response_text, re.DOTALL)

# # 서술형 또는 단답형 문제에 대한 처리가 필요한 경우
# # 예시: 모든 빈 선택지에 "서술형 문제입니다." 메시지를 추가
# for idx in range(len(choices)):
#     if choices[idx] == "":
#         choices[idx] = "<br>____________________"

# print(questions)
# print(choices)
# print(answers)

# generate_pdf(questions, choices)
# generate_pdf_with_answers(questions, choices, answers)