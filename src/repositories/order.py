from typing import List

from src.entities.order import Order


class OrderRepository:
	@staticmethod
	def get_orders_by_user(self, user_id: int) -> List[Order]:
		pass

	@staticmethod
	def update_order_status(self, order_id: int, status: str, priority: str) -> bool:
		pass

	@staticmethod
	def bulk_update_orders(self, orders: List[Order]) -> bool:
		"""
		Update multiple orders in the database in a single transaction.
		
		Args:
			orders: List of Order objects to update
			
		Returns:
			bool: True if all updates were successful, False otherwise
			
		Raises:
			DatabaseException: If database operation fails
		"""
		pass
