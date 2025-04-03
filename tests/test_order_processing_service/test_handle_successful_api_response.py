import pytest
from unittest.mock import Mock, patch
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus, Thresholds
from tests.factories.order import OrderFactory

class TestHandleSuccessfulAPIResponse:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_set_processed_status_when_api_data_above_threshold_and_amount_below_threshold(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1, 
            amount=Thresholds.API_AMOUNT_THRESHOLD - 1,  # amount below threshold
            flag=False  # flag must be False to get PROCESSED status
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD + 1

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value

    def test_should_set_pending_status_when_api_data_below_threshold(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD - 1,  # amount below threshold
            flag=False  # flag must be False to test api_data condition
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD - 1

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PENDING.value

    def test_should_set_pending_status_when_flag_is_true(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD - 1,  # amount below threshold
            flag=True  # flag is True, should always return PENDING
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD + 1

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PENDING.value

    def test_should_set_error_status_when_all_conditions_are_false(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD + 1,  # amount above threshold
            flag=False  # flag must be False to get ERROR status
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD + 1  # api_data above threshold

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.ERROR.value

    def test_should_handle_api_data_exactly_at_threshold(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD - 1,  # amount below threshold
            flag=False  # flag must be False to get PROCESSED status
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD  # api_data at threshold

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value

    def test_should_handle_amount_exactly_at_threshold(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD,  # amount at threshold
            flag=False  # flag must be False to get ERROR status
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD + 1

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.ERROR.value

    def test_should_handle_both_values_at_threshold(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(
            id=1,
            amount=Thresholds.API_AMOUNT_THRESHOLD,  # amount at threshold
            flag=False  # flag must be False to get ERROR status
        )
        api_data = Thresholds.API_SUCCESS_THRESHOLD  # api_data at threshold

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.ERROR.value

    def test_should_handle_maximum_api_data_value(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50)
        api_data = float('inf')

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value

    def test_should_handle_minimum_api_data_value(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_data = float('-inf')

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PENDING.value

    def test_should_handle_zero_api_data_value(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_data = 0

        # Act
        result = order_processing_service._handle_successful_api_response(order, api_data)

        # Assert
        assert result.status == OrderStatus.PENDING.value 