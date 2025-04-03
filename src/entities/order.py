from src.constants import OrderStatus, OrderPriority


class Order:
	def __init__(self, id: int, type: str, amount: float, flag: bool):
		self.id = id
		self.type = type
		self.amount = amount
		self.flag = flag
		self.status = None
		self.priority = OrderPriority.LOW.value
