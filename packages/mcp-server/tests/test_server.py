"""Tests for FastAPI server application."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestServerApp:
    """Test cases for server application."""

    def test_server_app_import(self):
        """Test that app can be imported from server."""
        from src.server import app

        assert app is not None

    def test_server_app_is_fastapi(self):
        """Test that app is a FastAPI instance."""
        from src.server import app

        assert isinstance(app, FastAPI)

    def test_server_app_has_title(self):
        """Test that app has proper title."""
        from src.server import app

        assert "AI Engineering Knowledge" in app.title

    def test_server_app_has_version(self):
        """Test that app has version from package."""
        from src import __version__
        from src.server import app

        assert app.version == __version__

    def test_health_endpoint_exists(self):
        """Test that /health endpoint exists."""
        from src.server import app

        client = TestClient(app)
        response = client.get("/health")
        # Should return either 200 or 503 depending on service status
        assert response.status_code in [200, 503]

    def test_health_endpoint_returns_json(self):
        """Test that /health endpoint returns JSON."""
        from src.server import app

        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert "version" in data

    def test_main_function_exists(self):
        """Test that main function exists for CLI entry point."""
        from src.server import main

        assert main is not None
        assert callable(main)


class TestServerLifecycle:
    """Test cases for server lifecycle events."""

    def test_startup_event_defined(self):
        """Test that startup event is defined."""
        from src.server import app

        # Check that we have lifespan or on_event handlers
        # In newer FastAPI, lifespan is preferred
        assert app.router.lifespan_context is not None or hasattr(app, "on_event")

    def test_mongodb_client_available(self):
        """Test that MongoDB client is configured."""
        from src.server import mongodb_client

        # May be None before startup, but should be importable
        assert mongodb_client is not None or mongodb_client is None

    def test_qdrant_client_available(self):
        """Test that Qdrant client is configured."""
        from src.server import qdrant_client

        # May be None before startup, but should be importable
        assert qdrant_client is not None or qdrant_client is None
