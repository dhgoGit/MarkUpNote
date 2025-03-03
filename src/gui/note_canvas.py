from PyQt5.QtWidgets import QWidget, QLineEdit, QRubberBand, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPainter, QPen, QColor, QImage, QFont, QPixmap
import os
import uuid
from PIL import Image

from src.utils.text_processor import text_processor
from src.utils.image_to_html_converter import ImageToHtmlConverter
from src.gui.modes.text_mode import TextMode
from src.gui.modes.draw_mode import DrawMode
from src.gui.modes.resize_text_mode import ResizeTextMode
from src.gui.modes.text_recognition_mode import TextRecognitionMode
from src.gui.modes.view_mode import ViewMode
from src.gui.custom_text_box import CustomTextBox

class NoteCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.init_canvas()
        
    def init_canvas(self):
        """캔버스 초기화"""
        self.mode = "text"
        self.previous_mode = "text"  # 이전 모드 저장
        self.drawing = False
        self.last_point = None
        self.text_boxes = []
        self.image = QImage(self.size(), QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        
        # 선택 모드 관련 변수
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.rubber_band = None
        self.buttons_widget = None
        self.selection_fixed = False
        self.processed_area = None  # 처리된 영역 저장
        self.original_image = None  # 원본 이미지 저장
        self.markup_text_box = None  # 현재 처리 중인 텍스트 박스
        self.resizing_text_box = None  # 크기 조절 중인 텍스트 박스
        self.current_font_size = 12  # 기본 폰트 크기를 12pt로 설정
        
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: white;")
        
        # 모드 초기화
        self.text_mode = TextMode(self)
        self.draw_mode = DrawMode(self)
        self.resize_text_mode = ResizeTextMode(self)
        self.text_recognition_mode = TextRecognitionMode(self)
        self.view_mode = ViewMode(self)
        
        # 현재 모드 설정
        self.current_mode = self.text_mode
        
    def resizeEvent(self, event):
        """캔버스 크기 변경 이벤트 처리"""
        if self.width() > 0 and self.height() > 0:
            new_image = QImage(self.size(), QImage.Format.Format_RGB32)
            new_image.fill(Qt.GlobalColor.white)
            painter = QPainter(new_image)
            painter.drawImage(0, 0, self.image)
            self.image = new_image
        
    def paintEvent(self, event):
        """페인트 이벤트 처리"""
        painter = QPainter(self)
        # 배경 이미지 그리기
        painter.drawImage(0, 0, self.image)
        
        # HTMLMemo의 내용 그리기
        if hasattr(self, 'html_memo'):
            self.html_memo.draw(painter, self)
        
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리"""
        self.current_mode.mouse_press_event(event)
        
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        self.current_mode.mouse_move_event(event)
        
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트 처리"""
        self.current_mode.mouse_release_event(event)

    def process_selection(self, area):
        """선택 영역 처리"""
        if not self.selection_fixed:
            return
            
        # 원본 이미지와 영역 저장
        self.processed_area = area
        self.original_image = self.image.copy()
        
        # 선택 영역의 이미지를 추출하고 처리
        selected_image = self.image.copy(area)
        
        # 선택 영역을 회색조로 변환
        painter = QPainter(self.image)
        for y in range(area.top(), area.bottom() + 1):
            for x in range(area.left(), area.right() + 1):
                color = self.image.pixelColor(x, y)
                gray = (color.red() + color.green() + color.blue()) // 3
                painter.setPen(QColor(gray, gray, gray))
                painter.drawPoint(x, y)

        # QImage를 PIL Image로 변환
        buffer = selected_image.bits().asarray(selected_image.byteCount())
        pil_image = Image.frombytes('RGBA', (selected_image.width(), selected_image.height()), buffer, 'raw', 'BGRA')
        
        # 텍스트 처리
        text = text_processor.process_image(pil_image)
        if text:
            # 텍스트 박스 생성
            self.markup_text_box = self.create_text_box(area.topLeft(), text)
            self.markup_text_box.resize(area.width(), area.height())
                
        # 버튼 위젯 숨기기
        if self.buttons_widget:
            self.buttons_widget.hide()
            
        # 선택 영역 숨기기
        if self.rubber_band:
            self.rubber_band.hide()
            
        self.update()

    def show_selection_buttons(self):
        """선택 영역 버튼 표시"""
        if not self.rubber_band or not self.selection_fixed:
            return
            
        if self.buttons_widget:
            self.buttons_widget.hide()
            self.buttons_widget.deleteLater()
            
        selection_area = self.rubber_band.geometry()
        self.buttons_widget = QWidget(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        
        process_btn = QPushButton("텍스트 변환")
        cancel_btn = QPushButton("취소")
        
        process_btn.clicked.connect(lambda: self.process_selection(selection_area))
        cancel_btn.clicked.connect(self.revert_changes)
        
        layout.addWidget(process_btn)
        layout.addWidget(cancel_btn)
        
        # 버튼 스타일 설정
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
        
        # 버튼 위치 조정
        button_pos = selection_area.bottomRight() + QPoint(10, 10)
        self.buttons_widget.move(button_pos)
        self.buttons_widget.show()

    def show_text_control_buttons(self, area):
        """텍스트 컨트롤 버튼 표시"""
        if self.buttons_widget:
            self.buttons_widget.hide()
            self.buttons_widget.deleteLater()
            
        self.buttons_widget = QWidget(self)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 텍스트 크기 조절 버튼
        size_layout = QHBoxLayout()
        decrease_btn = QPushButton("-")
        increase_btn = QPushButton("+")
        size_label = QPushButton(f"{self.current_font_size}pt")
        size_label.setEnabled(False)
        
        decrease_btn.setFixedSize(30, 30)
        increase_btn.setFixedSize(30, 30)
        size_label.setFixedWidth(50)
        
        decrease_btn.clicked.connect(self.decrease_font_size)
        increase_btn.clicked.connect(self.increase_font_size)
        
        size_layout.addWidget(decrease_btn)
        size_layout.addWidget(size_label)
        size_layout.addWidget(increase_btn)
        
        # Commit/Revert 버튼
        button_layout = QHBoxLayout()
        commit_btn = QPushButton("Commit")
        revert_btn = QPushButton("Revert")
        
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
        for btn in [commit_btn, revert_btn, decrease_btn, increase_btn, size_label]:
            btn.setStyleSheet(button_style)
        
        commit_btn.clicked.connect(self.commit_changes)
        revert_btn.clicked.connect(self.revert_changes)
        
        button_layout.addWidget(commit_btn)
        button_layout.addWidget(revert_btn)
        
        main_layout.addLayout(size_layout)
        main_layout.addLayout(button_layout)
        
        self.buttons_widget.setLayout(main_layout)
        button_pos = area.bottomRight() + QPoint(10, 10)
        self.buttons_widget.move(button_pos)
        self.buttons_widget.show()

    def commit_changes(self):
        """변경사항 확정"""
        if self.markup_text_box:
            self.text_boxes.append(self.markup_text_box)
            self.markup_text_box = None
            
        # 회색 영역을 완전히 제거 (흰색이 아닌 투명하게)
        if self.processed_area:
            painter = QPainter(self.image)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.eraseRect(self.processed_area)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.fillRect(self.processed_area, Qt.GlobalColor.white)
            
        self.cleanup_selection()
        self.mode = self.previous_mode  # 이전 모드로 복귀
        self.update()
        
    def revert_changes(self):
        """변경사항 취소"""
        if self.markup_text_box:
            self.markup_text_box.hide()
            self.markup_text_box.deleteLater()
            self.markup_text_box = None
            
        self.cleanup_selection()
        self.mode = self.previous_mode  # 이전 모드로 복귀
        self.update()
        
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
        
    def save_canvas(self):
        """캔버스 저장"""
        if not os.path.exists("saved_notes"):
            os.makedirs("saved_notes")
            
        # UUID 생성
        file_uuid = str(uuid.uuid4())
        image_path = f"saved_notes/{file_uuid}.png"
        html_path = f"saved_notes/{file_uuid}.html"
            
        # 현재 모드 저장
        previous_mode = self.current_mode
        
        # 임시로 View 모드 적용
        self.set_mode("view")
        
        # 텍스트 박스에 태그 추가
        for text_box in self.text_boxes:
            text_box.wrapTextWithTags()
            
        # text_box_memory의 텍스트 박스들도 처리
        if hasattr(self.text_mode, 'text_box_memory'):
            for text_box in self.text_mode.text_box_memory.get_text_boxes():
                text_box.wrapTextWithTags()
        
        # 캔버스 내용 반영 기다리기
        QApplication.processEvents()
        # 현재 화면의 모든 내용을 이미지로 저장
        pixmap = self.grab()
        pixmap.save(image_path)
        
        # 텍스트 박스 원래대로 복원
        for text_box in self.text_boxes:
            text_box.restoreOriginalText()
            
        # text_box_memory의 텍스트 박스들도 복원
        if hasattr(self.text_mode, 'text_box_memory'):
            for text_box in self.text_mode.text_box_memory.get_text_boxes():
                text_box.restoreOriginalText()
        
        # 이미지를 HTML로 변환
        try:
            converter = ImageToHtmlConverter()
            html_content = converter.convert_to_html(image_path)
            
            # HTML 파일 저장
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            print(f"HTML 변환 중 오류 발생: {str(e)}")
        
        # 원래 모드로 복원
        if previous_mode != self.view_mode:
            if previous_mode == self.text_mode:
                self.set_mode("text")
            elif previous_mode == self.draw_mode:
                self.set_mode("draw")
            elif previous_mode == self.resize_text_mode:
                self.set_mode("resize_text")
            elif previous_mode == self.text_recognition_mode:
                self.set_mode("text_recognition")
                
        # 캔버스 초기화
        self.image.fill(Qt.GlobalColor.white)
        
        # 텍스트 박스들 제거
        for text_box in self.text_boxes[:]:
            text_box.hide()
            text_box.deleteLater()
        self.text_boxes.clear()
        
        # text_box_memory의 텍스트 박스들도 제거
        if hasattr(self.text_mode, 'text_box_memory'):
            self.text_mode.text_box_memory.clear_all()
        
        # 캔버스 업데이트
        self.update()

    def increase_font_size(self):
        """폰트 크기 증가"""
        self.current_font_size = min(72, self.current_font_size + 2)  # 최대 72pt
        self.update_font_size()
        
    def decrease_font_size(self):
        """폰트 크기 감소"""
        self.current_font_size = max(6, self.current_font_size - 2)  # 최소 6pt
        self.update_font_size()
        
    def update_font_size(self):
        """폰트 크기 업데이트"""
        if self.markup_text_box and self.buttons_widget:
            # 텍스트 박스의 폰트 크기 변경
            font = self.markup_text_box.font()
            font.setPointSize(self.current_font_size)
            self.markup_text_box.setFont(font)
            
            # 크기 표시 레이블 업데이트
            size_label = self.buttons_widget.findChild(QPushButton, "")
            if size_label:
                size_label.setText(f"{self.current_font_size}pt")

    def set_mode(self, mode_name):
        """모드 변경"""
        # 현재 모드 비활성화
        self.current_mode.deactivate()
        
        # 새로운 모드 설정
        if mode_name == "text":
            self.current_mode = self.text_mode
        elif mode_name == "draw":
            self.current_mode = self.draw_mode
        elif mode_name == "resize_text":
            self.current_mode = self.resize_text_mode
        elif mode_name == "text_recognition":
            self.current_mode = self.text_recognition_mode
        elif mode_name == "view":
            self.current_mode = self.view_mode
            
        # 새로운 모드 활성화
        self.current_mode.activate()
        
    def process_selection(self, area):
        """선택 영역 처리"""
        if not self.selection_fixed:
            return
            
        # 원본 이미지와 영역 저장
        self.processed_area = area
        self.original_image = self.image.copy()
        
        # 선택 영역의 이미지를 추출하고 처리
        selected_image = self.image.copy(area)
        
        # 선택 영역을 회색조로 변환
        painter = QPainter(self.image)
        for y in range(area.top(), area.bottom() + 1):
            for x in range(area.left(), area.right() + 1):
                color = self.image.pixelColor(x, y)
                gray = (color.red() + color.green() + color.blue()) // 3
                painter.setPen(QColor(gray, gray, gray))
                painter.drawPoint(x, y)

        # QImage를 PIL Image로 변환
        buffer = selected_image.bits().asarray(selected_image.byteCount())
        pil_image = Image.frombytes('RGBA', (selected_image.width(), selected_image.height()), buffer, 'raw', 'BGRA')
        
        # 텍스트 처리
        text = text_processor.process_image(pil_image)
        if text:
            # 텍스트 박스 생성
            self.markup_text_box = self.create_text_box(area.topLeft(), text)
            self.markup_text_box.resize(area.width(), area.height())
                
        # 버튼 위젯 숨기기
        if self.buttons_widget:
            self.buttons_widget.hide()
            
        # 선택 영역 숨기기
        if self.rubber_band:
            self.rubber_band.hide()
            
        self.update()

    def clear_canvas(self):
        """캔버스의 모든 내용을 초기화"""
        # 이미지 초기화
        self.image.fill(Qt.GlobalColor.white)
        
        # 텍스트 박스들 제거
        for text_box in self.text_boxes[:]:
            text_box.hide()
            text_box.deleteLater()
        self.text_boxes.clear()
        
        # 캔버스 업데이트
        self.update()

    def create_text_box(self, pos, text=""):
        """텍스트 박스 생성"""
        text_box = CustomTextBox(self)
        text_box.setPlainText(text)
        text_box.move(pos)
        text_box.show()
        self.text_boxes.append(text_box)  # 텍스트 박스를 리스트에 추가
        return text_box 