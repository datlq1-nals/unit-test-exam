from typing import Any


class APIResponse:
	def __init__(self, status: str, data: Any):
		self.status = status
		self.data = data

