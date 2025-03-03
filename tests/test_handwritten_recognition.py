import unittest
import os
from PIL import Image
import datasets
from src.utils.text_processor import text_processor
import pandas as pd
from datetime import datetime
import numpy as np

class TestHandwrittenRecognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화 - 데이터셋 다운로드"""
        print("\n데이터셋 다운로드 시작...")
        cls.dataset = datasets.load_dataset("corto-ai/handwritten-text", split="train[:100]")  # 처음 100개 샘플만 사용
        cls.save_dir = "tests/resources/handle_text_recognition"
        os.makedirs(cls.save_dir, exist_ok=True)
        
        # 결과를 저장할 디렉토리 생성
        cls.results_dir = os.path.join(cls.save_dir, "results")
        os.makedirs(cls.results_dir, exist_ok=True)

    def calculate_similarity(self, text1, text2):
        """두 텍스트 간의 유사도 계산 (대소문자 무시)"""
        if text1 is None or text2 is None:
            return 0.0
            
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if len(text1) == 0 or len(text2) == 0:
            return 0.0
            
        # 레벤슈타인 거리 계산
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
        
        # 유사도를 백분율로 변환 (0~100)
        max_len = max(m, n)
        if max_len == 0:
            return 100.0
        similarity = ((max_len - dp[m][n]) / max_len) * 100
        return round(similarity, 2)

    def test_handwritten_recognition(self):
        """손글씨 인식 테스트"""
        print("\n손글씨 인식 테스트 시작...")
        results = []
        
        for idx, sample in enumerate(self.dataset):
            print(f"\n샘플 {idx+1}/100 처리 중...")
            
            # 이미지 저장 및 처리
            image = sample['image']  # 이미 PIL Image 객체임
            image_path = os.path.join(self.save_dir, f"sample_{idx}.png")
            image.save(image_path)
            
            # 텍스트 인식
            recognized_text = text_processor.process_image(image)
            expected_text = sample['text']
            
            # 유사도 계산
            similarity = self.calculate_similarity(recognized_text, expected_text)
            
            # 결과 저장
            results.append({
                'sample_id': idx,
                'image_path': image_path,
                'expected_text': expected_text,
                'recognized_text': recognized_text,
                'similarity': similarity
            })
            
            print(f"기대 텍스트: {expected_text}")
            print(f"인식된 텍스트: {recognized_text}")
            print(f"유사도: {similarity}%")
        
        # 결과를 DataFrame으로 변환하고 CSV로 저장
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(self.results_dir, f'recognition_results_{timestamp}.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # 전체 통계 계산
        avg_similarity = np.mean([r['similarity'] for r in results])
        print(f"\n테스트 완료!")
        print(f"평균 유사도: {avg_similarity:.2f}%")
        print(f"결과가 저장된 경로: {csv_path}")
        
        # 최소 기대 유사도 (예: 60%)
        min_expected_similarity = 60.0
        self.assertGreaterEqual(avg_similarity, min_expected_similarity,
                              f"평균 유사도({avg_similarity:.2f}%)가 기대치({min_expected_similarity}%)보다 낮습니다.")

if __name__ == '__main__':
    unittest.main() 