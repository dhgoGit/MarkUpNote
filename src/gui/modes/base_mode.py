from abc import ABC, abstractmethod
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QMouseEvent

class BaseMode(ABC):
    def __init__(self, canvas):
        self.canvas = canvas
        
    @abstractmethod
    def mouse_press_event(self, event: QMouseEvent):
        pass
        
    @abstractmethod
    def mouse_move_event(self, event: QMouseEvent):
        pass
        
    @abstractmethod
    def mouse_release_event(self, event: QMouseEvent):
        pass
        
    def activate(self):
        """모드 활성화 시 호출"""
        pass
        
    def deactivate(self):
        """모드 비활성화 시 호출"""
        pass 