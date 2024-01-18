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
        ocr.py : Easy OCR 기능을 구현
        pdf_processing : Convert API 기능을 구현

     model.py : DataBase 기능을 구현

/flask-server/static : 정적 파일들을 저장할 폴더

/flask-server/templates : HTML 템플릿 파일을 저장할 폴더
```

---