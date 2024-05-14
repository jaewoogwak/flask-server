import base64
import io
import pdf2image
import concurrent.futures
from openai import OpenAI
from .langchain import request_prompt_img_detecting

client = OpenAI()

def convert_pdf_to_images(pdf_content):
    """
    PDF 파일의 내용을 이미지로 변환합니다.
    :param pdf_content: PDF 파일의 내용 (bytes)
    :return: 이미지 데이터 목록
    """
    images = pdf2image.convert_from_bytes(pdf_content)
    return images

def encode_image(image):
    """ 이미지를 base64 문자열로 인코딩합니다. """
    return base64.b64encode(image).decode('utf-8')

def send_image_to_openai(image, is_PDF=False, user_option=None):
    """ OpenAI API를 사용하여 이미지에 대한 설명을 요청하고, 결과의 'content'만 반환합니다. """
    if is_PDF:
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        image_content = image_content.getvalue()
    else:
        image_content = image
    base64_image = encode_image(image_content)
    # OpenAI API 호출
    response_json = request_prompt_img_detecting(base64_image, user_option)
    # print(response_json)
    return response_json['image_detections']

def image_to_openai_response(image_content):
    # 하나의 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    result = send_image_to_openai(image_content)
    
    # 결과 출력
    # print(result)
    
    return result

def images_to_openai_responses(images_content):
    # 각 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(send_image_to_openai, images_content))

    # 결과 출력
    # for result in results:
    #     print(result)   
    
    return " ".join(map(str, results))

def PDF_to_openai_responses(pdf_content, user_option=None):
    # PDF를 이미지로 변환
    images = convert_pdf_to_images(pdf_content)

    # 각 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda image: send_image_to_openai(image, is_PDF=True, user_option=user_option), images))

    # 결과 출력
    #for result in results:
    #    print(result)   
    
    return " ".join(map(str, results))