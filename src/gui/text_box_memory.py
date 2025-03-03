from PyQt5.QtGui import QFont
from .custom_text_box import CustomTextBox

class TextBoxMemory:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TextBoxMemory, cls).__new__(cls)
            cls._instance._text_boxes = []
            cls._instance._current_mode = None
        return cls._instance
        
    def add_text_box(self, canvas, pos, text=None):
        """텍스트 박스 생성 및 추가"""
        text_box = CustomTextBox(canvas, self)
        text_box.move(pos)
        
        # 폰트 크기 설정 (12pt로 고정)
        font = text_box.font()
        font.setPointSize(12)
        text_box.setFont(font)
        
        # 패딩 설정
        padding = 5  # 5px padding
        margin = 3   # 3px margin for safety
        total_spacing = (padding + margin) * 2  # 양쪽에 적용되므로 2배
        
        # 텍스트가 주어진 경우 설정
        if text:
            text_box.setText(text)
            # 텍스트 내용에 따라 크기 조절
            doc = text_box.document()
            doc.setTextWidth(-1)  # 자동 줄바꿈 비활성화하여 실제 텍스트 크기 계산
            
            # 텍스트 길이에 따른 여유 공간 계산
            width_margin = 1.3  # 30% 여유 공간
            height_margin = 1.5  # 50% 여유 공간 (증가)
            
            # 여유 공간을 고려한 크기 계산
            text_width = int(doc.idealWidth() * width_margin + total_spacing)
            text_height = int(doc.size().height() * height_margin + total_spacing)
            
            # 최소/최대 크기 설정
            text_width = max(min(text_width, 500), 100)  # 최대 500px, 최소 100px
            text_height = max(min(text_height, 300), 50)  # 최대 300px, 최소 50px (증가)
            
            text_box.resize(text_width, text_height)
            doc.setTextWidth(text_width - total_spacing)  # 패딩을 고려하여 줄바꿈 설정
        else:
            # 새로운 빈 텍스트 박스는 더 큰 크기로 생성
            text_box.resize(200, 50)  # 높이를 50px로 증가
        
        # 스타일 설정
        text_box.setStyleSheet(f"""
                QTextEdit {{
                    background-color: white;
                    border: 1px dashed gray;
                    padding: {padding}px;
                    margin: {margin}px;
                }}
            """)
        
        text_box.show()
        text_box.setFocus()
        self._text_boxes.append(text_box)
        return text_box
        
    def get_text_boxes(self):
        """모든 텍스트 박스 반환"""
        return self._text_boxes
        
    def hide_all(self):
        """모든 텍스트 박스 숨기기"""
        for text_box in self._text_boxes:
            text_box.hide()
            
    def show_all(self):
        """모든 텍스트 박스 보이기"""
        for text_box in self._text_boxes:
            text_box.show()
            
    def remove_text_box(self, text_box):
        """텍스트 박스 제거"""
        if text_box in self._text_boxes:
            self._text_boxes.remove(text_box)
            text_box.deleteLater()
            
    def clear_all(self):
        """모든 텍스트 박스 제거"""
        for text_box in self._text_boxes[:]:
            text_box.deleteLater()
        self._text_boxes.clear()
        
    def set_mode(self, mode):
        """현재 모드 설정"""
        self._current_mode = mode