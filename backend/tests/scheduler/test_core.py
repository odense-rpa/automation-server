"""
Tests for scheduler core module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime

from app.scheduler.core import AutomationScheduler, scheduler_background_task


class TestAutomationScheduler:
    """Tests for AutomationScheduler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scheduler = AutomationScheduler()
    
    @patch('app.scheduler.core.settings')
    @pytest.mark.asyncio
    async def test_run_background_task_disabled(self, mock_settings):
        """Test background task when scheduler is disabled."""
        mock_settings.scheduler_enabled = False
        
        with patch('app.scheduler.core.logger') as mock_logger:
            await self.scheduler.run_background_task()
            mock_logger.info.assert_called_once_with("Scheduler is disabled via configuration")
    
    @patch('app.scheduler.core.settings')
    @patch('app.scheduler.core.asyncio.sleep', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_run_background_task_single_iteration(self, mock_sleep, mock_settings):
        """Test background task for a single iteration."""
        mock_settings.scheduler_enabled = True
        mock_settings.scheduler_interval = 10
        
        # Mock the schedule method to avoid actual scheduling
        with patch.object(self.scheduler, 'schedule', new_callable=AsyncMock) as mock_schedule:
            # Stop after first iteration by making sleep raise an exception
            mock_sleep.side_effect = [KeyboardInterrupt()]
            
            with pytest.raises(KeyboardInterrupt):
                await self.scheduler.run_background_task()
            
            # Verify schedule was called once
            mock_schedule.assert_called_once()
            # Verify sleep was called with correct interval
            mock_sleep.assert_called_once_with(10)
    
    @patch('app.scheduler.core.settings')
    @patch('app.scheduler.core.asyncio.sleep', new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_run_background_task_error_handling(self, mock_sleep, mock_settings):
        """Test background task error handling."""
        mock_settings.scheduler_enabled = True
        mock_settings.scheduler_interval = 10
        mock_settings.scheduler_error_backoff = 30
        
        # Mock schedule to raise an error first, then succeed
        with patch.object(self.scheduler, 'schedule', new_callable=AsyncMock) as mock_schedule:
            mock_schedule.side_effect = [Exception("Test error"), None, KeyboardInterrupt()]
            mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
            
            with patch('app.scheduler.core.logger') as mock_logger:
                with pytest.raises(KeyboardInterrupt):
                    await self.scheduler.run_background_task()
                
                # Verify error was logged
                mock_logger.error.assert_called_once_with("Scheduler error: Test error")
            
            # Verify schedule was called twice (error, then success)
            assert mock_schedule.call_count == 2
            
            # Verify sleep was called with both error backoff and normal interval
            expected_calls = [call(30), call(10)]
            mock_sleep.assert_has_calls(expected_calls)
    
    
    @pytest.mark.asyncio
    async def test_process_triggers_empty_list(self):
        """Test processing triggers with empty trigger list."""
        mock_trigger_repo = MagicMock()
        mock_process_repo = MagicMock()
        mock_trigger_repo.get_all.return_value = []
        
        # Should complete without errors
        await self.scheduler._process_triggers(mock_trigger_repo, mock_process_repo, datetime.now())
        
        mock_trigger_repo.get_all.assert_called_once_with(include_deleted=False)
    
    @pytest.mark.asyncio
    async def test_process_triggers_skips_disabled_triggers(self):
        """Test that disabled triggers are skipped."""
        mock_trigger_repo = MagicMock()
        mock_process_repo = MagicMock()
        
        # Create disabled trigger
        disabled_trigger = MagicMock()
        disabled_trigger.enabled = False
        disabled_trigger.id = 1
        
        mock_trigger_repo.get_all.return_value = [disabled_trigger]
        
        await self.scheduler._process_triggers(mock_trigger_repo, mock_process_repo, datetime.now())
        
        # Should not process disabled triggers
        mock_process_repo.get.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_triggers_skips_deleted_processes(self):
        """Test that triggers for deleted processes are skipped."""
        mock_trigger_repo = MagicMock()
        mock_process_repo = MagicMock()
        
        # Create enabled trigger
        enabled_trigger = MagicMock()
        enabled_trigger.enabled = True
        enabled_trigger.process_id = 1
        enabled_trigger.id = 2
        
        # Process is deleted
        deleted_process = MagicMock()
        deleted_process.deleted = True
        
        mock_trigger_repo.get_all.return_value = [enabled_trigger]
        mock_process_repo.get.return_value = deleted_process
        
        await self.scheduler._process_triggers(mock_trigger_repo, mock_process_repo, datetime.now())
        
        # Should check process status but not proceed with processing
        mock_process_repo.get.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_scheduler_background_task():
    """Test the backward compatibility function."""
    with patch('app.scheduler.core.scheduler') as mock_scheduler:
        mock_scheduler.run_background_task = AsyncMock()
        
        await scheduler_background_task()
        
        mock_scheduler.run_background_task.assert_called_once()