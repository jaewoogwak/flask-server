import base64
import io
import pdf2image
import concurrent.futures
from openai import OpenAI
from .langchain import request_prompt_img_detecting

client = OpenAI()

def convert_pdf_to_images(pdf_content):
    """
    PDF 파일의 내용을 이미지로 변환하는 함수
    
    Args:
        pdf_content (bytes): 학습자가 업로드한 강의자료
    Returns:
        list: 변환된 이미지 데이터 목록
    Exceptions:
        pdf2image.exceptions.PDFPageCountError: PDF 페이지 수를 계산하는 데 실패했을 때 발생
        pdf2image.exceptions.PDFSyntaxError: PDF 구문 오류로 인해 변환이 실패했을 때 발생
    """
    # PDF를 이미지로 된 list로 변환 후 PDF_to_openai_responses에 return
    images = pdf2image.convert_from_bytes(pdf_content)
    return images

def encode_image(image):
    """ 
    이미지를 base64 문자열로 인코딩하는 함수

    Args:
        image (bytes): 학습자가 업로드한 강의자료 중 한 페이지
    Returns:
        str: Base64로 인코딩된 문자열
    Exceptions:
        TypeError: 이미지 데이터가 잘못된 형식일 때 발생
    """
    # 이미지를 base64 문자열로 인코딩 후 send_image_to_openai에 return
    return base64.b64encode(image).decode('utf-8')

def send_image_to_openai(image, is_PDF=False, user_option=None):
    """ 
    OpenAI API를 사용하여 이미지에 대한 분석을 요청하고, 결과를 반환하는 함수

    Args:
        image (bytes): 학습자가 업로드한 강의자료 중 한 페이지
        is_PDF (bool): PDF에서 변환된 이미지인지 여부
        user_option (str): 사용자의 요청사항이 들어간 커스텀 프롬프트
    Returns:
        str: OpenAI API에서 반환된 이미지 분석 결과
    Exceptions:
        OpenAIError: OpenAI API 요청 실패 시 발생
        IOError: 이미지 데이터를 처리하는 동안 입출력 오류가 발생할 때
    """
    # PDF에서 변환된 이미지인지 아닌지에 따라 다르게 처리
    if is_PDF:
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        image_content = image_content.getvalue()
    else:
        image_content = image

    # base64 문자열로 인코딩 수행
    base64_image = encode_image(image_content)

    # OpenAI API 호출 이후 결과를 json으로 반환받음
    response_json = request_prompt_img_detecting(base64_image, user_option)
    return response_json['image_detections']

def image_to_openai_response(image_content):
    """ 
    하나의 이미지가 업로드된 경우 이미지 분석 함수를 호출하고 결과를 반환하는 함수

    Args:
        image_content (bytes): 사용자가 업로드한 강의자료
    Returns:
        str: OpenAI API에서 반환된 이미지 분석 결과
    Exceptions:
        OpenAIError: OpenAI API 요청 실패 시 발생
    """
    # 이미지 분석 함수 호출 후 결과를 반환받음
    result = send_image_to_openai(image_content)    
    return result

def images_to_openai_responses(images_content):
    """ 
    여러 이미지가 업로드된 경우 이미지 분석 함수를 호출하고 결과를 반환하는 함수

    Args:
        images_content (list of bytes): 사용자가 업로드한 강의자료
    Returns:
        str: 모든 이미지에 대한 분석 결과가 결합된 문자열
    Exceptions:
        OpenAIError: OpenAI API 요청 실패 시 발생
        IOError: 이미지 데이터를 처리하는 동안 입출력 오류가 발생할 때
    """
    # 속도 증가를 위한 병렬 처리, 이미지 분석 함수 호출 후 결과를 입력받음
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(send_image_to_openai, images_content))
    # list의 내용을 하나의 문자열로 결합해 반환
    return " ".join(map(str, results))

def PDF_to_openai_responses(pdf_content, user_option=None):
    """ 
    PDF 파일을 이미지로 변환하고, 이미지 분석 함수를 호출하고 결과를 반환하는 함수

    Args:
        pdf_content (bytes): 사용자가 업로드한 강의자료
        user_option (str): 사용자의 요청사항이 들어간 커스텀 프롬프트
    Returns:
        str: PDF의 각 페이지에 대한 OpenAI API 응답이 결합된 문자열
    Exceptions:
        OpenAIError: OpenAI API 요청 실패 시 발생.
        IOError: 이미지 데이터를 처리하는 동안 입출력 오류가 발생할 때.
    """
    # PDF를 이미지 리스트로 변환
    images = convert_pdf_to_images(pdf_content)

    # 속도 증가를 위한 병렬 처리, 이미지 분석 함수 호출 후 결과를 입력받음
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda image: send_image_to_openai(image, is_PDF=True, user_option=user_option), images)) 
    # list의 내용을 하나의 문자열로 결합해 반환
    return " ".join(map(str, results))