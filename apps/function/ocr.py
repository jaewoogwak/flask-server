import concurrent.futures
import pdf2image
import io
from google.cloud import vision
from PIL import Image

# TODO: OCR_image_byte, OCR_images_byte 함수 통합, 한개든 여러개든 여러개의 조건에 포함됨

def OCR_image_byte(image_content):
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

def OCR_images_byte(images_content: bytes) -> str:
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

def OCR_PDF(pdf_content: bytes) -> str:
    """
    PDF 파일의 내용에서 텍스트를 추출합니다. PDF의 내용을 이미지로 변환한 후 이미지에서 텍스트를 추출합니다.
    
    Args:
        pdf_content(bytes): pdf형식 파일 입력
        
    Return:
        string: 학습 자료 내용 string
    """
    # Client 인스턴스를 한 번만 생성
    client = vision.ImageAnnotatorClient()
    
    def ocr_image(image: Image.Image, client: vision.ImageAnnotatorClient) -> str:
        """
        한 페이지의 이미지를 입력받아 텍스트를 추출

        Args:
            image (Image.Image): 단일 이미지
            client (vision.ImageAnnotatorClient): Google Cloud Vision API 클라이언트

        Returns:
            string: 한 페이지의 내용 string
        """
        # 이미지 데이터를 바이트 스트림으로 변환합니다.
        image_content = io.BytesIO()
        
        # 이미지를 JPEG 포맷으로 바이트 스트림에 저장합니다.
        image.save(image_content, format='JPEG')
        
        # 바이트 스트림의 현재 위치를 파일의 시작 부분으로 재설정하고 바이트 데이터를 가져옵니다.
        image_content = image_content.getvalue()

        # Vision API의 이미지 객체를 생성합니다.
        vision_image = vision.Image(content=image_content)
        
        # Vision API 클라이언트를 사용하여 텍스트 감지 요청을 보냅니다.
        response = client.text_detection(image=vision_image)
        
        # 텍스트 감지 결과를 가져옵니다.
        texts = response.text_annotations
        
        # 텍스트 감지 결과가 있으면 첫 번째 텍스트 내용을 반환하고, 없으면 "No text found"를 반환합니다.
        return texts[0].description if texts else "No text found"

    images = pdf2image.convert_from_bytes(pdf_content)
    
    # ThreadPoolExecutor를 사용하여 이미지 별로 ocr_image 함수를 병렬 실행
    # client 인스턴스를 ocr_image 함수의 인자로 전달
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # executor.map 호출 시 함수에 전달할 여러 인자를 처리하기 위해 zip을 사용
        results = list(executor.map(lambda img: ocr_image(img, client), images))

    return " ".join(results)