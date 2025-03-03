from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtWidgets import QRubberBand, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QImage
from PIL import Image
from datetime import datetime
import os
from .base_mode import BaseMode
from src.utils.text_processor import text_processor

class TextRecognitionMode(BaseMode):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.rubber_band = None
        self.buttons_widget = None
        self.selection_fixed = False
        self.processed_area = None
        self.original_image = None
        self.debug_mode = False  # 디버그 모드 기본값 설정
        
    def activate(self):
        self.selecting = True
        self.selection_fixed = False
        self.selection_start = None
        self.selection_end = None
        
    def mouse_press_event(self, event):
        if not self.selection_fixed:
            self.selection_start = event.pos()
            self.selection_end = None
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.canvas)
            self.rubber_band.setGeometry(QRect(self.selection_start, QSize()))
            self.rubber_band.show()
            
    def mouse_move_event(self, event):
        if not self.selection_fixed and self.selection_start:
            self.selection_end = event.pos()
            if self.rubber_band:
                self.rubber_band.setGeometry(QRect(self.selection_start, self.selection_end).normalized())
                
    def mouse_release_event(self, event):
        if not self.selection_fixed and self.selection_start:
            self.selection_end = event.pos()
            if self.rubber_band and self.selection_end:
                self.selection_fixed = True
                self.show_selection_buttons()
                
    def show_selection_buttons(self):
        """선택 영역 버튼 표시
        
        버튼 위치 설정 과정:
        1. selection_area = self.rubber_band.geometry(): 현재 선택된 영역의 위치와 크기 정보를 가져옵니다.
        2. selection_area.bottomRight(): 선택 영역의 오른쪽 아래 모서리 좌표를 가져옵니다.
        3. QPoint(10, 10): x와 y 방향으로 각각 10픽셀씩 offset을 줍니다.
        4. button_pos = selection_area.bottomRight() + QPoint(10, 10): 최종적으로 버튼이 위치할 곳을 계산합니다.
        5. self.buttons_widget.move(button_pos): 계산된 위치로 버튼 위젯을 이동시킵니다.
        
        결과적으로 버튼들은 선택 영역의 오른쪽 아래 모서리에서 10픽셀 떨어진 위치에 나타나게 됩니다.
        """
        if not self.rubber_band or not self.selection_fixed:
            return
            
        ## 버튼 위치 조정
        if self.buttons_widget:
            self.buttons_widget.hide()
            self.buttons_widget.deleteLater()
            
        selection_area = self.rubber_band.geometry()
        self.buttons_widget = QWidget(self.canvas)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        process_btn = QPushButton("텍스트 변환")
        cancel_btn = QPushButton("취소")
        
        process_btn.clicked.connect(lambda: self.process_selection(selection_area))
        cancel_btn.clicked.connect(self.cleanup_selection)
        
        layout.addWidget(process_btn)
        layout.addWidget(cancel_btn)
        
        button_style = """
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """
        for btn in [process_btn, cancel_btn]:
            btn.setStyleSheet(button_style)
            
        self.buttons_widget.setLayout(layout)
        button_pos = selection_area.bottomRight() + QPoint(10, 10)
        self.buttons_widget.move(button_pos)
        self.buttons_widget.show()
        
    def process_selection(self, area):
        """선택 영역 처리"""
        if not self.selection_fixed:
            return
            
        # 원본 이미지와 영역 저장
        self.processed_area = area
        self.original_image = self.canvas.image.copy()
        
        # 선택 영역의 이미지를 추출하고 처리
        selected_image = self.canvas.image.copy(area)
        
        # 선택 영역을 완전히 지우기
        painter = QPainter(self.canvas.image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.eraseRect(area)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.fillRect(area, Qt.GlobalColor.white)
                
        # QImage를 PIL Image로 변환
        buffer = selected_image.bits().asarray(selected_image.byteCount())
        pil_image = Image.frombytes('RGBA', (selected_image.width(), selected_image.height()), buffer, 'raw', 'BGRA')
        
        # 텍스트 처리
        text = text_processor.process_image(pil_image)
        if text:
            # 텍스트 박스 생성 (크기는 자동으로 조절됨)
            text_box = self.canvas.text_mode.create_text_box(area.topLeft(), text)
            # 피드백 저장
            self.store_feedback(pil_image, text)
            
        # 선택 영역과 버튼 숨기기
        self.cleanup_selection()
        
        # 텍스트 크기 조절 모드로 전환
        self.canvas.set_mode("resize_text")
        self.canvas.update()
        
    def cleanup_selection(self):
        """선택 모드 정리"""
        if self.rubber_band:
            self.rubber_band.hide()
        if self.buttons_widget:
            self.buttons_widget.hide()
            self.buttons_widget.deleteLater()
            self.buttons_widget = None
        self.selecting = False
        self.selection_fixed = False
        self.selection_start = None
        self.selection_end = None
        self.processed_area = None
        self.original_image = None
        
    def deactivate(self):
        self.cleanup_selection() 
        
    ##
    def store_feedback(self, image, converted_text):
        """피드백 저장"""
        if not self.debug_mode:
            return
        
        # 디버그 디렉토리 생성
        self.debug_dir = "debug/feedback"
        os.makedirs(self.debug_dir, exist_ok=True)
        
        # 현재 시간 기반 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"feedback_{timestamp}.png"
        
        # 이미지 저장
        image.save(os.path.join(self.debug_dir, file_name))
        
        # 텍스트 저장
        with open(os.path.join(self.debug_dir, "feedback.txt"), "a") as f:
            f.write(f"{timestamp}: {converted_text}\n")
        