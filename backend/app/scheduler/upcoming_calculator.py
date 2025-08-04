"""
Utility functions for calculating upcoming trigger executions.

This module provides functions to calculate when triggers will next execute,
primarily used for the "Up Next" display feature.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from cronsim import CronSim, CronSimError

from app.database.models import Trigger
from app.enums import TriggerType

logger = logging.getLogger(__name__)


def calculate_next_execution(trigger: Trigger, now: Optional[datetime] = None) -> Optional[datetime]:
    """
    Calculate the next execution time for a trigger.
    
    Args:
        trigger: The trigger to calculate next execution for
        now: Current datetime (defaults to datetime.now())
        
    Returns:
        Next execution datetime or None if trigger won't execute
    """
    if now is None:
        now = datetime.now()
    
    if not trigger.enabled or trigger.deleted:
        return None
    
    try:
        if trigger.type == TriggerType.CRON:
            return _calculate_cron_next_execution(trigger, now)
        elif trigger.type == TriggerType.DATE:
            return _calculate_date_next_execution(trigger, now)
        elif trigger.type == TriggerType.WORKQUEUE:
            # Workqueue triggers don't have predictable schedules
            return None
        else:
            logger.warning(f"Unknown trigger type: {trigger.type}")
            return None
    except Exception as e:
        logger.error(f"Error calculating next execution for trigger {trigger.id}: {e}")
        return None


def _calculate_cron_next_execution(trigger: Trigger, now: datetime) -> Optional[datetime]:
    """Calculate next execution for cron trigger."""
    if not trigger.cron:
        return None
    
    try:
        cron_sim = CronSim(trigger.cron, now)
        next_execution = next(cron_sim)
        return next_execution
    except (CronSimError, StopIteration) as e:
        logger.error(f"Error calculating cron next execution for trigger {trigger.id}: {e}")
        return None


def _calculate_date_next_execution(trigger: Trigger, now: datetime) -> Optional[datetime]:
    """Calculate next execution for date trigger."""
    if not trigger.date:
        return None
    
    # If the scheduled date is in the future, return it
    if trigger.date > now:
        return trigger.date
    
    # If the scheduled date is in the past, it won't execute again
    return None


def get_upcoming_executions(
    triggers: List[Trigger], 
    hours_ahead: int = 24, 
    now: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get upcoming executions for a list of triggers within a time window.
    
    Args:
        triggers: List of triggers to check
        hours_ahead: How many hours ahead to look (default: 24)
        now: Current datetime (defaults to datetime.now())
        
    Returns:
        List of dictionaries containing trigger and execution info
    """
    if now is None:
        now = datetime.now()
    
    cutoff_time = now + timedelta(hours=hours_ahead)
    upcoming_executions = []
    
    for trigger in triggers:
        next_execution = calculate_next_execution(trigger, now)
        
        if next_execution and next_execution <= cutoff_time:
            upcoming_executions.append({
                'trigger': trigger,
                'next_execution': next_execution,
                'trigger_type': trigger.type.value,
                'process_id': trigger.process_id,
                'parameters': trigger.parameters
            })
    
    # Sort by next execution time
    upcoming_executions.sort(key=lambda x: x['next_execution'])
    
    return upcoming_executions


def get_cron_next_executions(
    trigger: Trigger, 
    count: int = 5, 
    now: Optional[datetime] = None
) -> List[datetime]:
    """
    Get the next N executions for a cron trigger.
    
    Args:
        trigger: The cron trigger
        count: Number of next executions to return
        now: Current datetime (defaults to datetime.now())
        
    Returns:
        List of next execution datetimes
    """
    if now is None:
        now = datetime.now()
    
    if trigger.type != TriggerType.CRON or not trigger.cron:
        return []
    
    try:
        cron_sim = CronSim(trigger.cron, now)
        next_executions = []
        
        for _ in range(count):
            try:
                next_execution = next(cron_sim)
                next_executions.append(next_execution)
            except StopIteration:
                break
        
        return next_executions
    except CronSimError as e:
        logger.error(f"Error calculating cron executions for trigger {trigger.id}: {e}")
        return []