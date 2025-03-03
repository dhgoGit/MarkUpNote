import pytesseract
from PIL import Image
import numpy as np
import os

class ImageToHtmlConverter:
    def __init__(self):
        # Tesseract 설정
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image_path):
        """이미지 전처리"""
        # 이미지 로드
        image = Image.open(image_path)
        
        # RGB로 변환
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        return image

    def extract_text_from_image(self, image):
        """이미지에서 텍스트 추출"""
        # OCR 수행
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text.strip()

    def convert_to_html(self, image_path):
        # 이미지 전처리
        image = self.preprocess_image(image_path)
        
        # 텍스트 추출
        extracted_text = self.extract_text_from_image(image)
        
        # 줄바꿈 처리
        text_blocks = extracted_text.split('\n\n')
        formatted_text = ''
        for block in text_blocks:
            if block.strip():
                formatted_text += f'<p>{block.replace(chr(10), "<br>")}</p>\n'
        
        # HTML 형식으로 변환
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Converted Document</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 5px;
                    border: 1px solid #e0e0e0;
                }}
                p {{
                    margin: 0 0 1em 0;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {formatted_text}
            </div>
        </body>
        </html>
        """
        
        return html_content 