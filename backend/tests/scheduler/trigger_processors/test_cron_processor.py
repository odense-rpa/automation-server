"""
Tests for CronTriggerProcessor.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.scheduler.trigger_processors.cron import CronTriggerProcessor
from app.scheduler.trigger_processors.base import ProcessingServices


class TestCronTriggerProcessor:
    """Tests for CronTriggerProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock services
        self.mock_services = MagicMock(spec=ProcessingServices)
        self.processor = CronTriggerProcessor(self.mock_services)
    
    def create_mock_trigger(self, cron_expr="0 0 * * *", process_id=1, parameters=""):
        """Helper to create mock trigger."""
        trigger = MagicMock()
        trigger.id = 1
        trigger.cron = cron_expr
        trigger.process_id = process_id
        trigger.parameters = parameters
        return trigger
    
    @patch('app.scheduler.trigger_processors.cron.CronSim')
    @patch('app.scheduler.trigger_processors.cron.validate_cron_expression')
    def test_process_trigger_time_to_trigger(self, mock_validate, mock_cronsim):
        """Test processing when it's time to trigger."""
        # Setup mocks
        mock_validate.return_value = "0 0 * * *"
        mock_iterator = mock_cronsim.return_value
        now = datetime(2023, 1, 1, 0, 0, 0)
        mock_iterator.__next__.return_value = now  # Next scheduled time matches current time
        
        trigger = self.create_mock_trigger()
        
        # Mock the session creation
        with patch.object(self.processor, '_create_session', return_value=True) as mock_create:
            result = self.processor._process_trigger(trigger, "validated_params", now)
        
        # Verify results
        assert result is True
        mock_validate.assert_called_once_with("0 0 * * *")
        # CronSim is called with one minute before the current time
        expected_start_time = now - timedelta(minutes=1)
        mock_cronsim.assert_called_once_with("0 0 * * *", expected_start_time)
        mock_create.assert_called_once_with(trigger, "validated_params")
    
    @patch('app.scheduler.trigger_processors.cron.CronSim')
    @patch('app.scheduler.trigger_processors.cron.validate_cron_expression')
    def test_process_trigger_not_time_to_trigger(self, mock_validate, mock_cronsim):
        """Test processing when it's not time to trigger."""
        # Setup mocks
        mock_validate.return_value = "0 0 * * *"
        mock_iterator = mock_cronsim.return_value
        now = datetime(2023, 1, 1, 1, 0, 0)  # Not midnight
        next_time = datetime(2023, 1, 2, 0, 0, 0)  # Next scheduled time is tomorrow midnight
        mock_iterator.__next__.return_value = next_time
        
        trigger = self.create_mock_trigger()
        
        # Mock the session creation (should not be called)
        with patch.object(self.processor, '_create_session') as mock_create:
            result = self.processor._process_trigger(trigger, "validated_params", now)
        
        # Verify results
        assert result is True  # Still successful, just not triggered
        mock_validate.assert_called_once_with("0 0 * * *")
        # CronSim is called with one minute before the current time
        expected_start_time = now - timedelta(minutes=1)
        mock_cronsim.assert_called_once_with("0 0 * * *", expected_start_time)
        mock_create.assert_not_called()
    
    @patch('app.scheduler.trigger_processors.cron.validate_cron_expression')
    def test_process_trigger_invalid_cron(self, mock_validate):
        """Test processing with invalid cron expression."""
        # Setup mock to raise validation error
        mock_validate.side_effect = ValueError("Invalid cron expression")
        
        trigger = self.create_mock_trigger(cron_expr="invalid")
        now = datetime(2023, 1, 1, 0, 0, 0)
        
        with patch('app.scheduler.trigger_processors.cron.logger') as mock_logger:
            result = self.processor._process_trigger(trigger, "validated_params", now)
        
        # Verify results
        assert result is False
        mock_validate.assert_called_once_with("invalid")
        mock_logger.error.assert_called_once()
    
    @patch('app.scheduler.trigger_processors.cron.CronSim')
    @patch('app.scheduler.trigger_processors.cron.validate_cron_expression')
    def test_process_trigger_session_creation_failure(self, mock_validate, mock_cronsim):
        """Test processing when session creation fails."""
        # Setup mocks
        mock_validate.return_value = "0 0 * * *"
        mock_iterator = mock_cronsim.return_value
        now = datetime(2023, 1, 1, 0, 0, 0)
        mock_iterator.__next__.return_value = now  # Next scheduled time matches current time
        
        trigger = self.create_mock_trigger()
        
        # Mock session creation to fail
        with patch.object(self.processor, '_create_session', return_value=False) as mock_create:
            result = self.processor._process_trigger(trigger, "validated_params", now)
        
        # Verify results
        assert result is False
        mock_create.assert_called_once_with(trigger, "validated_params")
    
    @patch('app.scheduler.trigger_processors.cron.CronSim')
    @patch('app.scheduler.trigger_processors.cron.validate_cron_expression')
    def test_process_trigger_cronsim_exception(self, mock_validate, mock_cronsim):
        """Test processing when CronSim raises exception."""
        # Setup mocks
        mock_validate.return_value = "0 0 * * *"
        mock_cronsim.side_effect = Exception("CronSim error")
        
        trigger = self.create_mock_trigger()
        now = datetime(2023, 1, 1, 0, 0, 0)
        
        with patch('app.scheduler.trigger_processors.cron.logger') as mock_logger:
            result = self.processor._process_trigger(trigger, "validated_params", now)
        
        # Verify results
        assert result is False
        mock_logger.error.assert_called_once()
    
    def test_process_trigger_common_cron_expressions(self):
        """Test processing with real cron expressions and timestamps."""
        test_cases = [
            ("0 0 * * *", datetime(2023, 1, 1, 0, 0, 0), True),   # Daily at midnight - match
            ("0 0 * * *", datetime(2023, 1, 1, 1, 0, 0), False),  # Daily at midnight - no match
            ("*/5 * * * *", datetime(2023, 1, 1, 0, 5, 0), True), # Every 5 minutes - match
            ("*/5 * * * *", datetime(2023, 1, 1, 0, 3, 0), False), # Every 5 minutes - no match
            ("0 9 * * 1", datetime(2023, 1, 2, 9, 0, 0), True),   # Monday at 9 AM - match
            ("0 9 * * 1", datetime(2023, 1, 3, 9, 0, 0), False),  # Tuesday at 9 AM - no match
        ]
        
        for cron_expr, test_time, should_match in test_cases:
            with patch.object(self.processor, '_create_session', return_value=True) as mock_create:
                trigger = self.create_mock_trigger(cron_expr=cron_expr)
                result = self.processor._process_trigger(trigger, "params", test_time)
                
                assert result is True  # Processing should always succeed
                
                if should_match:
                    mock_create.assert_called_once()
                else:
                    mock_create.assert_not_called()
                
                # Reset mock for next iteration
                mock_create.reset_mock()