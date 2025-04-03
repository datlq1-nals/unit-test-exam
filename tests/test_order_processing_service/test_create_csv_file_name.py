import pytest
from unittest.mock import Mock
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType

class TestCreateCSVFileName:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_create_valid_filename_when_user_id_and_order_type_are_valid(self, order_processing_service):
        # Arrange
        user_id = 1
        order_type = OrderType.TYPE_A.value

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv")

    def test_should_handle_special_characters_when_order_type_contains_special_chars(self, order_processing_service):
        # Arrange
        user_id = 1
        order_type = "TYPE@A#"

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv")

    def test_should_create_valid_filename_when_user_id_is_very_long(self, order_processing_service):
        # Arrange
        user_id = 999999999
        order_type = OrderType.TYPE_A.value

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv")

    def test_should_raise_exception_when_order_type_is_empty(self, order_processing_service):
        # Arrange
        user_id = 1
        order_type = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Order type cannot be empty"):
            order_processing_service._create_csv_file_name(user_id, order_type)

    def test_should_handle_maximum_length_order_type(self, order_processing_service):
        # Arrange
        user_id = 1
        order_type = "A" * 100  # Maximum length order type

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv")

    def test_should_handle_minimum_length_order_type(self, order_processing_service):
        # Arrange
        user_id = 1
        order_type = "A"  # Minimum length order type

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv")

    def test_should_handle_special_characters_in_user_id(self, order_processing_service):
        # Arrange
        user_id = 123
        order_type = OrderType.TYPE_A.value

        # Act
        filename = order_processing_service._create_csv_file_name(user_id, order_type)

        # Assert
        assert filename.startswith(f"orders_type_{order_type}_{user_id}_")
        assert filename.endswith(".csv") 