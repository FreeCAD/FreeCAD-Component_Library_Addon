from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QGraphicsBlurEffect, QWidget


class Overlay(QWidget):
	def __init__(self, parent):
		super().__init__(parent)

		self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

		self.fillColor = QColor(30, 30, 30, 120)
		self.penColor = QColor("#333333")

		self.popup_fillColor = QColor(240, 240, 240, 255)
		self.popup_penColor = QColor(200, 200, 200, 255)

	def paintEvent(self, event):
		s = self.size()
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.RenderHint.Antialiasing, True)

		popup_width = 300
		popup_height = 120
		ow = int(s.width()/2-popup_width/2)
		oh = int(s.height()/2-popup_height/2)

		font = QFont()
		font.setPixelSize(20)
		font.setItalic(True)
		qp.setFont(font)
		qp.setPen(QColor(70, 70, 70))
		qp.setPen(Qt.GlobalColor.white)
		tolw, tolh = 80, -5
		qp.drawText(ow + int(popup_width/2) - tolw, oh + int(popup_height/2) - tolh, "loading...")

		qp.end()

	def show(self):
		self.move(0, 0)
		self.resize(self.parent().size()) # type: ignore
		self.blur_effect = QGraphicsBlurEffect()
		self.blur_effect.setBlurRadius(30)
		self.parent().widget().setGraphicsEffect(self.blur_effect) # type: ignore

		return super().show()

	def hide(self) -> None:
		self.parent().widget().setGraphicsEffect(None) # type: ignore
		return super().hide()
