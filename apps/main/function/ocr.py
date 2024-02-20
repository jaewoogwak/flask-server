import concurrent.futures
import easyocr
import pdf2image
from PIL import Image
import io
import numpy as np

from google.cloud import vision

import os

# 현재 스크립트의 디렉토리 경로를 가져옵니다.
current_directory = os.path.dirname(__file__)

# 프로젝트 루트 디렉토리로 이동하기 위한 상대 경로를 설정합니다.
root_directory = os.path.join(current_directory, '../../../')

# JSON 파일의 상대 경로를 설정합니다.
json_path = os.path.join(root_directory, 'serious-conduit-413006-58f255767a58.json')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path

def OCRImage_Byte(image_content):
    """
    이미지 파일의 내용에서 텍스트를 추출합니다.
    :param image_content: 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description
    else:
        return "No text found"

def OCRImages_Byte(images_content):
    """
    여러 이미지 파일의 내용에서 텍스트를 추출합니다.
    :param images_content: 텍스트를 추출할 이미지 파일들의 내용 (bytes)
    :return: 각 이미지에서 추출된 텍스트의 리스트
    """
    def ocr_image(image_content):
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        return texts[0].description if texts else "No text found"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, images_content))

    return results

def OCRPDF(pdf_content):
    """
    PDF 파일의 내용에서 텍스트를 추출합니다.
    PDF의 내용을 이미지로 변환한 후 이미지에서 텍스트를 추출합니다.
    :param pdf_content: 텍스트를 추출할 PDF 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    def ocr_image(image):
        client = vision.ImageAnnotatorClient()
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        image_content = image_content.getvalue()

        vision_image = vision.Image(content=image_content)
        response = client.text_detection(image=vision_image)
        texts = response.text_annotations
        return texts[0].description if texts else "No text found"

    images = pdf2image.convert_from_bytes(pdf_content)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, images))

    return " ".join(results)
