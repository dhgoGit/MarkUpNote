from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QCursor, QPixmap, QColor
from .base_mode import BaseMode
from ..text_box_memory import TextBoxMemory

class DrawMode(BaseMode):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.text_box_memory = TextBoxMemory()
        self.drawing = False
        self.erasing = False
        self.last_point = None
        self.pen_width = 2
        self.eraser_width = 10  # 지우개 크기를 10px로 설정
        self.default_cursor = QCursor(Qt.CursorShape.ArrowCursor)
        self.create_eraser_cursor()
        
    def create_eraser_cursor(self):
        """지우개 커서 생성"""
        # 지우개 크기보다 약간 큰 픽스맵 생성
        cursor_size = self.eraser_width + 2
        pixmap = QPixmap(cursor_size, cursor_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # 흰색 원과 테두리 그리기
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 테두리 그리기
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawEllipse(1, 1, self.eraser_width, self.eraser_width)
        painter.end()
        
        # 커서 생성 (중심점을 원의 중앙으로 설정)
        self.eraser_cursor = QCursor(pixmap, cursor_size//2, cursor_size//2)
        
    def mouse_move_event(self, event):
        painter = QPainter(self.canvas.image)
        if self.drawing:
            painter.setPen(QPen(Qt.GlobalColor.black, self.pen_width, Qt.PenStyle.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.canvas.update()
        elif self.erasing:
            painter.setPen(QPen(Qt.GlobalColor.white, self.eraser_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.canvas.update()
            
    def mouse_release_event(self, event):
        self.drawing = False
        self.erasing = False
        
    def activate(self):
        """모드 활성화"""
        self.canvas.setCursor(self.default_cursor)
        
    def deactivate(self):
        """모드 비활성화"""
        self.canvas.setCursor(self.default_cursor)
        
    def mouse_press_event(self, event):
        ## 펜
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.erasing = False
            self.last_point = event.pos()
            self.canvas.setCursor(self.default_cursor)
        ## 지우개
        elif event.button() == Qt.MouseButton.RightButton:
            self.drawing = False
            self.erasing = True
            self.last_point = event.pos()
            self.canvas.setCursor(self.eraser_cursor)