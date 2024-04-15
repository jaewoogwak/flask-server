# Flask-server
한국기술교육대학교 컴퓨터공학부 졸업설계 Back-end 서버


---

## 파일 구조
```
/flask-server
    /apps
        /chatbot
            __init__.py
            routes.py
        /function
            langchain.py
            ocr.py
            pdf_processing.py
        /main
            __init__.py
            routes.py
        models.py
    /static
        /images
        /pdfs
    /templates
        index.html
    config.py
    main.py
```


## 설명
기능별로 구분하여 구조화한 Blueprint 구조를 차용하여 파일을 구성(차후 수정 가능성 있음)
파일 및 폴더별 기능을 설명하고자 함
```
/flask-server : flask 서버 폴더
    main.py : flask 서버 실행 코드, 기본 코드
    config.py : flask 서버 설정 코드

/flask-server/apps : 서버의 기능을 정의한 폴더
    /chatbot : 챗봇 기능을 위한 라우팅 구현
    /feedback : 문제 피드백 기능을 위한 라우팅 구현
    /function : 서버의 주요 단위 로직을 구현
        langchain.py : GPT API 사용 및 랭체인의 기능을 구현
        ocr.py : Google Vision OCR 기능을 구현
        pdf_processing.py : PDF 파일 생성 기능을 구현
        prompt.py : GPT API 사용 시 정의하는 프롬프트를 구현
    /main : 학습자료 기반 문제 생성을 위한 라우팅 구현
        generate_problem.py : 문제 생성시 필요한 로직을 통합한 함수 구현

     model.py : DataBase 기능을 구현(현재 미구현)

/flask-server/static : 정적 파일들을 저장할 폴더

/flask-server/templates : HTML 템플릿 파일을 저장할 폴더
```


## Package List
0. 설명하기 앞서 한 번에 Package를 다운 받으려면 다음 명령어를 실행한다.
```
pip install -r requirements.txt
```
패키지 설치에 추가적인 설정 방법은 다음 패키지 설명을 참고


1. flask : Python기반 Web Server Framework
```
pip install flask
```


2. Flask-CORS : Flask App에서 Cross-Origin Resource Sharing (CORS)을 처리하기 위한 라이브러리
```
pip install flask-cors
```


3. Pillow : Python에서 이미지 처리를 위한 라이브러리
```
pip install Pillow
```


4. pdfkit : HTML을 PDF로 변환하기 위한 라이브러리
```
pip install pdfkit
```
pdfkit을 사용하기 위해 wkhtmltopdf를 설치해야 함.
- window : <https://wkhtmltopdf.org/downloads.html>에서 설치파일 다운로드 및 실행, notion의 pdfkit 페이지를 참고.
- macOS : homebrew로 설치, 'brew install wkhtmltopdf'
- linux : <https://velog.io/@agust15/파이썬-wkhtmltopdf-설치하기centOS> 참고


5. google-cloud-vision : Google Cloud Vision API 클라이언트 라이브러리로, 이미지 분석을 위한 라이브러리
```
pip install google-cloud-vision
```
- 키파일 필요(깃에는 커밋하지 않았음)


6. pdf2image : PDF를 이미지로 변환하기 위한 라이브러리
```
pip install pdf2image
```
poppler기반 라이브러리이므로 설치 필요 <https://wooiljeong.github.io/python/pdf-to-image/> 참조

7. openai : OpenAI의 API를 사용하기 위한 클라이언트 라이브러리
```
pip install openai
```

8. unstructured : 텍스트, 이미지, PDF 파일 등 다양한 형태의 비정형 데이터를 분석하고 처리하는 라이브러리
```
pip install unstructured
```

9. langchain : llm 모델을 사용하기 용이하게 해주는 라이브러리
```
pip install langchain
```
---
