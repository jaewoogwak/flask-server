import base64
import io
import pdf2image
import concurrent.futures
from openai import OpenAI
from .prompt import img_detecting_prompt
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

def send_image_to_openai(image, is_PDF=False):
    """ OpenAI API를 사용하여 이미지에 대한 설명을 요청하고, 결과의 'content'만 반환합니다. """
    if is_PDF:
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        image_content = image_content.getvalue()
    else:
        image_content = image
    base64_image = encode_image(image_content)
    prompt = img_detecting_prompt(base64_image)
    # 문제 생성을 위한 프롬프트 설정
    message = [
        {"role": "system", "content": prompt.get_system_prompt()},
        {
            "role": "user", 
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{prompt.get_user_input()}"}}
            ]
        }
    ]
    # OpenAI API 호출
    response_json = request_prompt_img_detecting(message)
    print(response_json)
    return response_json.choices[0].message.content

def image_to_openai_response(image_content):
    # 하나의 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    result = send_image_to_openai(image_content)
    
    # 결과 출력
    print(result)
    
    return result

def images_to_openai_responses(images_content):
    # 각 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(send_image_to_openai, images_content))

    # 결과 출력
    for result in results:
        print(result)   
    
    return " ".join(results)

def PDF_to_openai_responses(pdf_content):
    # PDF를 이미지로 변환
    images = convert_pdf_to_images(pdf_content)

    # 각 이미지에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda image: send_image_to_openai(image, is_PDF=True), images))

    # 결과 출력
    #for result in results:
    #    print(result)   
    
    return " ".join(results)