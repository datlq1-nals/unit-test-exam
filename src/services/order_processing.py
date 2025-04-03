import csv
import time

from typing import Any

from src.constants import (
	OrderType,
	OrderStatus,
	OrderPriority,
	Thresholds,
	CSVHeaders,
	APIResponseStatus
)
from src.utils.exceptions import APIException, DatabaseException
from src.utils.response import APIResponse
from src.services.api_client import APIClient
from src.entities.order import Order
from src.repositories.order import OrderRepository

class OrderProcessingService:
	def __init__(self, api_client: APIClient):
		self.api_client = api_client
		self.order_repository = OrderRepository()

	def process_orders(self, user_id: int) -> bool:
		try:
			orders = self.order_repository.get_orders_by_user(user_id)

			if not orders:
				return False

			processed_orders = []
			for order in orders:
				processed_order = self._process_single_order(order, user_id)
				processed_orders.append(processed_order)

			# Bulk update all processed orders
			try:
				self.order_repository.bulk_update_orders(processed_orders)
			except DatabaseException:
				# If bulk update fails, mark all orders as having DB error
				for order in processed_orders:
					order.status = OrderStatus.DB_ERROR.value
				return False

			return True
		except Exception:
			return False
		
	def _create_csv_file_name(self, user_id: int, order_type: str) -> str:
		"""
		Create a csv file name with type of order and user id
		Args:
			user_id(int): User ID
			order_type(str): Type of order

		Returns:
			str: csv file name
		"""
		if not order_type:
			raise ValueError("Order type cannot be empty")
		
		return f"orders_type_{order_type}_{user_id}_{int(time.time())}.csv"

	def _process_single_order(self, order: Order, user_id: int) -> Order:
		order = self._process_order_by_type(order, user_id)
		order = self._update_order_priority(order)
		
		return order

	def _process_order_by_type(self, order: Order, user_id: int) -> Order:
		# Normalize order type by trimming whitespace and converting to uppercase
		order_type = order.type.strip().upper()
		
		if order_type == OrderType.TYPE_A.value:
			self._process_type_a_order(order, user_id)
		elif order_type == OrderType.TYPE_B.value:
			self._process_type_b_order(order)
		elif order_type == OrderType.TYPE_C.value:
			self._process_type_c_order(order)
		else:
			order.status = OrderStatus.UNKNOWN_TYPE.value

		return order

	def _process_type_a_order(self, order: Order, user_id: int) -> Order:
		try:
			# Initialize CSV file for Type A orders
			csv_filename = self._create_csv_file_name(user_id, OrderType.TYPE_A.value)
			with open(csv_filename, "w", newline="") as csv_file:
				csv_writer = csv.writer(csv_file)

				# Write CSV headers
				csv_writer.writerow(CSVHeaders.HEADERS)

				# Write order to CSV
				csv_writer.writerow([
					order.id,
					order.type,
					order.amount,
					str(order.flag).lower(),
					order.status,
					order.priority
				])

				# Add high value note if applicable
				if order.amount and order.amount > Thresholds.HIGH_VALUE_ORDER:
					csv_writer.writerow(CSVHeaders.HIGH_VALUE_NOTE)

			order.status = OrderStatus.EXPORTED.value
		except IOError:
			order.status = OrderStatus.EXPORT_FAILED.value
		
		return order

	def _process_type_b_order(self, order: Order) -> Order:
		try:
			api_response = self.api_client.call_api(order.id)
			order = self._handle_api_response(order, api_response)
		except Exception:
			order.status = OrderStatus.API_FAILURE.value

		return order

	def _process_type_c_order(self, order: Order) -> Order:
		order.status = (
			OrderStatus.COMPLETED.value if order.flag 
			else OrderStatus.IN_PROGRESS.value
		)

		return order

	def _handle_api_response(self, order: Order, api_response: APIResponse) -> Order:
		if api_response and api_response.status.lower() == APIResponseStatus.SUCCESS.value:
			order = self._handle_successful_api_response(order, float(api_response.data))
		else:
			order.status = OrderStatus.API_ERROR.value

		return order

	def _handle_successful_api_response(self, order: Order, api_data: float) -> Order:
		if order.flag:
			order.status = OrderStatus.PENDING.value
		elif api_data >= Thresholds.API_SUCCESS_THRESHOLD and order.amount < Thresholds.API_AMOUNT_THRESHOLD:
			order.status = OrderStatus.PROCESSED.value
		elif api_data < Thresholds.API_SUCCESS_THRESHOLD:
			order.status = OrderStatus.PENDING.value
		else:
			order.status = OrderStatus.ERROR.value
		
		return order

	def _update_order_priority(self, order: Order) -> Order:
		order.priority = (
			OrderPriority.HIGH.value if order.amount > Thresholds.HIGH_PRIORITY_ORDER
			else OrderPriority.LOW.value
		)

		return order
