import concurrent.futures
import pdf2image
import io
from google.cloud import vision


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
    # Client 인스턴스를 한 번만 생성
    client = vision.ImageAnnotatorClient()

    def ocr_image(image_content, client):
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        return texts[0].description if texts else "No text found"
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(ocr_image, images_content, [client] * len(images_content)))

    return " ".join(results)


def OCRPDF(pdf_content):
    """
    PDF 파일의 내용에서 텍스트를 추출합니다.
    PDF의 내용을 이미지로 변환한 후 이미지에서 텍스트를 추출합니다.
    :param pdf_content: 텍스트를 추출할 PDF 파일의 내용 (bytes)
    :return: 추출된 텍스트
    """
    # Client 인스턴스를 한 번만 생성
    client = vision.ImageAnnotatorClient()
    
    def ocr_image(image, client):
        image_content = io.BytesIO()
        image.save(image_content, format='JPEG')
        image_content = image_content.getvalue()

        vision_image = vision.Image(content=image_content)
        response = client.text_detection(image=vision_image)
        texts = response.text_annotations
        return texts[0].description if texts else "No text found"

    images = pdf2image.convert_from_bytes(pdf_content)
    
    # ThreadPoolExecutor를 사용하여 이미지 별로 ocr_image 함수를 병렬 실행
    # client 인스턴스를 ocr_image 함수의 인자로 전달
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # executor.map 호출 시 함수에 전달할 여러 인자를 처리하기 위해 zip을 사용
        results = list(executor.map(lambda img: ocr_image(img, client), images))

    return " ".join(results)