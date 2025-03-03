from PyQt5.QtWidgets import QTextEdit, QWidget, QPushButton, QMenu, QInputDialog, QLineEdit, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor

class DragHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(25, 25)  # 드래그 핸들 크기를 20x20으로 증가
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.dragging = False
        self.drag_start = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(100, 100, 100, 150))  # 반투명 회색
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.globalPos() - self.parent().pos()
        elif event.button() == Qt.MouseButton.RightButton:
            if Qt.KeyboardModifier.AltModifier & event.modifiers():
                parent = self.parent()
                if parent:
                    parent.cleanup()  # 정리 작업 수행 후 삭제
                    parent.deleteLater()
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.drag_start
            self.parent().move(new_pos)
            
    def mouseReleaseEvent(self, event):
        self.dragging = False

class HtmlButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("HTML", parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 100);
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 120, 150);
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 25)
        
        # 더블 클릭으로 텍스트 수정 가능하게 설정
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def mouseDoubleClickEvent(self, event):
        """더블 클릭으로 텍스트 수정"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.edit_text()
            
    def show_context_menu(self, position):
        """컨텍스트 메뉴 표시"""
        menu = QMenu(self)
        edit_action = menu.addAction("텍스트 수정")
        edit_action.triggered.connect(self.edit_text)
        menu.exec_(self.mapToGlobal(position))
        
    def edit_text(self):
        """버튼 텍스트 수정"""
        text, ok = QInputDialog.getText(self, '버튼 텍스트 수정', 
                                      '새로운 텍스트를 입력하세요:', 
                                      QLineEdit.EchoMode.Normal,
                                      self.text())
        if ok and text:
            self.setText(text)
            # 텍스트 길이에 따라 버튼 크기 조정
            fm = self.fontMetrics()
            width = fm.horizontalAdvance(text) + 20  # 여백 추가
            self.setFixedSize(max(50, width), 25)
        
    def updatePosition(self, parent_size):
        """버튼 위치 업데이트"""
        self.move(parent_size.width() - self.width() - 5,
                 parent_size.height() - self.height() - 5)

class ResizeHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(25, 25)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)  # 대각선 방향 크기 조절 커서
        self.resizing = False
        self.resize_start = None
        self.original_size = None
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(100, 100, 100, 150))  # 반투명 회색
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resizing = True
            self.resize_start = event.globalPos()
            self.original_size = self.parent().size()
            
    def mouseMoveEvent(self, event):
        if self.resizing and self.resize_start and self.original_size:
            diff = event.globalPos() - self.resize_start
            new_width = max(100, int(self.original_size.width() + diff.x()))
            new_height = max(50, int(self.original_size.height() + diff.y()))
            self.parent().resize(new_width, new_height)
            
    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_start = None
        self.original_size = None

class CustomTextBox(QTextEdit):
    def __init__(self, parent=None, memory=None):
        super().__init__(parent)
        self.memory = memory
        self.view_mode = False
        self.original_text = ""  # 원본 텍스트 저장용
        
        # 패딩과 마진 설정
        self.padding = 5
        self.margin = 2
        self.total_spacing = (self.padding + self.margin) * 2
        
        # 기본 폰트 크기 설정
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        
        # 초기 크기 설정
        self.resize(200, 50)
        
        self.drag_handle = None
        self.resize_handle = None
        self.html_button = None
        
        # 스타일 초기화 (가장 마지막에 실행)
        self.updateStyle()
        
        # 텍스트 변경 시 크기 조절
        self.textChanged.connect(self.adjust_size)
        
    def updateStyle(self):
        """view_mode에 따라 스타일 업데이트"""
        if self.view_mode:
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: white;
                    border: 1px dashed gray;
                    padding: {self.padding}px;
                    margin: {self.margin}px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: white;
                    border: 1px dashed gray;
                    padding: {self.padding}px;
                    margin: {self.margin}px;
                }}
            """)
            
    def setViewMode(self, enabled):
        """View 모드 설정"""
        self.view_mode = enabled
        self.updateStyle()
        
        if enabled:
            if self.drag_handle:
                self.drag_handle.hide()  # View 모드에서도 드래그 핸들 표시
            if not self.html_button:
                self.html_button = HtmlButton(self)
            self.html_button.show()  # View 모드에서 HTML 버튼 표시
            self.html_button.updatePosition(self.size())
            if self.resize_handle:
                self.resize_handle.hide()  # View 모드에서는 리사이즈 핸들 숨기기
        else:
            if self.drag_handle:
                self.drag_handle.show()  # 드래그 핸들은 항상 표시
            if self.html_button:
                self.html_button.hide()
            
    def enterEvent(self, event):
        """마우스가 위젯 영역에 들어올 때"""
        super().enterEvent(event)
        if self.resize_handle and not self.view_mode:  # View 모드가 아닐 때만 보이기
            self.resize_handle.show()
            
    def leaveEvent(self, event):
        """마우스가 위젯 영역을 벗어날 때"""
        super().leaveEvent(event)
        if self.resize_handle:
            self.resize_handle.hide()
            
    def showEvent(self, event):
        super().showEvent(event)
        # 드래그 핸들 생성 및 위치 설정
        if not self.drag_handle:
            self.drag_handle = DragHandle(self)
            self.updateDragHandlePosition()
            self.drag_handle.show()  # 드래그 핸들은 항상 표시
            
        # 리사이즈 핸들 생성 및 위치 설정
        if not self.resize_handle:
            self.resize_handle = ResizeHandle(self)
            self.updateResizeHandlePosition()
            self.resize_handle.hide()  # 초기에는 숨김
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.drag_handle:
            self.updateDragHandlePosition()
        if self.resize_handle:
            self.updateResizeHandlePosition()
        if self.html_button and self.view_mode:
            self.html_button.updatePosition(self.size())
            
    def updateDragHandlePosition(self):
        """드래그 핸들 위치 업데이트"""
        if self.drag_handle:
            self.drag_handle.move(0, 0)
            
    def updateResizeHandlePosition(self):
        """리사이즈 핸들 위치 업데이트"""
        if self.resize_handle:
            self.resize_handle.move(
                self.width() - self.resize_handle.width(),
                self.height() - self.resize_handle.height()
            )
            
    def cleanup(self):
        """위젯 삭제 전 정리 작업"""
        if self.parent() and hasattr(self.parent(), 'text_boxes'):
            if self in self.parent().text_boxes:
                self.parent().text_boxes.remove(self)
                
        if self.memory and hasattr(self.memory, 'remove_text_box'):
            self.memory.remove_text_box(self)
        if self.drag_handle:
            self.drag_handle.deleteLater()
            self.drag_handle = None
        if self.resize_handle:
            self.resize_handle.deleteLater()
            self.resize_handle = None
        if self.html_button:
            self.html_button.deleteLater()
            self.html_button = None
        
    def closeEvent(self, event):
        """위젯이 닫힐 때 호출되는 이벤트"""
        self.cleanup()
        super().closeEvent(event)
        
    def deleteLater(self):
        """위젯 삭제 시 호출되는 메서드"""
        self.cleanup()
        super().deleteLater()
        
    def adjust_size(self):
        """텍스트 내용에 따라 크기 자동 조절"""
        # 텍스트 크기 계산을 위해 자동 줄바꿈 비활성화
        doc = self.document()
        doc.setTextWidth(-1)
        
        # 여유 공간 계산
        width_margin = 1.3  # 30% 여유 공간
        height_margin = 1.5  # 50% 여유 공간
        
        # 텍스트 크기에 여유 공간 추가
        text_width = int(doc.idealWidth() * width_margin + self.total_spacing)
        text_height = int(doc.size().height() * height_margin + self.total_spacing)
        
        # 최소/최대 크기 제한
        text_width = max(min(text_width, 500), 100)  # 최대 500px, 최소 100px
        text_height = max(min(text_height, 300), 50)  # 최대 300px, 최소 50px
        
        # 크기 조절
        self.resize(text_width, text_height)
        
        # 줄바꿈 설정 복원
        doc.setTextWidth(text_width - self.total_spacing)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        
    def wrapTextWithTags(self):
        """텍스트를 HTML 버튼의 텍스트로 감싸기"""
        if self.html_button and self.html_button.isVisible():
            current_text = self.toPlainText()
            self.original_text = current_text
            button_text = self.html_button.text()
            wrapped_text = f"<{button_text}>{current_text}</{button_text}>"
            self.setPlainText(wrapped_text)
            self.html_button.hide()
            self.document().contentsChanged.emit()  # 내용 변경 시그널 강제 발생
            self.parent().repaint()
            # 약간의 지연을 주어 텍스트가 완전히 설정되도록 함
            QApplication.processEvents()
            
    def restoreOriginalText(self):
        """원본 텍스트로 복원"""
        if self.original_text:
            self.setPlainText(self.original_text)
            self.original_text = ""
            if self.view_mode and self.html_button:
                self.html_button.show()
            self.parent().repaint()
            QApplication.processEvents()

