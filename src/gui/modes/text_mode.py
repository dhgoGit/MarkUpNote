from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit
from .base_mode import BaseMode
from ..text_box_memory import TextBoxMemory

class TextMode(BaseMode):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.text_box_memory = TextBoxMemory()
        self.current_text_box = None
        
    def mouse_press_event(self, event):
        ## 텍스트 상자 생성, 폰트 사이즈에 맞게끔 크기 조절되게 생성해야함.
        self.current_text_box = self.create_text_box(event.pos())
        self.canvas.set_mode("resize_text")
            
    def mouse_move_event(self, event):
        pass
        
    def mouse_release_event(self, event):
        pass
        
    def create_text_box(self, pos, text=None):
        """텍스트 상자 생성"""
        return self.text_box_memory.add_text_box(self.canvas, pos, text)
        
    def deactivate(self):
        pass
        
    def activate(self):
        pass