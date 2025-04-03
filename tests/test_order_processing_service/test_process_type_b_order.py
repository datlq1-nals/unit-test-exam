import pytest
from unittest.mock import Mock, patch
from src.services.order_processing import OrderProcessingService
from src.repositories.order import OrderRepository
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus, Thresholds, APIResponseStatus
from src.utils.response import APIResponse
from tests.factories.order import OrderFactory

class TestProcessTypeBOrder:
    @pytest.fixture
    def mock_db_service(self):
        return Mock(spec=OrderRepository)

    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_process_successfully_when_api_call_succeeds(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.return_value = APIResponse(
            status="SUCCESS",
            data=100
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_set_api_failure_status_when_api_exception_occurs(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.side_effect = Exception("API error")

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.API_FAILURE.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_different_api_response_statuses_correctly(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.return_value = APIResponse(
            status="ERROR",
            data=None
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_different_api_response_data_values_correctly(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=150.0)  # Above API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=50
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.ERROR.value  # When amount > API_AMOUNT_THRESHOLD, status should be ERROR
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_api_response_at_success_threshold(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=Thresholds.API_SUCCESS_THRESHOLD
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value  # When api_data >= API_SUCCESS_THRESHOLD and amount < API_AMOUNT_THRESHOLD, status should be PROCESSED
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_api_response_just_below_success_threshold(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=Thresholds.API_SUCCESS_THRESHOLD - 1
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PENDING.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_maximum_api_response_value(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=float('inf')
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_minimum_api_response_value(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=float('-inf')
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PENDING.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_zero_api_response_value(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=0
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PENDING.value
        mock_api_client.call_api.assert_called_once_with(order.id)

    def test_should_handle_negative_api_response_value(self, order_processing_service, mock_api_client):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)  # Below API_AMOUNT_THRESHOLD
        mock_api_client.call_api.return_value = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=-100
        )

        # Act
        result = order_processing_service._process_type_b_order(order)

        # Assert
        assert result.status == OrderStatus.PENDING.value
        mock_api_client.call_api.assert_called_once_with(order.id) 