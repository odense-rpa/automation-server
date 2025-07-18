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
        # Add required attributes for the new tests
        self.mock_services.trigger_repository = MagicMock()
        self.mock_services.session_service = MagicMock()
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

    def test_process_trigger_only_once_per_minute_first_time(self):
        """Test that a trigger fires for the first time (last_triggered is None)."""
        now = datetime(2023, 1, 1, 0, 0, 0)
        
        # Create trigger with last_triggered = None (never fired)
        trigger = self.create_mock_trigger(cron_expr="0 0 * * *")
        trigger.last_triggered = None
        
        with patch.object(self.processor, '_create_session', return_value=True) as mock_create:
            result = self.processor._process_trigger(trigger, "params", now)
            
        # Should fire for first time
        assert result is True
        mock_create.assert_called_once()
    
    def test_process_trigger_only_once_per_minute_already_fired(self):
        """Test that a trigger doesn't fire again in the same minute."""
        now = datetime(2023, 1, 1, 0, 0, 0)
        
        # Create trigger that was already fired in the current minute
        trigger = self.create_mock_trigger(cron_expr="0 0 * * *")
        trigger.last_triggered = datetime(2023, 1, 1, 0, 0, 15)  # 15 seconds ago
        
        with patch.object(self.processor, '_create_session', return_value=True) as mock_create:
            result = self.processor._process_trigger(trigger, "params", now)
            
        # Should NOT fire again in same minute
        assert result is True
        mock_create.assert_not_called()
    
    def test_process_trigger_only_once_per_minute_next_minute(self):
        """Test that a trigger fires again after minute boundary."""
        now = datetime(2023, 1, 1, 0, 1, 0)  # Next minute
        
        # Create trigger that was fired in previous minute
        trigger = self.create_mock_trigger(cron_expr="*/1 * * * *")  # Every minute
        trigger.last_triggered = datetime(2023, 1, 1, 0, 0, 30)  # Previous minute
        
        with patch.object(self.processor, '_create_session', return_value=True) as mock_create:
            result = self.processor._process_trigger(trigger, "params", now)
            
        # Should fire in new minute
        assert result is True
        mock_create.assert_called_once()
    
    def test_process_trigger_updates_last_triggered_on_success(self):
        """Test that last_triggered is updated when session is created successfully."""
        now = datetime(2023, 1, 1, 0, 0, 0)
        
        # Create trigger with no last_triggered
        trigger = self.create_mock_trigger(cron_expr="0 0 * * *")
        trigger.last_triggered = None
        
        # Mock the repository update
        with patch.object(self.processor.services.trigger_repository, 'update') as mock_update:
            with patch.object(self.processor.services.session_service, 'create_session') as mock_session_service:
                mock_session_service.return_value = type('MockSession', (), {'id': 123})()
                
                result = self.processor._process_trigger(trigger, "params", now)
                
        # Should update last_triggered
        assert result is True
        mock_update.assert_called_once()
        # Verify that last_triggered was set to current time
        update_call = mock_update.call_args
        assert update_call[0][0] == trigger  # First argument is the trigger
        assert "last_triggered" in update_call[0][1]  # Second argument contains last_triggered
    
    def test_process_trigger_multiple_calls_same_minute(self):
        """Test that multiple calls within the same minute only trigger once."""
        base_time = datetime(2023, 1, 1, 0, 0, 0)
        
        # Create trigger with no last_triggered
        trigger = self.create_mock_trigger(cron_expr="0 0 * * *")
        trigger.last_triggered = None
        
        session_create_count = 0
        
        def mock_create_session_side_effect(*args, **kwargs):
            nonlocal session_create_count
            session_create_count += 1
            # Update last_triggered to simulate the real behavior
            trigger.last_triggered = base_time
            return type('MockSession', (), {'id': 123})()
        
        with patch.object(self.processor.services.session_service, 'create_session', side_effect=mock_create_session_side_effect):
            with patch.object(self.processor.services.trigger_repository, 'update'):
                # First call should trigger
                result1 = self.processor._process_trigger(trigger, "params", base_time)
                
                # Second call in same minute should not trigger
                result2 = self.processor._process_trigger(trigger, "params", base_time.replace(second=30))
                
                # Third call in same minute should not trigger
                result3 = self.processor._process_trigger(trigger, "params", base_time.replace(second=45))
        
        # All calls should return True (success)
        assert result1 is True
        assert result2 is True
        assert result3 is True
        
        # But session should only be created once
        assert session_create_count == 1