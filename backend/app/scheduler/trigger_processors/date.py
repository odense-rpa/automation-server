"""
Date trigger processor.

This module implements the trigger processor for date-based scheduling.
"""

import logging
from datetime import datetime

from app.database.models import Trigger
from .base import AbstractTriggerProcessor

logger = logging.getLogger(__name__)


class DateTriggerProcessor(AbstractTriggerProcessor):
    """Processor for date-based triggers."""
    
    def _process_trigger(self, trigger: Trigger, validated_params: str, now: datetime) -> bool:
        """Process a date trigger.
        
        Args:
            trigger: The date trigger to process
            validated_params: Pre-validated parameters
            now: Current datetime for date comparison
            
        Returns:
            True if processing was successful
        """
        try:
            # Check if the trigger date has been reached
            if trigger.date and trigger.date <= now:
                logger.info(f"Triggering date trigger {trigger.id} at {now}")
                
                # Create the session
                success = self._create_session(trigger, validated_params)
                
                if success:
                    # Date triggers are one-time only, so disable and mark as deleted
                    self.services.trigger_repository.update(trigger, {"enabled": False, "deleted": True})
                    logger.info(f"Date trigger {trigger.id} disabled after execution")
                
                return success
            else:
                # Not time to trigger yet, but processing was successful
                return True
                
        except Exception as e:
            logger.error(f"Error processing date trigger {trigger.id}: {e}")
            return False