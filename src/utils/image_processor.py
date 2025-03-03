from PIL import Image
import numpy as np
from PyQt5.QtGui import QImage
from .text_processor import text_processor

def process_image_region(qimage: QImage) -> str:
    """선택된 이미지 영역을 처리하여 텍스트로 변환
    
    Args:
        qimage (QImage): 처리할 이미지 영역
        
    Returns:
        str: 변환된 텍스트
    """
    try:
        # QImage를 PIL Image로 변환
        width = qimage.width()
        height = qimage.height()
        
        # QImage를 바이트 배열로 변환
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)  # 32비트 이미지 (RGBA)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # RGBA to RGB
        rgb_arr = arr[..., :3]  # alpha 채널 제거
        rgb_image = Image.fromarray(rgb_arr)
        
        # 텍스트 처리기를 사용하여 이미지 처리
        markup_text = text_processor.process_image(rgb_image)
        if not markup_text:
            return "텍스트를 찾을 수 없습니다."
        return markup_text
        
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return f"오류 발생: {str(e)}"

def save_image(image: QImage, path: str) -> bool:
    """이미지를 파일로 저장
    
    Args:
        image (QImage): 저장할 이미지
        path (str): 저장 경로
        
    Returns:
        bool: 저장 성공 여부
    """
    try:
        return image.save(path)
    except Exception as e:
        print(f"이미지 저장 실패: {e}")
        return False 