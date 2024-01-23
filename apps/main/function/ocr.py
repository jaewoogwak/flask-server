import concurrent.futures
import easyocr
import pdf2image
from PIL import Image
import io
import numpy as np

def OCRImage_Byte(image_content):
    """
    바이트 형태의 이미지 파일의 내용에서 텍스트를 추출합니다.
    :param image_content: 텍스트를 추출할 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    reader = easyocr.Reader(['ko', 'en'])
    image = Image.open(io.BytesIO(image_content))
    result = reader.readtext(np.array(image))
    return " ".join([text[1] for text in result])

def OCRImage_PpmImageFile(image):
    """
    PpmImageFile 형태의 이미지 파일의 내용에서 텍스트를 추출합니다.
    :param image: 텍스트를 추출할 이미지 파일의 내용 (PpmImageFile)
    :return: 추출된 텍스트
    """
    reader = easyocr.Reader(['ko', 'en'])
    # 이미지를 numpy array로 변환
    image_np = np.array(image)
    result = reader.readtext(image_np)
    return " ".join([text[1] for text in result])

def OCRImages_Byte(images_content):
    """
    바이트 형태의 이미지 파일의 내용에서 텍스트를 추출합니다.
    :param images_content: 텍스트를 추출할 이미지 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    def ocr_image(image):
        reader = easyocr.Reader(['ko', 'en'], gpu=False)  # GPU 사용 여부 설정
        result = reader.readtext(np.array(image))
        return " ".join([text[1] for text in result])
    
    texts = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, images_content))
    
    texts.extend(results)
    return texts

def OCRPDF(pdf_content):
    """
    PDF 파일의 내용에서 텍스트를 추출합니다.
    먼저 PDF의 내용을 이미지로 변환한 후 이미지에서 텍스트를 추출합니다.
    :param pdf_content: 텍스트를 추출할 PDF 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    images = pdf2image.convert_from_bytes(pdf_content)

    texts = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 각 이미지에 대해 ocr_image 함수를 병렬로 실행
        results = list(executor.map(ocr_image_PpmImageFile, images))
    
    texts.extend(results)
    return " ".join(texts)
