import unittest
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import re

# 상위 디렉토리를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.text_processor import text_processor

class TestTextRecognition(unittest.TestCase):
    """손글씨 텍스트 인식 테스트 클래스"""
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.test_image_path = os.path.join('tests', 'resources', 'origin', 'test_image.png')
        self.preprocess_image_path = os.path.join('tests', 'resources', 'temp', 'preprocess', 'preprocessing_steps.png')
        self.result_path = os.path.join('tests', 'resources', 'temp', 'recognition-result')
        
        # 결과 디렉토리가 없으면 생성
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)
            
        self.create_test_image()
        
    def create_test_image(self):
        """테스트용 이미지 생성"""
        # 이미지 크기 설정
        width = 400
        height = 200
        
        # 흰색 배경의 이미지 생성
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 텍스트 설정
        text = "Hello World"
        
        try:
            # 시스템 폰트 사용
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            # 폰트를 찾을 수 없는 경우 기본 폰트 사용
            font = ImageFont.load_default()
        
        # 텍스트 위치 계산 (중앙 정렬)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # 텍스트 그리기
        draw.text((x, y), text, font=font, fill='black')
        
        # 노이즈 추가
        img_array = np.array(image)
        noise = np.random.normal(0, 25, img_array.shape)
        noisy_image = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        # 이미지 저장
        self.test_image = Image.fromarray(noisy_image)
        self.test_image.save(self.test_image_path)
        print(f"테스트 이미지가 '{self.test_image_path}'로 저장되었습니다.")

    def visualize_preprocessing_steps(self, image):
        """이미지 전처리 단계별 시각화
        
        Args:
            image (PIL.Image): 원본 이미지
        """
        # PIL Image를 numpy 배열로 변환
        img_array = np.array(image)
        
        # 결과를 저장할 리스트
        titles = ['원본']
        images = [img_array]
        
        # 1. RGBA to RGB 변환 (필요한 경우)
        if len(img_array.shape) == 3 and img_array.shape[-1] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            titles.append('RGB 변환')
            images.append(img_array)
        
        # 2. 이미지 크기 조정
        scale_factor = 2
        height, width = img_array.shape[:2]
        width = int(width * scale_factor)
        height = int(height * scale_factor)
        img_array = cv2.resize(img_array, (width, height), interpolation=cv2.INTER_CUBIC)
        titles.append('크기 조정')
        images.append(img_array)
        
        # 3. 노이즈 제거
        denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
        titles.append('노이즈 제거')
        images.append(denoised)
        
        # 4. 그레이스케일 변환
        gray = cv2.cvtColor(denoised, cv2.COLOR_RGB2GRAY)
        titles.append('그레이스케일')
        images.append(gray)
        
        # 5. 적응형 이진화
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        titles.append('이진화')
        images.append(binary)
        
        # 6. 모폴로지 연산
        kernel = np.ones((2,2), np.uint8)
        morphology = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        titles.append('모폴로지 연산')
        images.append(morphology)
        
        # 결과 시각화
        plt.figure(figsize=(20, 10))
        for idx, (img, title) in enumerate(zip(images, titles)):
            plt.subplot(2, 3, idx + 1)
            if len(img.shape) == 3:
                plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            else:
                plt.imshow(img, cmap='gray')
            plt.title(title)
            plt.axis('off')
        
        # 결과 저장
        plt.tight_layout()
        plt.savefig(self.preprocess_image_path)
        plt.close()
        
        print(f"전처리 단계별 결과가 '{self.preprocess_image_path}'에 저장되었습니다.")
    
    def test_preprocessing_visualization(self):
        """이미지 전처리 시각화 테스트"""
        print("\n=== 이미지 전처리 시각화 테스트 시작 ===")
        
        # 전처리 단계 시각화
        self.visualize_preprocessing_steps(self.test_image)
        
        print("=== 테스트 완료 ===")

    def normalize_text(self, text):
        """텍스트 정규화
        
        대소문자 구분을 없애고, 구두점을 제거하며, 연속된 공백을 하나로 만듭니다.
        
        Args:
            text (str): 정규화할 텍스트
            
        Returns:
            str: 정규화된 텍스트
        """
        # 구두점 제거 및 소문자 변환
        text = re.sub(r'[^\w\s]', '', text.lower())
        # 연속된 공백을 하나로
        text = ' '.join(text.split())
        return text
    
    def calculate_text_similarity(self, text1, text2):
        """텍스트 유사도 계산
        
        Args:
            text1 (str): 첫 번째 텍스트
            text2 (str): 두 번째 텍스트
            
        Returns:
            float: 텍스트 유사도 (0.0 ~ 1.0)
        """
        text1 = self.normalize_text(text1)
        text2 = self.normalize_text(text2)
        
        if text1 == text2:
            return 1.0
        
        # 단어 단위로 비교
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Jaccard 유사도 계산
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    def save_recognition_results(self, results):
        """인식 결과를 CSV 파일로 저장
        
        Args:
            results (list): 테스트 결과 리스트. 각 항목은 (예상 텍스트, 인식된 텍스트, 유사도) 형태
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(self.result_path, f'recognition_results_{timestamp}.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['예상 텍스트', '인식된 텍스트', '정규화된 예상', '정규화된 인식', '유사도'])
            
            total_similarity = 0.0
            for expected, actual, similarity in results:
                writer.writerow([
                    expected, 
                    actual, 
                    self.normalize_text(expected),
                    self.normalize_text(actual),
                    f'{similarity:.2%}'
                ])
                total_similarity += similarity
            
            # 평균 유사도 추가
            avg_similarity = total_similarity / len(results) if results else 0
            writer.writerow(['', '', '', '평균 유사도', f'{avg_similarity:.2%}'])
        
        print(f"\n인식 결과가 '{csv_path}'에 저장되었습니다.")
        return avg_similarity

    def test_text_recognition(self):
        """텍스트 인식 테스트"""
        print("\n=== 텍스트 인식 테스트 시작 ===")
        
        test_cases = [
            ("Hello World", self.test_image),  # 기본 테스트 이미지
        ]
        
        results = []
        for expected_text, test_image in test_cases:
            print(f"\n테스트 케이스: 예상 텍스트 '{expected_text}'")
            
            # 텍스트 인식 수행
            recognized_text = text_processor.process_image(test_image)
            
            # 텍스트 유사도 계산
            similarity = self.calculate_text_similarity(expected_text, recognized_text)
            results.append((expected_text, recognized_text, similarity))
            
            print(f"예상 텍스트: {expected_text}")
            print(f"인식된 텍스트: {recognized_text}")
            print(f"정규화된 예상: {self.normalize_text(expected_text)}")
            print(f"정규화된 인식: {self.normalize_text(recognized_text)}")
            print(f"유사도: {similarity:.2%}")
        
        # 결과를 CSV 파일로 저장
        avg_similarity = self.save_recognition_results(results)
        
        print(f"\n=== 테스트 완료 ===")
        print(f"평균 유사도: {avg_similarity:.2%}")
        
        # 유사도가 80% 이상이면 테스트 통과
        self.assertTrue(avg_similarity >= 0.8, f"텍스트 인식 정확도가 너무 낮습니다: {avg_similarity:.2%}")

if __name__ == '__main__':
    unittest.main() 