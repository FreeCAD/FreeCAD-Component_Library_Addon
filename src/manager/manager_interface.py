from typing import Any

from PySide6.QtCore import Signal, Slot
from PySide6.QtNetwork import QNetworkRequest

from ..api import ApiInterface, CMSApi, CMSReply, ComponentRequest, getApi
from ..data import Component, DTypes, FileTypes
from ..utils import ABCQObject
from .downloader import FileDownloader
from .page import PageStates
from .query import ComponentQueryInterface, RepoComponentQuery


class ManagerInterface(ABCQObject):
	component_loaded: Signal

	api: ApiInterface
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
		# ? make ENums for by and order
		raise NotImplementedError

	def filter(self,/ , filetypes: list[str], tags: list[str]):
		# ? replace typehint of filetypes & tags with enum
		raise NotImplementedError



class OnlineRepoManager(ManagerInterface):
	component_loaded = Signal()

	query: RepoComponentQuery = RepoComponentQuery()
	page_states = PageStates()
	DOWNLOAD_PATH = "test/downloads"

	def __init__(self, api_url: str) -> None:
		super().__init__()
		self.api: CMSApi = getApi(api_url)

	def reload_page(self) -> CMSReply:
		self.query.page = 1
		return self.request_components()

	def next_page(self) -> CMSReply:
		self.query.page = self.page_states.next_page
		return self.request_components()

	def prev_page(self) -> CMSReply:
		self.query.page = self.page_states.prev_page
		return self.request_components()

	def search(self, search_key: str) -> CMSReply:
		self.query.search_key = search_key
		return self.reload_page()

	def sort(self, /, by: str, order: str) -> CMSReply:
		self.query.sort_by = by
		self.query.sort_ord = order
		return self.reload_page()

	def filter(self,/ , filetypes: list[str], tags: list[str]) -> CMSReply:
		self.query.file_types = filetypes
		self.query.tags = tags
		return self.reload_page()


	def download_component(self, component: Component, filetype: FileTypes) -> FileDownloader:
		file = component.files.get(filetype)
		if file is None:
			raise FileNotFoundError()
		return FileDownloader(file.url, self.DOWNLOAD_PATH, f"{component.metadata.name}.{file.type.value}")


	def request_components(self) -> CMSReply:
		reply: CMSReply = self.api.read(ComponentRequest(self.query))
		reply.finished.connect(self.__component_response_handler)
		return reply


	@Slot(dict)
	def __component_response_handler(self, json_data: dict[str, Any]):
		page: PageStates = self.page_states.load_page(json_data)
		self.query.page = page.page_no
		self.query.page_size = page.size
		self.component_loaded.emit()


class LocalStorageManager(ManagerInterface):...
