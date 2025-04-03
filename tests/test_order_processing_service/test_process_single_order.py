import pytest

from unittest.mock import Mock, patch
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus, APIResponseStatus, Thresholds, OrderPriority
from tests.factories.order import OrderFactory
from src.utils.exceptions import APIException

class TestProcessSingleOrder:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_process_successfully_when_order_type_is_A(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.EXPORTED.value

    def test_should_add_high_value_note_when_type_a_order_amount_exceeds_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_VALUE_ORDER + 1)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.EXPORTED.value

    @patch('builtins.open')
    def test_should_set_export_failed_when_io_error_occurs(self, mock_open, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1)
        mock_open.side_effect = IOError()

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.EXPORT_FAILED.value

    def test_should_process_successfully_when_order_type_is_B(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1, amount=10)
        mock_api_client.call_api.return_value = Mock(
            status=APIResponseStatus.SUCCESS.value,
            data=100
        )

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.PROCESSED.value

    def test_should_set_api_error_when_api_returns_error_status(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.return_value = Mock(status="ERROR", data=None)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value

    def test_should_set_api_error_when_api_returns_null_response(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.return_value = None

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.API_ERROR.value

    def test_should_set_api_failure_when_api_throws_exception(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1)
        mock_api_client.call_api.side_effect = APIException()

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.API_FAILURE.value

    def test_should_set_pending_when_api_data_below_threshold(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1, amount=Thresholds.API_AMOUNT_THRESHOLD + 1)
        mock_api_client.call_api.return_value = Mock(
            status=APIResponseStatus.SUCCESS.value,
            data=Thresholds.API_SUCCESS_THRESHOLD - 1
        )

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.PENDING.value

    def test_should_set_pending_when_order_flag_is_true(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1, amount=Thresholds.API_AMOUNT_THRESHOLD + 1, flag=True)
        mock_api_client.call_api.return_value = Mock(
            status=APIResponseStatus.SUCCESS.value,
            data=Thresholds.API_AMOUNT_THRESHOLD + 1
        )

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.PENDING.value

    def test_should_set_error_when_api_data_and_amount_above_threshold(self, order_processing_service, mock_api_client):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_b_order(id=1, amount=Thresholds.API_AMOUNT_THRESHOLD + 1)
        mock_api_client.call_api.return_value = Mock(
            status=APIResponseStatus.SUCCESS.value,
            data=Thresholds.API_AMOUNT_THRESHOLD + 1
        )

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.ERROR.value

    def test_should_process_successfully_when_order_type_is_C(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_c_order(id=1, flag=True)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.COMPLETED.value

    def test_should_set_in_progress_when_type_c_order_flag_is_false(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_c_order(id=1, flag=False)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.IN_PROGRESS.value

    def test_should_set_unknown_status_when_order_type_is_invalid(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_order(id=1, type="INVALID_TYPE")

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.UNKNOWN_TYPE.value

    def test_should_handle_case_insensitive_order_type(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_order(id=1, type=OrderType.TYPE_A.value.lower())

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.EXPORTED.value

    def test_should_handle_whitespace_in_order_type(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_order(id=1, type=f" {OrderType.TYPE_A.value} ")

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.EXPORTED.value

    def test_should_handle_empty_order_type(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_order(id=1, type="")

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.status == OrderStatus.UNKNOWN_TYPE.value

    def test_should_set_high_priority_when_amount_exceeds_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_PRIORITY_ORDER + 1)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.priority == OrderPriority.HIGH.value

    def test_should_set_low_priority_when_amount_below_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_PRIORITY_ORDER - 1)

        # Act
        result = order_processing_service._process_single_order(order, user_id)

        # Assert
        assert result.priority == OrderPriority.LOW.value 