import os
import platform
# OMP: Error #15: Initializing libiomp5md.dll 문제 해결을 위한 환경 변수 설정
# 코드의 맨 위에 있어야함
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# OCR 설정
# 프로젝트 루트 디렉토리의 절대 경로 설정
current_directory = os.path.dirname(os.path.abspath(__file__))
# Google Cloud Vision API 설정
google_vision_setting = {
    "credentials_path": os.path.join(current_directory, 'serious-conduit-413006-58f255767a58.json')
}
# 환경 변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_vision_setting["credentials_path"]


# 운영체제별 PDF 생성 설정
wk_setting = {
    'Windows': {
        'OS': 'Windows',
        'PATH': 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
    },
    'Darwin': {  # macOS
        'OS': 'Darwin',
        'PATH': None  # macOS에서는 경로 설정이 필요 없을 수 있음
    },
    'Linux': {
        'OS': 'Linux',
        'PATH': None  # 기본값, Linux 등 다른 운영체제
    }
}[platform.system()]


# GPT API KEY 설정, 환경 변수 설정으로 KEY를 하드코딩 X
# linux의 경우
# terminal에서 'nano ~/.bashrc' 입력 후 'export OPENAI_API_KEY="GPT_API_KEY"'으로 환경변수 설정
# 이후 terminal에서 'source ~/.bashrc'로 설정 로드

# MacOS의 경우
# terminal에서 'nano ~/.zshrc' 입력 후 'export OPENAI_API_KEY="GPT_API_KEY"'으로 환경변수 설정
# 이후 terminal에서 'source ~/.zshrc'로 설정 로드

# windows의 경우
# window 검색 창에 '환경 변수 편집'입력 후 선택 -> 시스템 변수 섹션에서 '새로만들기' 선택
# -> 변수 이름으로 'OPENAI_API_KEY' 입력 후 변수 값으로 키 값(위에서 설명한 GPT_API_KEY) 입력
# -> 내용 적용 후 컴퓨터 재부팅

KEY = os.getenv("OPENAI_API_KEY")

# groq API key 설정, chatbot기능 제외 문제 생성 로직에만 사용됨
Groq_api_key=os.getenv("GROQ_API_KEY")
