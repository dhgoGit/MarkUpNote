import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
import argparse

def main():
    """애플리케이션 메인 함수"""
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description='MarkUpNote 애플리케이션')
    parser.add_argument('--debug', action='store_true', help='디버그 모드 활성화')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(debug_mode=args.debug)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 