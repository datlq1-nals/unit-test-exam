from abc import ABC, abstractmethod

from src.utils.response import APIResponse


class APIClient(ABC):
	@abstractmethod
	def call_api(self, order_id: int) -> APIResponse:
		pass

