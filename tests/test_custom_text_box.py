import unittest
from PyQt5.QtWidgets import QApplication
from src.gui.custom_text_box import CustomTextBox, HtmlButton

class TestCustomTextBox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.text_box = CustomTextBox()
        self.text_box.show()  # 텍스트박스도 보이게 설정
        self.text_box.setPlainText("hello man!!!")
        self.text_box.html_button = HtmlButton(self.text_box)
        self.text_box.html_button.setText("HTML")
        self.text_box.html_button.show()
        self.text_box.html_button.setVisible(True)
        self.text_box.view_mode = True  # view_mode를 True로 설정

    def test_text_wrapping_with_html_tags(self):
        """텍스트 저장 시 HTML 태그로 감싸지는지 테스트"""
        self.assertTrue(self.text_box.html_button.isVisible())
        self.text_box.wrapTextWithTags()
        expected_text = "<HTML>hello man!!!</HTML>"
        actual_text = self.text_box.toPlainText()
        self.assertEqual(
            actual_text, 
            expected_text, 
            f"Expected text to be wrapped with HTML tags.\nExpected: {expected_text}\nActual: {actual_text}"
        )
        self.text_box.restoreOriginalText()

    def test_html_button_text_in_tags(self):
        """HTML 버튼의 텍스트가 태그로 사용되는지 테스트"""
        self.assertTrue(self.text_box.html_button.isVisible())
        self.text_box.html_button.setText("button")
        self.text_box.wrapTextWithTags()
        expected_text = "<button>hello man!!!</button>"
        actual_text = self.text_box.toPlainText()
        self.assertEqual(
            actual_text, 
            expected_text, 
            f"Expected text to be wrapped with button tags.\nExpected: {expected_text}\nActual: {actual_text}"
        )
        self.text_box.restoreOriginalText()

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

if __name__ == '__main__':
    unittest.main() 