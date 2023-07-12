from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QNetworkRequest

from ..data import Component, DTypes, FileTypes
from ..network import network_access_manager, sslConfig
from ..network.api import Api, ApiReply, ComponentRequest, getApi
from ..utils import Interface
from .downloader import FileDownloader
from .page import PageStates
from .query import ComponentQueryInterface, RepoComponentQuery


class ManagerInterface(Interface):
	component_loaded: Signal

	api: Any # TODO change type of api to APIInterface
	page_states: PageStates
	query: ComponentQueryInterface

	def reload_page(self):
		raise NotImplementedError

	def next_page(self):
		raise NotImplementedError

	def prev_page(self):
		raise NotImplementedError

	def search(self, search_key: str):
		raise NotImplementedError

	def sort(self, /, by: str, order: str):
		# TODO make ENums for by and order
		raise NotImplementedError

	def filter(self,/ , filetypes: list[str], tags: list[str]):
		# TODO replace typehint of filetypes & tags with enum
		raise NotImplementedError



class OnlineRepoManager(QObject):
	component_loaded = Signal()

	query = RepoComponentQuery()
	page_states = PageStates()
	DOWNLOAD_PATH = "/home/encryptedbee/tesla/projects/GSOC/Component_Library_Plugin/test/downloads"

	def __init__(self, api_url: str) -> None:
		super().__init__()
		self.api: Api = getApi(api_url, network_access_manager, sslConfig)

	def reload_page(self) -> ApiReply:
		self.query.page = 1
		return self.request_components()

	def next_page(self) -> ApiReply:
		self.query.page = self.page_states.next_page
		return self.request_components()

	def prev_page(self) -> ApiReply:
		self.query.page = self.page_states.prev_page
		return self.request_components()

	def search(self, search_key: str) -> ApiReply:
		self.query.search_key = search_key
		return self.reload_page()

	def sort(self, /, by: str, order: str) -> ApiReply:
		self.query.sort_by = by
		self.query.sort_ord = order
		return self.reload_page()

	def filter(self,/ , filetypes: list[str], tags: list[str]) -> ApiReply:
		self.query.file_types = filetypes
		self.query.tags = tags
		return self.reload_page()


	def download_component(self, component: Component, filetype: FileTypes) -> FileDownloader:
		file = component.files.get(filetype)
		if file is None:
			raise FileNotFoundError()
		return FileDownloader(file.url, self.DOWNLOAD_PATH, f"{component.name}.{file.type}")


	def request_components(self) -> ApiReply:
		reply: ApiReply = self.api.get(ComponentRequest(self.query))
		reply.finished.connect(self.__component_response_handler)
		return reply


	def request_tags(self) -> ApiReply:
		reply: ApiReply = self.api.get(QNetworkRequest("tag"))
		return reply


	Slot(dict)
	def __component_response_handler(self, json_data: dict[str, Any]):
		page: PageStates = self.page_states.load_page(json_data, DTypes.COMPONENT)
		self.query.page = page.page_no
		self.query.page_size = page.size
		self.component_loaded.emit()


class LocalStorageManager(QObject):...
