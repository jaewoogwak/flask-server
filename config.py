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
