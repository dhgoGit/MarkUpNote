def show_selection_buttons(self):
    """선택 영역 버튼 표시
    
    버튼 위치 설정 과정:
    1. selection_area = self.rubber_band.geometry(): 현재 선택된 영역의 위치와 크기 정보를 가져옵니다.
    2. selection_area.bottomRight(): 선택 영역의 오른쪽 아래 모서리 좌표를 가져옵니다.
    3. QPoint(10, 10): x와 y 방향으로 각각 10픽셀씩 offset을 줍니다.
    4. button_pos = selection_area.bottomRight() + QPoint(10, 10): 최종적으로 버튼이 위치할 곳을 계산합니다.
    5. self.buttons_widget.move(button_pos): 계산된 위치로 버튼 위젯을 이동시킵니다.
    
    결과적으로 버튼들은 선택 영역의 오른쪽 아래 모서리에서 10픽셀 떨어진 위치에 나타나게 됩니다.
    """
