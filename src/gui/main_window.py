from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from src.gui.note_canvas import NoteCanvas

class MainWindow(QMainWindow):
    def __init__(self, debug_mode=False):
        super().__init__()
        self.debug_mode = debug_mode
        self.init_ui()
        self.current_mode = "text"  # 초기 모드 설정
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("MarkUpNote")
        self.setGeometry(100, 100, 1200, 800)
        
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 레이아웃 설정
        layout = QHBoxLayout()
        main_widget.setLayout(layout)
        
        # 컨트롤 영역 설정
        self.setup_control_panel(layout)
        
        # 노트 캔버스 생성
        self.note_canvas = NoteCanvas()
        # 디버그 모드 설정 전달
        self.note_canvas.text_recognition_mode.debug_mode = self.debug_mode
        layout.addWidget(self.note_canvas)
        
    def setup_control_panel(self, parent_layout):
        """컨트롤 패널 설정"""
        control_widget = QWidget()
        control_widget.setFixedWidth(150)  # 컨트롤 패널 너비 설정
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(10, 20, 10, 20)  # 여백 설정
        control_layout.setSpacing(10)  # 버튼 간격 설정
        
        # 기본 버튼 스타일
        self.default_style = """
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: 500;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #d0d0d0;
            }
        """
        
        # 활성화된 버튼 스타일
        self.active_style = """
            QPushButton {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: 500;
                color: #1976d2;
            }
        """
        
        # 텍스트 모드 버튼
        self.text_btn = QPushButton("텍스트")
        self.text_btn.clicked.connect(self.set_text_mode)
        
        # 그리기 모드 버튼
        self.draw_btn = QPushButton("필기")
        self.draw_btn.clicked.connect(self.set_draw_mode)
        
        # 텍스트 인식 버튼
        self.text_recognition_btn = QPushButton("텍스트 인식")
        self.text_recognition_btn.clicked.connect(self.process_text)
        
        # View 모드 버튼 추가
        self.view_btn = QPushButton("View")
        self.view_btn.clicked.connect(self.set_view_mode)
        
        # 저장 버튼 (특별 스타일)
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self.save_note)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: 500;
                color: white;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
        """)
        
        # 모든 모드 버튼에 기본 스타일 적용
        self.mode_buttons = {
            "text": self.text_btn,
            "draw": self.draw_btn,
            "text_recognition": self.text_recognition_btn,
            "view": self.view_btn,
        }
        
        for btn in self.mode_buttons.values():
            btn.setStyleSheet(self.default_style)
        
        # 현재 모드 버튼 활성화
        self.update_button_styles("text")
        
        # 버튼들을 레이아웃에 추가
        control_layout.addWidget(self.text_btn)
        control_layout.addWidget(self.draw_btn)
        control_layout.addWidget(self.text_recognition_btn)
        control_layout.addWidget(self.view_btn)
        control_layout.addSpacing(20)  # 저장 버튼 위에 여백 추가
        control_layout.addWidget(self.save_btn)
        control_layout.addStretch()
        
        # 컨트롤 위젯에 마우스 이벤트 추가
        control_widget.mousePressEvent = self.handle_control_panel_click
        
        control_widget.setLayout(control_layout)
        control_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border-right: 1px solid #e0e0e0;
            }
        """)
        parent_layout.addWidget(control_widget)
        
    def update_button_styles(self, active_mode):
        """현재 모드에 따라 버튼 스타일 업데이트"""
        self.current_mode = active_mode
        for mode, btn in self.mode_buttons.items():
            if mode == active_mode:
                btn.setStyleSheet(self.active_style)
            else:
                btn.setStyleSheet(self.default_style)
                
    def handle_control_panel_click(self, event):
        """컨트롤 패널 클릭 처리"""
        clicked_widget = self.childAt(event.pos())
        if clicked_widget is None or isinstance(clicked_widget, QWidget) and not isinstance(clicked_widget, QPushButton):
            self.set_resize_text_mode()
            # 모든 버튼을 기본 스타일로 되돌림
            for btn in self.mode_buttons.values():
                btn.setStyleSheet(self.default_style)
            self.current_mode = "resize_text"
        
    def set_text_mode(self):
        """텍스트 모드로 전환"""
        self.note_canvas.set_mode("text")
        self.update_button_styles("text")
        # View 모드 해제
        for text_box in self.note_canvas.text_mode.text_box_memory.get_text_boxes():
            text_box.setViewMode(False)
        
    def set_draw_mode(self):
        """그리기 모드로 전환"""
        self.note_canvas.set_mode("draw")
        self.update_button_styles("draw")
        
    def set_resize_text_mode(self):
        """텍스트 박스 크기 조절 모드로 전환"""
        self.note_canvas.set_mode("resize_text")
        # resize 모드는 버튼 하이라이트 없음
        
    def process_text(self):
        """텍스트 변환 시작"""
        self.note_canvas.set_mode("text_recognition")
        self.update_button_styles("text_recognition")
        
    def save_note(self):
        """노트 저장"""
        self.note_canvas.save_canvas()
        # 저장 후 캔버스 초기화
        self.note_canvas.clear_canvas()
        # 텍스트 모드로 초기화
        self.set_text_mode()

    def set_view_mode(self):
        """View 모드로 전환"""
        self.note_canvas.set_mode("view")
        self.update_button_styles("view")

    def set_mode(self, mode_name):
        """모드 변경 처리"""
        self.current_mode = mode_name
        self.note_canvas.set_mode(mode_name)
        self.text_box_memory.set_mode(mode_name)  # TextBoxMemory 모드 업데이트
        self.update_button_styles()