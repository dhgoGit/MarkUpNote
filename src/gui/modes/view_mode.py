from .base_mode import BaseMode
from ..text_box_memory import TextBoxMemory

class ViewMode(BaseMode):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.text_box_memory = TextBoxMemory()
        
    def activate(self):
        """View 모드 활성화"""
        # 모든 텍스트 박스에 View 모드 적용
        for text_box in self.text_box_memory.get_text_boxes():
            text_box.setViewMode(True)
            
    def deactivate(self):
        """View 모드 비활성화"""
        # 모든 텍스트 박스의 View 모드 해제
        for text_box in self.text_box_memory.get_text_boxes():
            text_box.setViewMode(False)
            
    def mouse_press_event(self, event):
        pass
        
    def mouse_move_event(self, event):
        pass
        
    def mouse_release_event(self, event):
        pass 