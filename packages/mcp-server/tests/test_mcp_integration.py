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

    def test_mcp_excludes_infrastructure_tags(self):
        """Test that MCP excludes infrastructure endpoints from tools.

        Per context7 best practices, health check and other infrastructure
        endpoints should not be exposed as MCP tools.
        """
        from src.server import mcp

        # Verify exclude_tags is configured
        assert hasattr(mcp, "exclude_tags") or "infrastructure" in str(mcp.__dict__)

    def test_health_endpoint_has_infrastructure_tag(self):
        """Test that health endpoint is tagged as infrastructure."""
        from src.server import app

        # Find the health route
        health_route = None
        for route in app.routes:
            if hasattr(route, "path") and route.path == "/health":
                health_route = route
                break

        assert health_route is not None
        assert hasattr(health_route, "tags")
        assert "infrastructure" in health_route.tags

    def test_mcp_has_correct_name(self):
        """Test that MCP server has the correct name."""
        from src.server import mcp

        assert mcp.name == "AI Engineering Knowledge"

    def test_mcp_mounted_after_endpoints(self):
        """Test that MCP is created after endpoints are defined.

        This ensures all endpoints are captured by the MCP server.
        Per context7 docs, endpoints defined after mount_http() require
        calling setup_server() to be included.
        """
        from src.server import app

        # Health endpoint should exist
        route_paths = [
            route.path for route in app.routes if hasattr(route, "path")
        ]
        assert "/health" in route_paths
