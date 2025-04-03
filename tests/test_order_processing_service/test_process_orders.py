import pytest
from unittest.mock import Mock, patch, ANY
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus
from src.utils.exceptions import DatabaseException, APIException
from tests.factories.order import OrderFactory

class TestProcessOrders:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_process_all_orders_successfully_when_multiple_orders_exist(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [
            OrderFactory.create_type_a_order(id=1),
            OrderFactory.create_type_b_order(id=2),
            OrderFactory.create_type_c_order(id=3)
        ]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True
            mock_bulk_update.assert_called_once_with(orders)

    def test_should_return_false_when_user_has_no_orders(self, order_processing_service):
        # Arrange
        user_id = 1
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=None):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False

    def test_should_return_false_when_database_service_fails(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [OrderFactory.create_type_a_order(id=1)]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders', side_effect=DatabaseException):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False
            assert all(order.status == OrderStatus.DB_ERROR.value for order in orders)

    def test_should_return_false_when_user_id_is_invalid(self, order_processing_service):
        # Arrange
        user_id = -1
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=None):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False

    def test_should_return_false_when_order_list_is_empty(self, order_processing_service):
        # Arrange
        user_id = 1
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=[]):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False

    def test_should_process_successfully_when_order_list_has_maximum_allowed_orders(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [OrderFactory.create_type_a_order(id=i) for i in range(1000)]  # Assuming 1000 is max
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True
            mock_bulk_update.assert_called_once_with(orders)

    def test_should_handle_mixed_order_types_in_single_batch(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [
            OrderFactory.create_type_a_order(id=1),
            OrderFactory.create_type_b_order(id=2),
            OrderFactory.create_type_c_order(id=3)
        ]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True
            mock_bulk_update.assert_called_once_with(orders)
            assert orders[0].status == OrderStatus.EXPORTED.value
            assert orders[1].status in [OrderStatus.PROCESSED.value, OrderStatus.PENDING.value, OrderStatus.ERROR.value, OrderStatus.API_ERROR.value]
            assert orders[2].status in [OrderStatus.COMPLETED.value, OrderStatus.IN_PROGRESS.value]

    def test_should_continue_processing_when_single_order_fails(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [
            OrderFactory.create_type_a_order(id=1),
            OrderFactory.create_type_b_order(id=2, amount=50),  # Use valid amount but make API call fail
            OrderFactory.create_type_c_order(id=3)
        ]
        
        # Mock the api_client to fail for order id 2
        def mock_call_api(order_id):
            if order_id == 2:
                raise APIException("API Error")
            return Mock(status="success", data="100")

        order_processing_service.api_client.call_api.side_effect = mock_call_api
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True  # Process should continue even if one order fails
            mock_bulk_update.assert_called_once_with(orders)
            assert orders[0].status == OrderStatus.EXPORTED.value
            assert orders[1].status == OrderStatus.API_FAILURE.value  # Should be API_FAILURE due to APIException
            assert orders[2].status in [OrderStatus.COMPLETED.value, OrderStatus.IN_PROGRESS.value]

    def test_should_perform_bulk_update_successfully(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [OrderFactory.create_type_a_order(id=1)]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True
            mock_bulk_update.assert_called_once_with(orders)

    def test_should_handle_bulk_update_failure_gracefully(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [OrderFactory.create_type_a_order(id=1)]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders', side_effect=DatabaseException):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False
            assert all(order.status == OrderStatus.DB_ERROR.value for order in orders)

    def test_should_mark_all_orders_as_db_error_when_bulk_update_fails(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [
            OrderFactory.create_type_a_order(id=1),
            OrderFactory.create_type_b_order(id=2),
            OrderFactory.create_type_c_order(id=3)
        ]
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders', side_effect=DatabaseException):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False
            assert all(order.status == OrderStatus.DB_ERROR.value for order in orders)

    def test_should_process_orders_in_correct_sequence(self, order_processing_service):
        # Arrange
        user_id = 1
        orders = [
            OrderFactory.create_type_a_order(id=1),
            OrderFactory.create_type_b_order(id=2),
            OrderFactory.create_type_c_order(id=3)
        ]
        processed_orders = []
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=orders), \
             patch('src.repositories.order.OrderRepository.bulk_update_orders') as mock_bulk_update:
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is True
            mock_bulk_update.assert_called_once()
            assert mock_bulk_update.call_args[0][0] == orders  # Verify order sequence is maintained

    def test_should_handle_empty_order_list_after_processing(self, order_processing_service):
        # Arrange
        user_id = 1
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', return_value=[]):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False

    def test_should_return_false_when_any_exception_occurs(self, order_processing_service):
        # Arrange
        user_id = 1
        
        with patch('src.repositories.order.OrderRepository.get_orders_by_user', side_effect=Exception):
            # Act
            result = order_processing_service.process_orders(user_id)

            # Assert
            assert result is False 