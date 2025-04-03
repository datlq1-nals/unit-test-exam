import pytest
from unittest.mock import Mock, patch
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus, APIResponseStatus
from src.utils.response import APIResponse
from tests.factories.order import OrderFactory

class TestHandleAPIResponse:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_process_successfully_when_api_response_is_successful(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1, amount=50.0)
        api_response = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=100
        )

        # Act
        result = order_processing_service._handle_api_response(order, api_response)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value

    def test_should_set_api_error_status_when_api_response_fails(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = APIResponse(
            status=APIResponseStatus.ERROR.value,
            data=None
        )

        # Act
        result = order_processing_service._handle_api_response(order, api_response)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value

    def test_should_handle_invalid_response_data_gracefully(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data="invalid_data"
        )

        # Act & Assert
        with pytest.raises(ValueError):
            order_processing_service._handle_api_response(order, api_response)

    def test_should_handle_null_api_response(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = None

        # Act
        result = order_processing_service._handle_api_response(order, api_response)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value

    def test_should_handle_empty_api_response(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=""
        )

        # Act & Assert
        with pytest.raises(ValueError):
            order_processing_service._handle_api_response(order, api_response)

    def test_should_handle_malformed_api_response(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = APIResponse(
            status="UNKNOWN_STATUS",
            data=None
        )

        # Act
        result = order_processing_service._handle_api_response(order, api_response)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value
        
    def test_should_handle_api_response_with_success_status_but_no_data(self, order_processing_service):
        # Arrange
        order = OrderFactory.create_type_b_order(id=1)
        api_response = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=None
        )

        # Act & Assert
        with pytest.raises(TypeError):
            order_processing_service._handle_api_response(order, api_response) 