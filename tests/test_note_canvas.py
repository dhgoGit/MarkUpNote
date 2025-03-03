import pytest
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage
from src.gui.note_canvas import NoteCanvas

@pytest.fixture
def canvas(qtbot):
    """테스트용 노트 캔버스 픽스처"""
    canvas = NoteCanvas()
    qtbot.addWidget(canvas)
    return canvas

def test_initial_state(canvas):
    """초기 상태 테스트"""
    assert canvas.mode == "text"
    assert not canvas.drawing
    assert canvas.last_point is None
    assert len(canvas.text_boxes) == 0
    assert isinstance(canvas.image, QImage)

def test_text_mode(canvas, qtbot):
    """텍스트 모드 테스트"""
    # 텍스트 모드에서 클릭
    canvas.set_mode("text")
    qtbot.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    
    # 텍스트 박스가 생성되었는지 확인
    assert len(canvas.text_boxes) == 1
    text_box = canvas.text_boxes[0]
    assert text_box.pos() == QPoint(100, 100)

def test_draw_mode(canvas, qtbot):
    """그리기 모드 테스트"""
    # 그리기 모드로 전환
    canvas.set_mode("draw")
    
    # 마우스 드래그 시뮬레이션
    qtbot.mousePress(canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    assert canvas.drawing
    assert canvas.last_point == QPoint(100, 100)
    
    qtbot.mouseMove(canvas, pos=QPoint(150, 150))
    assert canvas.last_point == QPoint(150, 150)
    
    qtbot.mouseRelease(canvas, Qt.MouseButton.LeftButton)
    assert not canvas.drawing

def test_selection_mode(canvas, qtbot):
    """선택 모드 테스트"""
    # 선택 모드 시작
    canvas.start_selection()
    assert canvas.selecting
    assert canvas.mode == "selection"
    
    # 영역 선택 시뮬레이션
    qtbot.mousePress(canvas, Qt.MouseButton.LeftButton, pos=QPoint(100, 100))
    assert canvas.selection_start == QPoint(100, 100)
    assert canvas.rubber_band is not None
    
    # 선택 취소
    canvas.cancel_selection()
    assert not canvas.selecting
    assert canvas.mode == "text" 