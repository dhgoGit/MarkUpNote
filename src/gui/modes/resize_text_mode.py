from PyQt5.QtCore import QSize
from PyQt5.Qt import Qt
from .base_mode import BaseMode
from ..text_box_memory import TextBoxMemory

class ResizeTextMode(BaseMode):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.resizing = False
        self.resize_start = None
        self.original_size = None
        self.resizing_text_box = None
        
    def activate(self):
        """모드 활성화"""
        super().activate()
        self.canvas.setCursor(Qt.CursorShape.SizeAllCursor)
        
    def deactivate(self):
        """모드 비활성화"""
        super().deactivate()
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
        self.resizing = False
        self.resize_start = None
        self.original_size = None
        self.resizing_text_box = None
        
    def mouse_press_event(self, event):
        """마우스 클릭 이벤트 처리"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 모든 텍스트 박스를 검사하여 클릭된 위치의 텍스트 박스 찾기
            pos = event.pos()
            for text_box in self.canvas.text_boxes:
                if text_box.geometry().contains(pos):
                    self.resizing = True
                    self.resize_start = pos
                    self.resizing_text_box = text_box
                    self.original_size = text_box.size()
                    break
            
    def mouse_move_event(self, event):
        """마우스 이동 이벤트 처리"""
        if self.resizing and self.resize_start and self.resizing_text_box and self.original_size:
            try:
                if not self.resizing_text_box.isVisible():
                    self.resizing = False
                    return
                    
                diff = event.pos() - self.resize_start
                new_width = max(100, int(self.original_size.width() + diff.x()))
                new_height = max(50, int(self.original_size.height() + diff.y()))
                
                self.resizing_text_box.resize(new_width, new_height)
            except RuntimeError:
                # 텍스트 박스가 삭제된 경우
                self.resizing = False
                self.resize_start = None
                self.original_size = None
                self.resizing_text_box = None
            
    def mouse_release_event(self, event):
        """마우스 릴리즈 이벤트 처리"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizing = False
            self.resize_start = None
            self.original_size = None
            self.resizing_text_box = None 