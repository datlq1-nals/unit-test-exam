import pytest
from unittest.mock import Mock, patch
from src.services.order_processing import OrderProcessingService
from src.repositories.order import OrderRepository
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus
from tests.factories.order import OrderFactory

class TestProcessTypeCOrder:
    @pytest.fixture
    def mock_db_service(self):
        return Mock(spec=OrderRepository)

    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_set_completed_status_when_flag_is_true(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_c_order(id=1, flag=True)

        # Act
        result = order_processing_service._process_type_c_order(order)

        # Assert
        assert result.status == OrderStatus.COMPLETED.value

    def test_should_set_in_progress_status_when_flag_is_false(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_c_order(id=1, flag=False)

        # Act
        result = order_processing_service._process_type_c_order(order)

        # Assert
        assert result.status == OrderStatus.IN_PROGRESS.value

    def test_should_handle_flag_transition_from_true_to_false(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_c_order(id=1, flag=True)
        order_processing_service._process_type_c_order(order)  # First process with flag=True
        order.flag = False  # Change flag to False

        # Act
        result = order_processing_service._process_type_c_order(order)

        # Assert
        assert result.status == OrderStatus.IN_PROGRESS.value

    def test_should_handle_flag_transition_from_false_to_true(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_c_order(id=1, flag=False)
        order_processing_service._process_type_c_order(order)  # First process with flag=False
        order.flag = True  # Change flag to True

        # Act
        result = order_processing_service._process_type_c_order(order)

        # Assert
        assert result.status == OrderStatus.COMPLETED.value

    def test_should_handle_flag_changes_without_affecting_other_orders(self, order_processing_service):
        # Arrange
        order1 = OrderFactory.create_type_c_order(id=1, flag=True)
        order2 = OrderFactory.create_type_c_order(id=2, flag=False)
        
        # Act
        result1 = order_processing_service._process_type_c_order(order1)
        result2 = order_processing_service._process_type_c_order(order2)

        # Assert
        assert result1.status == OrderStatus.COMPLETED.value
        assert result2.status == OrderStatus.IN_PROGRESS.value 