import base64
import io
import pdf2image
import concurrent.futures
from openai import OpenAI

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
    # 메시지 구성
    message = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "이 이미지에 어떤 내용들이 들어 있는지 한국말로 설명해줘. 이미지에 표나 그래프, 다이어그램이 있다면 절대로 표나 그래프, 다이어그램에 있는 수치나 단어를 언급해서는 안돼. 반드시 수치나 단어가 들어가지 않은, 어떤 개념을 다루는 표와 그래프인지만을 설명해야 해. 응답은 JSON 형식으로 반환해줘."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]
    # OpenAI API 호출
    response_json = client.chat.completions.create(
        model="gpt-4-turbo",  
        response_format={"type": "json_object"},
        messages=message,
        max_tokens=1200
    )
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
    for result in results:
        print(result)   
    
    return " ".join(results)