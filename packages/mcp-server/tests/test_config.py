"""Tests for configuration module.

Tests for cloud database configuration settings (Story 5.4).
"""


class TestSettings:
    """Test cases for Settings configuration class."""

    def test_default_environment(self):
        """Test that default environment is 'local'."""
        from src.config import Settings

        # Use _env_file=None to skip loading .env file and get true defaults
        settings = Settings(_env_file=None)
        assert settings.environment == "local"

    def test_default_mongodb_uri(self):
        """Test that default MongoDB URI is set correctly."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.mongodb_uri == "mongodb://localhost:27017"

    def test_default_mongodb_database(self):
        """Test that default MongoDB database is set correctly."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.mongodb_database == "knowledge_db"

    def test_default_qdrant_url(self):
        """Test that default Qdrant URL is set correctly."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.qdrant_url == "http://localhost:6333"

    def test_default_server_host(self):
        """Test that default server host is set correctly."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.server_host == "0.0.0.0"

    def test_default_server_port(self):
        """Test that default server port is set correctly."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.server_port == 8000

    def test_default_log_level(self):
        """Test that default log level is 'INFO'."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.log_level == "INFO"

    def test_settings_singleton_exported(self):
        """Test that settings singleton is exported."""
        from src.config import settings

        # Just verify it's exported - don't check specific values since they come from .env
        assert settings is not None

    def test_env_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SERVER_PORT", "9000")

        from src.config import Settings

        settings = Settings()
        assert settings.environment == "production"
        assert settings.server_port == 9000


class TestCloudDatabaseSettings:
    """Test cases for cloud database configuration settings (Story 5.4)."""

    def test_default_qdrant_api_key_is_none(self):
        """Test that QDRANT_API_KEY defaults to None."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.qdrant_api_key is None

    def test_qdrant_api_key_from_env(self, monkeypatch):
        """Test that QDRANT_API_KEY can be set from environment."""
        monkeypatch.setenv("QDRANT_API_KEY", "test-api-key-12345")

        from src.config import Settings

        settings = Settings()
        assert settings.qdrant_api_key == "test-api-key-12345"

    def test_default_ssl_enabled_true_for_production(self, monkeypatch):
        """Test that SSL is enabled by default in production."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        from src.config import Settings

        settings = Settings()
        assert settings.ssl_enabled is True

    def test_default_ssl_enabled_true(self):
        """Test that SSL is enabled by default."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.ssl_enabled is True

    def test_ssl_enabled_from_env(self, monkeypatch):
        """Test that SSL_ENABLED can be set from environment."""
        monkeypatch.setenv("SSL_ENABLED", "false")

        from src.config import Settings

        settings = Settings()
        assert settings.ssl_enabled is False

    def test_default_connection_timeout_ms(self):
        """Test default connection timeout is 5000ms."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.connection_timeout_ms == 5000

    def test_connection_timeout_from_env(self, monkeypatch):
        """Test that CONNECTION_TIMEOUT_MS can be set from environment."""
        monkeypatch.setenv("CONNECTION_TIMEOUT_MS", "10000")

        from src.config import Settings

        settings = Settings()
        assert settings.connection_timeout_ms == 10000

    def test_default_max_pool_size(self):
        """Test default max pool size is 10."""
        from src.config import Settings

        settings = Settings(_env_file=None)
        assert settings.max_pool_size == 10

    def test_max_pool_size_from_env(self, monkeypatch):
        """Test that MAX_POOL_SIZE can be set from environment."""
        monkeypatch.setenv("MAX_POOL_SIZE", "25")

        from src.config import Settings

        settings = Settings()
        assert settings.max_pool_size == 25

    def test_environment_values(self, monkeypatch):
        """Test that environment supports local, staging, production."""
        for env in ["local", "staging", "production"]:
            monkeypatch.setenv("ENVIRONMENT", env)

            from src.config import Settings

            settings = Settings()
            assert settings.environment == env

    def test_mongodb_atlas_uri_accepted(self, monkeypatch):
        """Test that MongoDB Atlas connection strings are accepted."""
        atlas_uri = "mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true"
        monkeypatch.setenv("MONGODB_URI", atlas_uri)

        from src.config import Settings

        settings = Settings()
        assert settings.mongodb_uri == atlas_uri

    def test_qdrant_cloud_url_accepted(self, monkeypatch):
        """Test that Qdrant Cloud URLs are accepted."""
        cloud_url = "https://abc123.cloud.qdrant.io:6333"
        monkeypatch.setenv("QDRANT_URL", cloud_url)

        from src.config import Settings

        settings = Settings()
        assert settings.qdrant_url == cloud_url


class TestEnvironmentValidation:
    """Test environment validation functions (Story 5.4 Task 7)."""

    def test_validate_environment_production_with_cloud(self):
        """Test validation passes for production with cloud databases."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="production",
            mongodb_uri="mongodb+srv://user:pass@cluster.mongodb.net/db",
            qdrant_url="https://abc123.cloud.qdrant.io:6333",
        )

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_environment_production_with_local_mongodb(self):
        """Test validation fails for production with local MongoDB."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="production",
            mongodb_uri="mongodb://localhost:27017",
            qdrant_url="https://abc123.cloud.qdrant.io:6333",
        )

        assert result.is_valid is False
        assert any("MongoDB" in e and "localhost" in e for e in result.errors)

    def test_validate_environment_production_with_local_qdrant(self):
        """Test validation fails for production with local Qdrant."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="production",
            mongodb_uri="mongodb+srv://user:pass@cluster.mongodb.net/db",
            qdrant_url="http://localhost:6333",
        )

        assert result.is_valid is False
        assert any("Qdrant" in e and "localhost" in e for e in result.errors)

    def test_validate_environment_local_with_local_dbs(self):
        """Test validation passes for local with local databases."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="local",
            mongodb_uri="mongodb://localhost:27017",
            qdrant_url="http://localhost:6333",
        )

        assert result.is_valid is True
        assert len(result.warnings) > 0  # Should warn about using local in dev

    def test_validate_environment_staging_with_local_warns(self):
        """Test validation warns for staging with local databases."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="staging",
            mongodb_uri="mongodb://localhost:27017",
            qdrant_url="http://localhost:6333",
        )

        # Staging should warn but not fail
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_validate_mongodb_uri_format_invalid(self):
        """Test validation catches invalid MongoDB URI format."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="local",
            mongodb_uri="not-a-valid-uri",
            qdrant_url="http://localhost:6333",
        )

        assert result.is_valid is False
        assert any("MongoDB URI" in e and "format" in e.lower() for e in result.errors)

    def test_validate_qdrant_url_format_invalid(self):
        """Test validation catches invalid Qdrant URL format."""
        from src.storage.connection import validate_environment

        result = validate_environment(
            environment="local",
            mongodb_uri="mongodb://localhost:27017",
            qdrant_url="not-a-valid-url",
        )

        assert result.is_valid is False
        assert any("Qdrant URL" in e and "format" in e.lower() for e in result.errors)
