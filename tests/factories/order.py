import random
from typing import Optional
from faker import Faker

from src.entities.order import Order
from src.constants import OrderType, OrderStatus, OrderPriority


fake = Faker()


class OrderFactory:
    @staticmethod
    def create_order(
        id: int = 1,
        type: str = OrderType.TYPE_A.value,
        amount: float = 100.0,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        order = Order(
            id=id,
            type=type,
            amount=amount,
            flag=flag
        )
        if status is not None:
            order.status = status
        order.priority = priority
        
        return order

    @staticmethod
    def create_type_a_order(
        id: int = 1,
        amount: float = 100.0,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=OrderType.TYPE_A.value,
            amount=amount,
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_type_b_order(
        id: int = 1,
        amount: float = 50.0,  # Lower than API_AMOUNT_THRESHOLD
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=OrderType.TYPE_B.value,
            amount=amount,
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_type_c_order(
        id: int = 1,
        amount: float = 100.0,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=OrderType.TYPE_C.value,
            amount=amount,
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_high_value_order(
        id: int = 1,
        type: str = OrderType.TYPE_A.value,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=type,
            amount=1000000.0,  # High value amount
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_low_value_order(
        id: int = 1,
        type: str = OrderType.TYPE_A.value,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=type,
            amount=10.0,  # Low value amount
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_zero_amount_order(
        id: int = 1,
        type: str = OrderType.TYPE_A.value,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=type,
            amount=0.0,
            flag=flag,
            status=status,
            priority=priority
        )

    @staticmethod
    def create_negative_amount_order(
        id: int = 1,
        type: str = OrderType.TYPE_A.value,
        flag: bool = False,
        status: str = None,
        priority: str = OrderPriority.LOW.value
    ) -> Order:
        return OrderFactory.create_order(
            id=id,
            type=type,
            amount=-100.0,
            flag=flag,
            status=status,
            priority=priority
        ) 