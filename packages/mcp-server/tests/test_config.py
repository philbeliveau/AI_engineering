"""Tests for configuration module."""



class TestSettings:
    """Test cases for Settings configuration class."""

    def test_default_environment(self):
        """Test that default environment is 'local'."""
        from src.config import Settings

        settings = Settings()
        assert settings.environment == "local"

    def test_default_mongodb_uri(self):
        """Test that default MongoDB URI is set correctly."""
        from src.config import Settings

        settings = Settings()
        assert settings.mongodb_uri == "mongodb://localhost:27017"

    def test_default_mongodb_database(self):
        """Test that default MongoDB database is set correctly."""
        from src.config import Settings

        settings = Settings()
        assert settings.mongodb_database == "knowledge_db"

    def test_default_qdrant_url(self):
        """Test that default Qdrant URL is set correctly."""
        from src.config import Settings

        settings = Settings()
        assert settings.qdrant_url == "http://localhost:6333"

    def test_default_server_host(self):
        """Test that default server host is set correctly."""
        from src.config import Settings

        settings = Settings()
        assert settings.server_host == "0.0.0.0"

    def test_default_server_port(self):
        """Test that default server port is set correctly."""
        from src.config import Settings

        settings = Settings()
        assert settings.server_port == 8000

    def test_default_log_level(self):
        """Test that default log level is 'INFO'."""
        from src.config import Settings

        settings = Settings()
        assert settings.log_level == "INFO"

    def test_settings_singleton_exported(self):
        """Test that settings singleton is exported."""
        from src.config import settings

        assert settings is not None
        assert settings.environment == "local"

    def test_env_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("SERVER_PORT", "9000")

        from src.config import Settings

        settings = Settings()
        assert settings.environment == "production"
        assert settings.server_port == 9000
