"""
Utility functions for scheduler operations.

This module contains utility functions extracted from the original scheduler
for resource matching and other common operations.
"""

import re
from typing import List, Optional, Set
from app.database.models import Resource


def parse_capabilities_or_requirements(string: str) -> Set[str]:
    """Parse capabilities or requirements string into a set.
    
    Args:
        string: Comma or space-separated string of capabilities/requirements
        
    Returns:
        Set of parsed capabilities/requirements
    """
    if not string:
        return set()
    
    # Split by space or comma
    return set(re.split(r"[ ,]+", string.strip()))


def find_best_resource(requirements: str, resources: List[Resource]) -> Optional[Resource]:
    """Find the best matching resource for given requirements.
    
    Args:
        requirements: Requirements string for the session
        resources: List of available resources
        
    Returns:
        Best matching resource or None if no match found
    """
    if not requirements or not resources:
        return None
    
    session_requirements = parse_capabilities_or_requirements(requirements)
    best_resource = None
    least_capabilities = float("inf")

    for resource in resources:
        resource_capabilities = parse_capabilities_or_requirements(resource.capabilities)
        
        # Check if resource can satisfy all requirements
        if session_requirements.issubset(resource_capabilities):
            # Prefer resources with fewer capabilities to avoid over-allocation
            if len(resource_capabilities) < least_capabilities:
                best_resource = resource
                least_capabilities = len(resource_capabilities)

    return best_resource


def calculate_required_sessions(pending_items: int, scale_threshold: int) -> int:
    """Calculate how many sessions are needed based on pending items.
    
    Args:
        pending_items: Number of pending work items
        scale_threshold: Items per session threshold
        
    Returns:
        Number of sessions required (minimum 1 if any items exist)
    """
    if pending_items == 0:
        return 0
    
    required = pending_items // max(scale_threshold, 1)
    return max(1, required)


def should_scale_up(active_sessions: List, required_sessions: int, resource_limit: int) -> bool:
    """Check if we should scale up based on current and required sessions.
    
    Args:
        active_sessions: List of currently active sessions
        required_sessions: Number of sessions we need
        resource_limit: Maximum allowed sessions for this trigger
        
    Returns:
        True if we should create a new session
    """
    if required_sessions == 0:
        return False
    
    # Don't exceed the resource limit
    capped_required = min(required_sessions, resource_limit)
    return len(active_sessions) < capped_required