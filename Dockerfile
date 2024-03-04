# 기본 이미지로 python 공식 이미지 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 및 한글 폰트 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    poppler-utils \
    fonts-nanum \
    && rm -rf /var/lib/apt/lists/*


# 현재 디렉토리의 내용을 컨테이너의 작업 디렉토리로 복사
COPY . /app

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 컨테이너 실행 시 실행될 명령어
CMD ["flask", "run", "--host=0.0.0.0"]