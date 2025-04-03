import pytest
import os
from unittest.mock import Mock, patch, mock_open, ANY
from src.services.order_processing import OrderProcessingService
from src.services.api_client import APIClient
from src.constants import OrderType, OrderStatus, Thresholds, CSVHeaders
from tests.factories.order import OrderFactory

class TestProcessTypeAOrder:
    @pytest.fixture
    def mock_api_client(self):
        return Mock(spec=APIClient)

    @pytest.fixture
    def order_processing_service(self, mock_api_client):
        return OrderProcessingService(mock_api_client)

    def test_should_create_csv_file_successfully_when_all_data_is_valid(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify CSV headers were written
            handle.write.assert_any_call(ANY)
            write_calls = handle.write.call_args_list
            assert len(write_calls) >= 2  # At least headers and data
            assert write_calls[0][0][0].startswith('ID,Type,Amount,Flag,Status,Priority')

    def test_should_add_high_value_note_when_amount_exceeds_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_VALUE_ORDER + 1)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was written
            write_calls = handle.write.call_args_list
            assert any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_not_add_high_value_note_when_amount_below_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_VALUE_ORDER - 1)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was not written
            write_calls = handle.write.call_args_list
            assert not any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_set_export_failed_status_when_file_system_error_occurs(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=1000)
        mock_file = mock_open()
        mock_file.side_effect = IOError("File system error")

        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORT_FAILED.value
            mock_file.assert_called_once()

    def test_should_set_export_failed_status_when_csv_writing_fails(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=1000)
        mock_file = mock_open()
        mock_file.return_value.__enter__().write.side_effect = IOError("CSV writing error")

        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORT_FAILED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            assert handle.write.called

    def test_should_handle_invalid_order_data_gracefully(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1)
        order.amount = None  # Invalid data
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value

    def test_should_handle_amount_exactly_at_high_value_threshold(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=Thresholds.HIGH_VALUE_ORDER)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was NOT written
            write_calls = handle.write.call_args_list
            assert not any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_handle_maximum_allowed_amount(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=float('inf'))
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was written
            write_calls = handle.write.call_args_list
            assert any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_handle_minimum_allowed_amount(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=float('-inf'))
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was not written
            write_calls = handle.write.call_args_list
            assert not any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_handle_zero_amount(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=0)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was not written
            write_calls = handle.write.call_args_list
            assert not any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_handle_negative_amount(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=-100)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify high value note was not written
            write_calls = handle.write.call_args_list
            assert not any('Note,High value order' in call[0][0] for call in write_calls)

    def test_should_handle_decimal_amount_values(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1, amount=100.50)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify order data was written with decimal amount
            write_calls = handle.write.call_args_list
            assert any('100.5' in call[0][0] for call in write_calls)

    def test_should_write_csv_headers_correctly(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(id=1)
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify CSV headers were written first
            write_calls = handle.write.call_args_list
            assert write_calls[0][0][0].startswith('ID,Type,Amount,Flag,Status,Priority')

    def test_should_write_order_details_to_csv_correctly(self, order_processing_service):
        # Arrange
        user_id = 1
        order = OrderFactory.create_type_a_order(
            id=1,
            amount=1000,
            flag=True,
            status=OrderStatus.PENDING.value,
            priority="HIGH"
        )
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            # Act
            result = order_processing_service._process_type_a_order(order, user_id)

            # Assert
            assert result.status == OrderStatus.EXPORTED.value
            mock_file.assert_called_once()
            handle = mock_file.return_value.__enter__()
            
            # Verify order details were written correctly with original status
            write_calls = handle.write.call_args_list
            order_data = write_calls[1][0][0].strip()  # Second write call contains order data
            expected_data = f"{order.id},{order.type},{order.amount},{str(order.flag).lower()},{OrderStatus.PENDING.value},{order.priority}"
            assert order_data == expected_data 