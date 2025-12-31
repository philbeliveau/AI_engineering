"""Tests for health check endpoint."""

import pytest


class TestHealthCheck:
    """Test cases for health check endpoint."""

    def test_health_check_import(self):
        """Test that health_check can be imported."""
        from src.tools.health import health_check

        assert health_check is not None

    @pytest.mark.asyncio
    async def test_health_check_is_async(self):
        """Test that health_check is an async function."""
        import inspect

        from src.tools.health import health_check

        assert inspect.iscoroutinefunction(health_check)

    @pytest.mark.asyncio
    async def test_health_check_returns_dict(self):
        """Test that health_check returns a dictionary."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_health_check_has_status(self):
        """Test that health_check returns status field."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_health_check_has_timestamp(self):
        """Test that health_check returns timestamp field."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_health_check_has_services(self):
        """Test that health_check returns services field."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        assert "services" in result

    @pytest.mark.asyncio
    async def test_health_check_has_version(self):
        """Test that health_check returns version field."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        assert "version" in result

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_when_no_clients(self):
        """Test that health check is unhealthy when no clients provided."""
        from src.tools.health import health_check

        result = await health_check(mongodb_client=None, qdrant_client=None)
        # When clients are None, services should be unavailable
        assert result["services"]["mongodb"] == "unavailable"
        assert result["services"]["qdrant"] == "unavailable"

    def test_health_check_exported_from_tools(self):
        """Test that health_check is exported from tools package."""
        from src.tools import health_check

        assert health_check is not None
