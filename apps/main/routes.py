from . import main
from flask import request, jsonify, Response, request, stream_with_context
import time
from ..function.ocr import OCR_image_byte, OCR_images_byte, OCR_PDF
from .generate_problem import generate
from ..function.image_test import image_to_openai_response, images_to_openai_responses, PDF_to_openai_responses
import json

# TODO: 단일 이미지(/image)/다중 이미지(/images) 처리 통합, 기능적으로 동일
# /image routing으로 통일, 이후 해당 코드에 대한 주석 추가

# 단일 이미지 처리
@main.route('/image', methods=['POST'])
def upload_image():
    """
    단일 이미지를 처리할 엔드포인트
    """
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # 이미지 파일의 내용을 읽음
    image_content = file.read()
        
    if user_option['isTextCentered'] == 1:
        text = image_to_openai_response(image_content, user_option)
    else:
        text = OCR_image_byte(image_content)
        
        result = generate(text, user_option)
        return jsonify(result), 200

# 이미지 여러 장 처리
@main.route('/images', methods=['POST'])
def upload_images():
    """
    여러 이미지를 처리할 엔드포인트
    """
    if 'files' not in request.files:
        return 'No files part', 400
    
    files = request.files.getlist('files')
    
    if not files or any(file.filename == '' for file in files):
        return 'No selected files', 400
    
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # 파일을 바이트 컨텐츠로 변환
    images = [file.read() for file in files]

    if user_option['isTextCentered'] == 1:
        text = images_to_openai_responses(images, user_option)
    else:
        text = OCR_images_byte(images)
        
    result = generate(text, user_option)
    return jsonify(result), 200

@main.route('/pdf', methods=['POST'])
def upload_PDF():
    """
    POST /upload/pdf
    PDF 학습자료를 기반으로 문제 생성 및 vectordb 생성
    
    Request Body:
        {
            "file": "file object",                  # 업로드된 PDF 파일
            "examSetting":                          # JSON 형식의 시험 설정 옵션, TODO: 안 쓰는 옵션은 수정 필요
            {
                {
                    multipleChoice: int,            # 객관식 수
                    shortAnswer: int,               # 단답형 수 
                    essay: int,                     # 서술형 수
                    examNumber: int,                # 문제 총 수
                    custom_prompt: "stirng",        # 사용자 커스텀 프롬프트
                    custom_image_prompt: "string",  # 이미지 처리에 대한 추가적인 커스텀 프롬프트
                    isTextCentered: int,            # 이미지 기반으로 자료를 인식하면 1, OCR 기반으로 자료를 인식하면 0
                    isLectureOnly: int,             # 문제 생성 시 지식 범위를 자료에 한정하면 1, 외부 추가적인 지식을 사용하면 0
                }
            }   
        }
    
    Returns:
        json: 
        {
            "case": int,                            # 문제 유형, 0이면 객관식, 1이면 주관식
            "question": "string",                   # 문제 명(제목)
            "choices": array of string or "string", # 문제 선지, 객관식의 경우 선택지 string이 배열로 주어지고, 주관식의 경우 "빈칸"으로 반환
            "correct_answer": int or "string",      # 문제의 답, 객관식의 경우 선택지 번호(int), 주관식의 경우 정답 string 반환  
            "explanation": "string",                # 문제의 답에 대한 해설
            "intent": "string"                      # 문제 생성 의도
        }
        
    Exceptions:
        400: 
            - {"error": "No file part"}: 요청에 'file' 부분이 없는 경우.
            - {"error": "No selected file"}: 파일이 선택되지 않은 경우.
            - {"error": "No examSetting found in the form data"}: 폼 데이터에 'examSetting'이 없는 경우.
            - {"error": "Invalid JSON format in examSetting"}: 'examSetting'이 유효한 JSON 형식이 아닌 경우.
    """
    
    # 요청에서 'file'이 포함되어 있는지 확인
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    # file 파싱
    file = request.files['file']
    
    # file 필드는 존재하나 파일을 선택하지 않았는지 확인
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # 'examSetting' 폼 데이터를 가져와 JSON으로 파싱
    try:
        user_option_str = request.form['examSetting']
        user_option = json.loads(user_option_str)
    # 폼 데이터에 'examSetting' 키가 없는 경우
    except KeyError:
        return jsonify({"error": "No examSetting found in the form data"}), 400
    # 'examSetting'이 유효한 JSON 형식이 아닌 경우
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in examSetting"}), 400
    
    # PDF 파일의 내용을 읽음
    pdf_content = file.read()

    # 이미지 기반의 처리로 학습자료를 읽기(1)
    if user_option['isTextCentered'] == 1:
        text = PDF_to_openai_responses(pdf_content, user_option)
    # OCR 기능으로 학습자료를 읽기(0 or any) 
    else:
        text = OCR_PDF(pdf_content)
        
    # 학습자료를 읽은 내용을 기반으로 문제 생성
    result = generate(text, user_option)
    # 문제 생성 내용 반환
    return jsonify(result), 200