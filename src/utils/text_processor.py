from PIL import Image, ImageEnhance
import numpy as np
import cv2
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import os

class TextProcessor:
    """텍스트 처리기 클래스
    
    이 클래스는 이미지에서 텍스트를 추출하는 기능을 제공합니다.
    Microsoft의 TrOCR 모델을 사용하여 이미지에서 텍스트를 인식합니다.
    
    Attributes:
        processor (TrOCRProcessor): TrOCR 전처리기
        model (VisionEncoderDecoderModel): TrOCR 모델
        device (torch.device): 연산 장치 (CPU/GPU)
    """
    
    def __init__(self):
        """텍스트 처리기 초기화"""
        print("텍스트 처리기 초기화 시작...")
    
        # GPU 사용 가능 여부 확인
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"사용 장치: {self.device}")
        
        # 1. 환경 변수 설정
        os.environ['TRANSFORMERS_CACHE'] = os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        
        try:
            # 2. ASCII 문자만 포함된 토큰 확인
            with open("util/access_token/token", "r", encoding='utf-8') as f:
                auth_token = f.read().strip()
                # ASCII 문자만 허용
                auth_token = ''.join(c for c in auth_token if ord(c) < 128)
        except FileNotFoundError:
            print("토큰 파일을 찾을 수 없습니다.")
            auth_token = None
            
        try:
            # 3. 모델 로드 시도
            self.processor = TrOCRProcessor.from_pretrained(
                "microsoft/trocr-base-handwritten",
                use_auth_token=auth_token,  # token 대신 use_auth_token 사용
                trust_remote_code=True
            )
        except Exception as e:
            print(f"모델 로드 실패: {str(e)}")
            # 4. 오프라인 모드로 재시도
            try:
                self.processor = TrOCRProcessor.from_pretrained(
                    "microsoft/trocr-base-handwritten",
                    local_files_only=True
                )
            except Exception as offline_e:
                print(f"오프라인 로드도 실패: {str(offline_e)}")
                raise
        
        # 모델과 프로세서 로드
        model_name = "microsoft/trocr-base-handwritten"
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name, use_auth_token=auth_token)
        
        # 모델을 해당 장치로 이동
        self.model.to(self.device)
        print("텍스트 처리기 초기화 완료")

    def preprocess_image(self, image):
        """이미지 전처리
        
        Args:
            image (PIL.Image): 처리할 이미지
            
        Returns:
            PIL.Image: 전처리된 이미지
        """
        print("이미지 전처리 시작...")
        
        # PIL Image를 numpy 배열로 변환
        img_array = np.array(image)
        print(f"원본 이미지 배열 형태: {img_array.shape}")
        
        # RGBA to RGB 변환 (알파 채널 제거)
        if len(img_array.shape) == 3 and img_array.shape[-1] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            print("RGBA에서 RGB로 변환 완료")
        
        # 이미지 크기 조정 (텍스트가 더 선명해지도록)
        scale_factor = 2
        height, width = img_array.shape[:2]
        width = int(width * scale_factor)
        height = int(height * scale_factor)
        img_array = cv2.resize(img_array, (width, height), interpolation=cv2.INTER_CUBIC)
        print(f"이미지 크기 조정 완료: {width}x{height}")
        
        # 노이즈 제거
        if len(img_array.shape) == 3:
            img_array = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
        else:
            img_array = cv2.fastNlMeansDenoising(img_array)
        print("노이즈 제거 완료")
        
        # 그레이스케일 변환
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        print("그레이스케일 변환 완료")
        
        # 적응형 이진화
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        print("적응형 이진화 완료")
        
        # 모폴로지 연산으로 텍스트 선명도 향상
        kernel = np.ones((2,2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        print("모폴로지 연산 완료")
        
        # 이진화된 이미지를 3채널 RGB로 변환
        rgb_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
        print("RGB 변환 완료")
        
        # numpy 배열을 PIL Image로 변환
        enhanced_image = Image.fromarray(rgb_image)
        print(f"전처리된 이미지 크기: {enhanced_image.size}")
        print(f"전처리된 이미지 모드: {enhanced_image.mode}")
        
        return enhanced_image

    def recognize_text(self, preprocessed_image):
        """이미지에서 텍스트 인식
        
        Args:
            preprocessed_image (PIL.Image): 전처리된 이미지
            
        Returns:
            str: 인식된 텍스트
        """
        try:
            print("텍스트 인식 처리 시작...")
            
            # 이미지를 모델 입력 형식으로 변환
            pixel_values = self.processor(preprocessed_image, return_tensors="pt").pixel_values
            print(f"입력 텐서 형태: {pixel_values.shape}")
            
            pixel_values = pixel_values.to(self.device)
            print("텐서를 GPU로 이동 완료")
            
            with torch.no_grad():
                # 텍스트 생성
                generated_ids = self.model.generate(pixel_values)
                print("텍스트 생성 완료")
                
                # 토큰을 텍스트로 변환
                generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                print("토큰 디코딩 완료")
                
                return generated_text
            
        except Exception as e:
            print(f"텍스트 인식 중 오류 발생: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            return None

    def process_image(self, image):
        """이미지를 텍스트로 변환
        
        Args:
            image (PIL.Image): 처리할 이미지
            
        Returns:
            str: 변환된 텍스트 또는 오류 메시지
        """
        if image is None:
            print("이미지가 선택되지 않았습니다.")
            return None
            
        try:
            print("이미지 텍스트 변환 시작...")
            print(f"이미지 크기: {image.size}")
            print(f"이미지 모드: {image.mode}")
            
            # 이미지 전처리
            preprocessed_image = self.preprocess_image(image)
            
            # 텍스트 인식
            print("텍스트 인식 시작...")
            text = self.recognize_text(preprocessed_image)
            
            if not text:
                print("인식된 텍스트가 없습니다.")
                return "텍스트를 찾을 수 없습니다."
            
            print(f"\n인식된 텍스트: {text}")
            return text.strip()
                
        except Exception as e:
            print(f"이미지 텍스트 변환 중 오류 발생: {str(e)}")
            return f"오류: OCR 처리 실패 - {str(e)}"

# 싱글톤 인스턴스 생성
text_processor = TextProcessor() 