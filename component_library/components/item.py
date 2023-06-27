from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget

from .ui.Ui_item_view import Ui_ComponentItemView


class ComponentItem(QWidget, Ui_ComponentItemView):

	def __init__(self, parent: QWidget, data:dict) -> None:

		super().__init__(parent)
		self.setupUi(self)

		self.data: dict[str, str] = data

		self.setupItem()


	def setupItem(self):
		url = QUrl(self.data.get("thumbnail", ""))
		self.thumbnail.setupThumbnail(url)
		self.componentLabel.setText(self.data.get("name", "").capitalize())
