import base64
import requests
from config import KEY
import os
import pdf2image
import concurrent.futures

def save_pdf_as_images(pdf_content, output_folder="images_test"):
    """
    PDF 파일의 내용을 이미지로 변환하고 각 페이지를 개별 이미지 파일로 저장합니다.
    :param pdf_content: 텍스트를 추출할 PDF 파일의 내용 (bytes)
    :param output_folder: 이미지를 저장할 폴더 경로
    :return: 저장된 이미지 파일들의 경로 목록
    """
    # 출력 폴더가 존재하지 않으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # PDF를 이미지로 변환
    images = pdf2image.convert_from_bytes(pdf_content)

    # 각 페이지를 이미지 파일로 저장
    image_paths = []
    for idx, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{idx + 1}.jpeg")
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)

    return image_paths

def encode_image(image_path):
    """ 이미지 파일을 base64 문자열로 인코딩합니다. """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def send_image_to_openai(image_path):
    """ OpenAI API를 사용하여 이미지에 대한 설명을 요청하고, 결과의 'content'만 반환합니다. """
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}"
    }
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 이미지에 어떤 내용들이 들어 있는지 한국말로 설명해줘. 이미지에 표나 그래프, 다이어그램이 있다면 절대로 표나 그래프, 다이어그램에 있는 수치나 단어를 언급해서는 안돼. 반드시 수치나 단어가 들어가지 않은, 어떤 개념을 다루는 표와 그래프인지만을 설명해야 해."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 1200
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()
    print(response_data)
    # API 응답에서 각 'content'를 문자열로 추출하고, 모두 결합
    contents = ' '.join([choice['message']['content'] for choice in response_data['choices']])
    return contents

def process_pdf_to_openai_responses(pdf_content, output_folder="images_test"):
    # 테스트 시 이 함수를 호출하면 됩니다.
    # PDF를 이미지로 변환하고 이미지 파일 경로를 가져옵니다.
    image_paths = save_pdf_as_images(pdf_content, output_folder)

    # 각 이미지 파일에 대해 OpenAI 요청을 수행하고 결과를 저장합니다.
    def get_openai_response(image_path):
        return send_image_to_openai(image_path)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(get_openai_response, image_paths))

    # 결과 출력
    for result in results:
        print(result)   
    
    return " ".join(results)