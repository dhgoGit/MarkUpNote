import pytest
import os
from PyQt5.QtGui import QImage
from src.utils.image_processor import process_image_region, save_image

@pytest.fixture
def test_image():
    """테스트용 이미지 픽스처"""
    image = QImage(100, 100, QImage.Format.Format_RGB32)
    image.fill(0)  # 검은색으로 채우기
    return image

def test_process_image_region(test_image):
    """이미지 영역 처리 테스트"""
    result = process_image_region(test_image)
    assert isinstance(result, str)
    assert len(result) > 0

def test_save_image(test_image, tmp_path):
    """이미지 저장 테스트"""
    # 임시 디렉토리에 저장
    save_path = os.path.join(tmp_path, "test.png")
    success = save_image(test_image, save_path)
    
    assert success
    assert os.path.exists(save_path)
    assert os.path.getsize(save_path) > 0 