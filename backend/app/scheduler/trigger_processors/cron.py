"""
Cron trigger processor.

This module implements the trigger processor for cron-based scheduling.
"""

import logging
from datetime import datetime, timedelta
from cronsim import CronSim

from app.database.models import Trigger
from app.scheduler.validators import validate_cron_expression
from .base import AbstractTriggerProcessor

logger = logging.getLogger(__name__)


class CronTriggerProcessor(AbstractTriggerProcessor):
    """Processor for cron-based triggers."""
    
    def _process_trigger(self, trigger: Trigger, validated_params: str, now: datetime) -> bool:
        """Process a cron trigger.
        
        Args:
            trigger: The cron trigger to process
            validated_params: Pre-validated parameters
            now: Current datetime for cron evaluation
            
        Returns:
            True if processing was successful
        """
        try:
            # Validate the cron expression
            validated_cron = validate_cron_expression(trigger.cron)
            
            # Check if it's time to trigger based on the cron expression
            # Simple approach: start from one minute before and check if next match is current minute
            current_minute = now.replace(second=0, microsecond=0)
            
            # Start from one minute before to catch the current minute
            start_time = current_minute - timedelta(minutes=1)
            
            try:
                cron_sim = CronSim(validated_cron, start_time)
                next_time = next(cron_sim)
                
                # If the next scheduled time matches the current minute, trigger
                if next_time.replace(second=0, microsecond=0) == current_minute:
                    logger.info(f"Triggering cron trigger {trigger.id} at {now}")
                    return self._create_session(trigger, validated_params)
                else:
                    # Not time to trigger yet, but processing was successful
                    return True
            except StopIteration:
                # No more matches in the next 50 years, so definitely not triggering now
                return True
                
        except Exception as e:
            logger.error(f"Error processing cron trigger {trigger.id}: {e}")
            return False