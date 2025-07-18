"""
Trigger processor registry.

This module provides a registry for mapping trigger types to their processors.
"""

import logging
from typing import Dict, Type

from app.enums import TriggerType
from .base import AbstractTriggerProcessor, ProcessingServices
from .cron import CronTriggerProcessor
from .date import DateTriggerProcessor
from .workqueue import WorkqueueTriggerProcessor

logger = logging.getLogger(__name__)


class TriggerProcessorRegistry:
    """Registry for trigger processors using the Strategy pattern."""
    
    def __init__(self, services: ProcessingServices):
        """Initialize the registry with services.
        
        Args:
            services: Processing services container
        """
        self.services = services
        self._processors: Dict[str, AbstractTriggerProcessor] = {}
        self._register_default_processors()
    
    def _register_default_processors(self):
        """Register the default trigger processors."""
        self._processors[TriggerType.CRON] = CronTriggerProcessor(self.services)
        self._processors[TriggerType.DATE] = DateTriggerProcessor(self.services)
        self._processors[TriggerType.WORKQUEUE] = WorkqueueTriggerProcessor(self.services)
    
    def get_processor(self, trigger_type: str) -> AbstractTriggerProcessor:
        """Get a processor for a trigger type.
        
        Args:
            trigger_type: The type of trigger to get processor for
            
        Returns:
            Appropriate trigger processor
            
        Raises:
            ValueError: If trigger type is not supported
        """
        if trigger_type not in self._processors:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")
        
        return self._processors[trigger_type]
    
    def register_processor(self, trigger_type: str, processor_class: Type[AbstractTriggerProcessor]):
        """Register a new processor type.
        
        Args:
            trigger_type: The trigger type to register
            processor_class: The processor class to register
        """
        self._processors[trigger_type] = processor_class(self.services)
        logger.info(f"Registered processor for trigger type: {trigger_type}")
    
    def get_supported_types(self) -> list:
        """Get list of supported trigger types.
        
        Returns:
            List of supported trigger type strings
        """
        return list(self._processors.keys())