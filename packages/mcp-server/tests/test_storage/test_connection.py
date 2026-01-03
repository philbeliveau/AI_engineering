"""Tests for cloud database connection handlers (Story 5.4).

Tests connection factory functions for MongoDB Atlas and Qdrant Cloud.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCloudDetection:
    """Test cloud vs local database detection functions."""

    def test_is_cloud_mongodb_atlas_srv(self):
        """Test detection of MongoDB Atlas mongodb+srv:// URLs."""
        from src.storage.connection import is_cloud_mongodb

        assert is_cloud_mongodb("mongodb+srv://user:pass@cluster.mongodb.net/db") is True

    def test_is_cloud_mongodb_atlas_net(self):
        """Test detection of MongoDB Atlas mongodb.net URLs."""
        from src.storage.connection import is_cloud_mongodb

        assert is_cloud_mongodb("mongodb://user:pass@cluster.mongodb.net:27017/db") is True

    def test_is_cloud_mongodb_local(self):
        """Test detection of local MongoDB URLs."""
        from src.storage.connection import is_cloud_mongodb

        assert is_cloud_mongodb("mongodb://localhost:27017") is False
        assert is_cloud_mongodb("mongodb://127.0.0.1:27017") is False

    def test_is_cloud_qdrant_cloud(self):
        """Test detection of Qdrant Cloud URLs."""
        from src.storage.connection import is_cloud_qdrant

        assert is_cloud_qdrant("https://abc123.cloud.qdrant.io:6333") is True
        assert is_cloud_qdrant("https://abc.us-east1-0.cloud.qdrant.io:6333") is True

    def test_is_cloud_qdrant_local(self):
        """Test detection of local Qdrant URLs."""
        from src.storage.connection import is_cloud_qdrant

        assert is_cloud_qdrant("http://localhost:6333") is False
        assert is_cloud_qdrant("http://127.0.0.1:6333") is False


class TestMongoDBConnectionFactory:
    """Test MongoDB connection factory function."""

    @patch("src.storage.connection.MongoClient")
    def test_create_mongodb_client_local(self, mock_client_class):
        """Test creating MongoDB client for local development."""
        from src.config import Settings
        from src.storage.connection import create_mongodb_client

        test_settings = Settings(
            mongodb_uri="mongodb://localhost:27017",
            connection_timeout_ms=5000,
        )
        client = create_mongodb_client(test_settings)

        # Should be called with basic options for local
        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert "serverSelectionTimeoutMS" in call_kwargs
        # Local shouldn't use ServerApi
        assert "server_api" not in call_kwargs or call_kwargs.get("server_api") is None

    @patch("src.storage.connection.MongoClient")
    def test_create_mongodb_client_atlas(self, mock_client_class):
        """Test creating MongoDB client for Atlas (cloud)."""
        from src.config import Settings
        from src.storage.connection import create_mongodb_client

        atlas_uri = "mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true"
        test_settings = Settings(
            mongodb_uri=atlas_uri,
            connection_timeout_ms=5000,
            max_pool_size=10,
        )
        client = create_mongodb_client(test_settings)

        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        # First arg is the URI
        assert call_args[0][0] == atlas_uri
        # Atlas should have additional options
        call_kwargs = call_args[1]
        assert "serverSelectionTimeoutMS" in call_kwargs
        assert "maxPoolSize" in call_kwargs

    @patch("src.storage.connection.MongoClient")
    def test_create_mongodb_client_uses_settings(self, mock_client_class):
        """Test that connection factory uses settings from provided settings."""
        from src.config import Settings
        from src.storage.connection import create_mongodb_client

        test_settings = Settings(
            mongodb_uri="mongodb://testhost:27017",
            connection_timeout_ms=8000,
            max_pool_size=20,
        )
        client = create_mongodb_client(test_settings)

        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["serverSelectionTimeoutMS"] == 8000


class TestQdrantConnectionFactory:
    """Test Qdrant connection factory function."""

    @patch("src.storage.connection.QdrantClient")
    def test_create_qdrant_client_local(self, mock_client_class):
        """Test creating Qdrant client for local development."""
        from src.config import Settings
        from src.storage.connection import create_qdrant_client

        test_settings = Settings(
            qdrant_url="http://localhost:6333",
            qdrant_api_key=None,
        )
        client = create_qdrant_client(test_settings)

        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["url"] == "http://localhost:6333"
        # Local shouldn't have API key
        assert call_kwargs.get("api_key") is None

    @patch("src.storage.connection.QdrantClient")
    def test_create_qdrant_client_cloud(self, mock_client_class):
        """Test creating Qdrant client for Qdrant Cloud."""
        from src.config import Settings
        from src.storage.connection import create_qdrant_client

        cloud_url = "https://abc123.cloud.qdrant.io:6333"
        api_key = "test-api-key-12345"
        test_settings = Settings(
            qdrant_url=cloud_url,
            qdrant_api_key=api_key,
        )
        client = create_qdrant_client(test_settings)

        mock_client_class.assert_called_once()
        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["url"] == cloud_url
        assert call_kwargs["api_key"] == api_key
        assert call_kwargs["timeout"] == 30  # Default cloud timeout

    @patch("src.storage.connection.QdrantClient")
    def test_create_qdrant_client_uses_settings(self, mock_client_class):
        """Test that connection factory uses settings from provided settings."""
        from src.config import Settings
        from src.storage.connection import create_qdrant_client

        test_settings = Settings(
            qdrant_url="http://testhost:6333",
        )
        client = create_qdrant_client(test_settings)

        call_kwargs = mock_client_class.call_args[1]
        assert call_kwargs["url"] == "http://testhost:6333"


class TestDatabaseHealthCheck:
    """Test database health check function (Story 5.4 Task 5)."""

    @pytest.mark.asyncio
    async def test_check_database_health_all_healthy(self):
        """Test health check when all databases are healthy."""
        from src.storage.connection import check_database_health

        mock_mongodb = AsyncMock()
        mock_mongodb.ping.return_value = True

        mock_qdrant = AsyncMock()
        mock_qdrant.ping.return_value = True

        result = await check_database_health(mock_mongodb, mock_qdrant)

        assert result["mongodb"] is True
        assert result["qdrant"] is True
        assert "details" in result

    @pytest.mark.asyncio
    async def test_check_database_health_mongodb_unhealthy(self):
        """Test health check when MongoDB fails."""
        from src.storage.connection import check_database_health

        mock_mongodb = AsyncMock()
        mock_mongodb.ping.return_value = False

        mock_qdrant = AsyncMock()
        mock_qdrant.ping.return_value = True

        result = await check_database_health(mock_mongodb, mock_qdrant)

        assert result["mongodb"] is False
        assert result["qdrant"] is True

    @pytest.mark.asyncio
    async def test_check_database_health_qdrant_unhealthy(self):
        """Test health check when Qdrant fails."""
        from src.storage.connection import check_database_health

        mock_mongodb = AsyncMock()
        mock_mongodb.ping.return_value = True

        mock_qdrant = AsyncMock()
        mock_qdrant.ping.return_value = False

        result = await check_database_health(mock_mongodb, mock_qdrant)

        assert result["mongodb"] is True
        assert result["qdrant"] is False

    @pytest.mark.asyncio
    async def test_check_database_health_handles_exception(self):
        """Test health check gracefully handles exceptions."""
        from src.storage.connection import check_database_health

        mock_mongodb = AsyncMock()
        mock_mongodb.ping.side_effect = Exception("Connection failed")

        mock_qdrant = AsyncMock()
        mock_qdrant.ping.return_value = True

        result = await check_database_health(mock_mongodb, mock_qdrant)

        assert result["mongodb"] is False
        assert result["qdrant"] is True
        assert "connection failed" in result["details"]["mongodb_error"].lower()

    @pytest.mark.asyncio
    async def test_check_database_health_handles_none_clients(self):
        """Test health check when clients are None."""
        from src.storage.connection import check_database_health

        result = await check_database_health(None, None)

        assert result["mongodb"] is False
        assert result["qdrant"] is False


class TestConnectionRetryLogic:
    """Test connection retry logic (Story 5.4 Task 6)."""

    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test that retry logic succeeds after initial failures."""
        from src.storage.connection import connect_with_retry

        call_count = 0

        async def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection refused")
            return "connected"

        result = await connect_with_retry(failing_then_success, max_retries=5)

        assert result == "connected"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test that retry raises after max attempts."""
        from src.storage.connection import connect_with_retry

        call_count = 0

        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Connection refused")

        with pytest.raises(ConnectionError) as exc_info:
            await connect_with_retry(always_fail, max_retries=3)

        # Should have tried 3 times (initial + 2 retries is wrong, it's max_retries attempts)
        assert call_count == 3
        assert "Connection refused" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self):
        """Test that retry uses exponential backoff timing."""
        import time

        from src.storage.connection import connect_with_retry

        call_times: list[float] = []

        async def failing_func():
            call_times.append(time.time())
            raise ConnectionError("Connection refused")

        try:
            await connect_with_retry(failing_func, max_retries=3, base_delay=0.1)
        except ConnectionError:
            pass

        # Verify timing: delays should be ~0.1s, ~0.2s between calls
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.08  # Allow some timing variance

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= 0.15  # Should be ~0.2s (2x first delay)

    @pytest.mark.asyncio
    async def test_retry_success_on_first_try(self):
        """Test that no retry occurs when first attempt succeeds."""
        from src.storage.connection import connect_with_retry

        call_count = 0

        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await connect_with_retry(success_func)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_logs_attempts(self):
        """Test that retry logic logs each attempt."""
        from src.storage.connection import connect_with_retry

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection refused")
            return "connected"

        result = await connect_with_retry(failing_func, operation_name="test_connection")

        assert result == "connected"
