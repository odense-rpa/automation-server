"""
Scheduler package for automation server.

This package contains the modular scheduler implementation that handles
trigger processing and session management for automation scripts.

The scheduler has been refactored from a monolithic design into a modular
architecture following the Strategy pattern:

- Core scheduler (AutomationScheduler) orchestrates the scheduling process
- Trigger processors handle specific trigger types (cron, date, workqueue)
- Services integration provides consistent abstraction layer usage
- Resource dispatcher handles session-to-resource allocation
- Validators provide reusable validation logic
- Utils contain utility functions for resource matching

This modular design improves:
- Testability: Each component can be unit tested independently
- Maintainability: Clear separation of concerns
- Extensibility: New trigger types can be added without modifying core logic
- Consistency: Aligns with the rest of the application's architecture
"""

# Maintain backward compatibility
from .core import AutomationScheduler, scheduler_background_task

__all__ = ['AutomationScheduler', 'scheduler_background_task']