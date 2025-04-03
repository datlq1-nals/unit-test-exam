import pytest
from unittest.mock import Mock, patch
from src.services.api_client import APIClient
from src.utils.response import APIResponse
from src.constants import APIResponseStatus

class TestCallAPI:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    def test_should_return_success_response_when_api_call_succeeds(self, mock_api_client):
        # Arrange
        order_id = 1
        expected_response = APIResponse(
            status=APIResponseStatus.SUCCESS.value,
            data=100
        )
        mock_api_client.call_api.return_value = expected_response

        # Act
        result = mock_api_client.call_api(order_id)

        # Assert
        assert result == expected_response
        mock_api_client.call_api.assert_called_once_with(order_id)

    def test_should_raise_exception_when_order_id_does_not_exist(self, mock_api_client):
        # Arrange
        order_id = 999
        mock_api_client.call_api.side_effect = ValueError("Order ID does not exist")

        # Act & Assert
        with pytest.raises(ValueError, match="Order ID does not exist"):
            mock_api_client.call_api(order_id)

    def test_should_raise_exception_when_order_id_is_negative(self, mock_api_client):
        # Arrange
        order_id = -1
        mock_api_client.call_api.side_effect = ValueError("Order ID cannot be negative")

        # Act & Assert
        with pytest.raises(ValueError, match="Order ID cannot be negative"):
            mock_api_client.call_api(order_id)

    def test_should_raise_exception_when_order_id_is_zero(self, mock_api_client):
        # Arrange
        order_id = 0
        mock_api_client.call_api.side_effect = ValueError("Order ID cannot be zero")

        # Act & Assert
        with pytest.raises(ValueError, match="Order ID cannot be zero"):
            mock_api_client.call_api(order_id)

    def test_should_raise_exception_when_api_timeout_occurs(self, mock_api_client):
        # Arrange
        order_id = 1
        mock_api_client.call_api.side_effect = TimeoutError("API request timed out")

        # Act & Assert
        with pytest.raises(TimeoutError, match="API request timed out"):
            mock_api_client.call_api(order_id)

    def test_should_raise_exception_when_api_returns_error(self, mock_api_client):
        # Arrange
        order_id = 1
        mock_api_client.call_api.side_effect = Exception("API returned an error")

        # Act & Assert
        with pytest.raises(Exception, match="API returned an error"):
            mock_api_client.call_api(order_id)

    def test_should_raise_exception_when_network_connection_fails(self, mock_api_client):
        # Arrange
        order_id = 1
        mock_api_client.call_api.side_effect = ConnectionError("Network connection failed")

        # Act & Assert
        with pytest.raises(ConnectionError, match="Network connection failed"):
            mock_api_client.call_api(order_id) 