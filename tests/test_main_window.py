import pytest
from PyQt5.QtCore import Qt
from src.gui.main_window import MainWindow

@pytest.fixture
def window(qtbot):
    """테스트용 메인 윈도우 픽스처"""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_window_title(window):
    """윈도우 타이틀 테스트"""
    assert window.windowTitle() == "MarkUpNote"

def test_control_panel_buttons(window):
    """컨트롤 패널 버튼 테스트"""
    assert window.text_mode_btn.text() == "Text Mode"
    assert window.draw_mode_btn.text() == "Draw Mode"
    assert window.process_markup_btn.text() == "Process Markup"
    assert window.save_btn.text() == "Save"

def test_mode_switching(window, qtbot):
    """모드 전환 테스트"""
    # 초기 모드는 텍스트
    assert window.note_canvas.mode == "text"
    
    # 그리기 모드로 전환
    qtbot.mouseClick(window.draw_mode_btn, Qt.MouseButton.LeftButton)
    assert window.note_canvas.mode == "draw"
    
    # 텍스트 모드로 전환
    qtbot.mouseClick(window.text_mode_btn, Qt.MouseButton.LeftButton)
    assert window.note_canvas.mode == "text" 