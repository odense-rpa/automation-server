"""
Tests for scheduler utils module.
"""

import pytest
from unittest.mock import MagicMock
from app.scheduler.utils import (
    parse_capabilities_or_requirements,
    find_best_resource,
    calculate_required_sessions,
    should_scale_up
)


class TestParseCapabilitiesOrRequirements:
    """Tests for parse_capabilities_or_requirements function."""
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parse_capabilities_or_requirements("")
        assert result == set()
    
    def test_parse_none(self):
        """Test parsing None."""
        result = parse_capabilities_or_requirements(None)
        assert result == set()
    
    def test_parse_space_separated(self):
        """Test parsing space-separated capabilities."""
        result = parse_capabilities_or_requirements("python docker linux")
        assert result == {"python", "docker", "linux"}
    
    def test_parse_comma_separated(self):
        """Test parsing comma-separated capabilities."""
        result = parse_capabilities_or_requirements("python,docker,linux")
        assert result == {"python", "docker", "linux"}
    
    def test_parse_mixed_separators(self):
        """Test parsing with mixed separators."""
        result = parse_capabilities_or_requirements("python, docker linux")
        assert result == {"python", "docker", "linux"}
    
    def test_parse_with_extra_spaces(self):
        """Test parsing with extra spaces."""
        result = parse_capabilities_or_requirements("  python   docker   linux  ")
        assert result == {"python", "docker", "linux"}


class TestFindBestResource:
    """Tests for find_best_resource function."""
    
    def create_mock_resource(self, capabilities):
        """Helper to create mock resource."""
        resource = MagicMock()
        resource.capabilities = capabilities
        return resource
    
    def test_find_best_resource_empty_requirements(self):
        """Test finding resource with empty requirements."""
        resources = [self.create_mock_resource("python docker")]
        result = find_best_resource("", resources)
        assert result is None
    
    def test_find_best_resource_no_resources(self):
        """Test finding resource with no available resources."""
        result = find_best_resource("python", [])
        assert result is None
    
    def test_find_best_resource_exact_match(self):
        """Test finding resource with exact capability match."""
        resource1 = self.create_mock_resource("python")
        resource2 = self.create_mock_resource("python docker")
        resources = [resource1, resource2]
        
        result = find_best_resource("python", resources)
        assert result == resource1  # Fewer capabilities preferred
    
    def test_find_best_resource_subset_match(self):
        """Test finding resource where requirements are subset of capabilities."""
        resource1 = self.create_mock_resource("python docker linux")
        resource2 = self.create_mock_resource("python java")
        resources = [resource1, resource2]
        
        result = find_best_resource("python", resources)
        assert result == resource2  # Fewer capabilities preferred
    
    def test_find_best_resource_no_match(self):
        """Test finding resource when no resource can satisfy requirements."""
        resource1 = self.create_mock_resource("java")
        resource2 = self.create_mock_resource("go")
        resources = [resource1, resource2]
        
        result = find_best_resource("python", resources)
        assert result is None
    
    def test_find_best_resource_multiple_requirements(self):
        """Test finding resource with multiple requirements."""
        resource1 = self.create_mock_resource("python docker linux mysql")
        resource2 = self.create_mock_resource("python docker")
        resources = [resource1, resource2]
        
        result = find_best_resource("python docker", resources)
        assert result == resource2  # Fewer capabilities preferred


class TestCalculateRequiredSessions:
    """Tests for calculate_required_sessions function."""
    
    def test_calculate_required_sessions_zero_items(self):
        """Test calculation with zero pending items."""
        result = calculate_required_sessions(0, 5)
        assert result == 0
    
    def test_calculate_required_sessions_below_threshold(self):
        """Test calculation with items below threshold."""
        result = calculate_required_sessions(3, 5)
        assert result == 1  # Minimum 1 session if any items exist
    
    def test_calculate_required_sessions_exact_threshold(self):
        """Test calculation with items exactly at threshold."""
        result = calculate_required_sessions(5, 5)
        assert result == 1
    
    def test_calculate_required_sessions_above_threshold(self):
        """Test calculation with items above threshold."""
        result = calculate_required_sessions(12, 5)
        assert result == 2  # 12 // 5 = 2
    
    def test_calculate_required_sessions_zero_threshold(self):
        """Test calculation with zero threshold (edge case)."""
        result = calculate_required_sessions(10, 0)
        assert result == 10  # Should use threshold of 1
    
    def test_calculate_required_sessions_negative_threshold(self):
        """Test calculation with negative threshold (edge case)."""
        result = calculate_required_sessions(10, -5)
        assert result == 10  # Should use threshold of 1


class TestShouldScaleUp:
    """Tests for should_scale_up function."""
    
    def test_should_scale_up_zero_required(self):
        """Test scaling decision with zero required sessions."""
        active_sessions = [MagicMock()]
        result = should_scale_up(active_sessions, 0, 5)
        assert result is False
    
    def test_should_scale_up_below_required(self):
        """Test scaling decision when active sessions below required."""
        active_sessions = [MagicMock()]
        result = should_scale_up(active_sessions, 3, 5)
        assert result is True
    
    def test_should_scale_up_meets_required(self):
        """Test scaling decision when active sessions meet required."""
        active_sessions = [MagicMock(), MagicMock(), MagicMock()]
        result = should_scale_up(active_sessions, 3, 5)
        assert result is False
    
    def test_should_scale_up_exceeds_required(self):
        """Test scaling decision when active sessions exceed required."""
        active_sessions = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        result = should_scale_up(active_sessions, 3, 5)
        assert result is False
    
    def test_should_scale_up_resource_limit_constraint(self):
        """Test scaling decision when resource limit constrains required sessions."""
        active_sessions = [MagicMock()]
        result = should_scale_up(active_sessions, 10, 2)  # Limited to 2 by resource_limit
        assert result is True  # 1 < min(10, 2) = 2
    
    def test_should_scale_up_at_resource_limit(self):
        """Test scaling decision when at resource limit."""
        active_sessions = [MagicMock(), MagicMock()]
        result = should_scale_up(active_sessions, 10, 2)  # Limited to 2 by resource_limit
        assert result is False  # 2 >= min(10, 2) = 2