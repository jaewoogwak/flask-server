# Flask-server
한국기술교육대학교 컴퓨터공학부 졸업설계 Back-end 서버


---
## 파일 구조
```
/flask-server
    /apps
        /main
            /function
                langchain.py
                ocr.py
                pdf_processing.py
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
    /main : 메인화면을 구현
        /function : 서버의 주요 로직을 구현
        langchain.py : 랭체인의 기능을 구현
        ocr.py : Google Vision OCR 기능을 구현
        pdf_processing : Convert API 기능을 구현

     model.py : DataBase 기능을 구현(현재 미구현)

/flask-server/static : 정적 파일들을 저장할 폴더

/flask-server/templates : HTML 템플릿 파일을 저장할 폴더
```


## Package List
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


5. NumPy : 다차원 배열 객체와 배열 작업을 위한 다양한 도구를 제공
```
pip install numpy
```


6. google-cloud-vision : Google Cloud Vision API 클라이언트 라이브러리로, 이미지 분석을 위한 라이브러리
```
pip install google-cloud-vision
```
- 키파일 필요(깃에는 커밋하지 않았음)


7. pdf2image : PDF를 이미지로 변환하기 위한 라이브러리
```
pip install pdf2image
```
poppler기반 라이브러리이므로 설치 필요 <https://wooiljeong.github.io/python/pdf-to-image/> 참조

8. openai : OpenAI의 API를 사용하기 위한 클라이언트 라이브러리
```
pip install openai
```
---

## 주의사항
1. mac, window 간 pdf_processing 문제(main\function\pdf_processing.py)
wkhtmltopdf의 사용법이 mac과 windows가 다르기에 commit된 내용을 pull한 이후 확인이 필요

본인의 환경을 제외한 내용을 주석 처리 후 사용하면 됨.
window의 경우 본인의 wkhtmltopdf 경로를 본인의 경로로 수정 필요
```
# wkhtmltopdf 설치 후 경로 입력 필요(windows에서만 생기는 문제, 본인 경로에 맞게 수정, 서버(linux)에 올리는 경우는 테스트 필요)
# Window 환경
config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
pdfkit.from_string(html_content, output_file, configuration=config)
    
# Mac 환경
pdfkit.from_string(html_content, output_file)
```
---
