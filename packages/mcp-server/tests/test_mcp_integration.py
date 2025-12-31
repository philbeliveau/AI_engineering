"""Tests for fastapi-mcp integration."""



class TestMCPIntegration:
    """Test cases for MCP integration."""

    def test_mcp_instance_created(self):
        """Test that MCP instance is created."""
        from src.server import mcp

        assert mcp is not None

    def test_mcp_is_fastapi_mcp(self):
        """Test that mcp is a FastApiMCP instance."""
        from fastapi_mcp import FastApiMCP

        from src.server import mcp

        assert isinstance(mcp, FastApiMCP)

    def test_app_has_mcp_routes(self):
        """Test that MCP routes are registered on the app."""
        from src.server import app

        # Check that MCP routes are registered
        route_paths = [route.path for route in app.routes]
        # The mcp.mount_http() adds /mcp endpoint
        assert any("/mcp" in path for path in route_paths)
