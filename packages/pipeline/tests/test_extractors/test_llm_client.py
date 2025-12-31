"""Tests for LLMClient.

All tests use mocked API calls - no real API requests are made.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import pytest

from src.extractors import LLMClient, LLMClientError


class TestLLMClientInitialization:
    """Test LLMClient initialization."""

    def test_init_with_defaults(self):
        """LLMClient uses settings defaults when no args provided."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024

            client = LLMClient()

            assert client.model == "claude-3-haiku-20240307"
            assert client.max_tokens == 1024

    def test_init_with_custom_values(self):
        """LLMClient accepts custom model and max_tokens."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "default-model"
            mock_settings.llm_max_tokens = 512

            client = LLMClient(
                model="claude-3-opus-20240229",
                max_tokens=2048,
                api_key="custom-key",
            )

            assert client.model == "claude-3-opus-20240229"
            assert client.max_tokens == 2048


class TestLLMClientExtract:
    """Test LLMClient.extract() method."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock Anthropic API response."""
        response = MagicMock()
        response.content = [MagicMock(text='{"decisions": []}')]
        response.usage = MagicMock(input_tokens=100, output_tokens=50)
        return response

    @pytest.fixture
    def llm_client(self):
        """Create an LLMClient with mocked settings."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024
            client = LLMClient()
            yield client

    @pytest.mark.asyncio
    async def test_extract_success(self, llm_client, mock_response):
        """Successful extraction returns LLM response text."""
        llm_client._client.messages.create = AsyncMock(return_value=mock_response)

        result = await llm_client.extract(
            prompt="Extract decisions from this text",
            content="Some content about RAG vs fine-tuning",
        )

        assert result == '{"decisions": []}'
        llm_client._client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_combines_prompt_and_content(self, llm_client, mock_response):
        """Extract method combines prompt and content correctly."""
        llm_client._client.messages.create = AsyncMock(return_value=mock_response)

        await llm_client.extract(
            prompt="Extract decisions",
            content="Content here",
        )

        call_args = llm_client._client.messages.create.call_args
        message_content = call_args.kwargs["messages"][0]["content"]
        assert "Extract decisions" in message_content
        assert "Content here" in message_content
        assert "CONTENT TO EXTRACT FROM:" in message_content

    @pytest.mark.asyncio
    async def test_extract_uses_correct_model(self, llm_client, mock_response):
        """Extract method uses the configured model."""
        llm_client._client.messages.create = AsyncMock(return_value=mock_response)

        await llm_client.extract(prompt="Test", content="Test")

        call_args = llm_client._client.messages.create.call_args
        assert call_args.kwargs["model"] == "claude-3-haiku-20240307"

    @pytest.mark.asyncio
    async def test_extract_uses_correct_max_tokens(self, llm_client, mock_response):
        """Extract method uses the configured max_tokens."""
        llm_client._client.messages.create = AsyncMock(return_value=mock_response)

        await llm_client.extract(prompt="Test", content="Test")

        call_args = llm_client._client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 1024


class TestLLMClientErrorHandling:
    """Test LLMClient error handling."""

    @pytest.fixture
    def llm_client(self):
        """Create an LLMClient with mocked settings."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024
            client = LLMClient()
            yield client

    @pytest.mark.asyncio
    async def test_extract_auth_error(self, llm_client):
        """AuthenticationError raises LLMClientError with AUTH_ERROR code."""
        llm_client._client.messages.create = AsyncMock(
            side_effect=anthropic.AuthenticationError(
                message="Invalid API key",
                response=MagicMock(status_code=401),
                body=None,
            )
        )

        with pytest.raises(LLMClientError) as exc_info:
            await llm_client.extract(prompt="Test", content="Test")

        assert exc_info.value.code == "AUTH_ERROR"
        assert "authentication" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_extract_bad_request_error(self, llm_client):
        """BadRequestError raises LLMClientError with BAD_REQUEST code."""
        llm_client._client.messages.create = AsyncMock(
            side_effect=anthropic.BadRequestError(
                message="Invalid request",
                response=MagicMock(status_code=400),
                body=None,
            )
        )

        with pytest.raises(LLMClientError) as exc_info:
            await llm_client.extract(prompt="Test", content="Test")

        assert exc_info.value.code == "BAD_REQUEST"

    @pytest.mark.asyncio
    async def test_extract_api_status_error(self, llm_client):
        """APIStatusError raises LLMClientError with API_ERROR code."""
        llm_client._client.messages.create = AsyncMock(
            side_effect=anthropic.APIStatusError(
                message="Server error",
                response=MagicMock(status_code=500),
                body=None,
            )
        )

        with pytest.raises(LLMClientError) as exc_info:
            await llm_client.extract(prompt="Test", content="Test")

        assert exc_info.value.code == "API_ERROR"
        assert "500" in exc_info.value.message


class TestLLMClientRetryLogic:
    """Test LLMClient retry behavior."""

    @pytest.fixture
    def llm_client(self):
        """Create an LLMClient with mocked settings."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024
            client = LLMClient()
            yield client

    @pytest.fixture
    def mock_response(self):
        """Create a mock Anthropic API response."""
        response = MagicMock()
        response.content = [MagicMock(text='{"result": "success"}')]
        response.usage = MagicMock(input_tokens=100, output_tokens=50)
        return response

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, llm_client, mock_response):
        """Retries on RateLimitError before succeeding."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise anthropic.RateLimitError(
                    message="Rate limited",
                    response=MagicMock(status_code=429),
                    body=None,
                )
            return mock_response

        llm_client._client.messages.create = AsyncMock(side_effect=side_effect)

        # Patch tenacity to not actually wait
        with patch("tenacity.wait_exponential.__call__", return_value=0):
            result = await llm_client.extract(prompt="Test", content="Test")

        assert result == '{"result": "success"}'
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self, llm_client, mock_response):
        """Retries on APIConnectionError before succeeding."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise anthropic.APIConnectionError(
                    request=MagicMock(),
                )
            return mock_response

        llm_client._client.messages.create = AsyncMock(side_effect=side_effect)

        with patch("tenacity.wait_exponential.__call__", return_value=0):
            result = await llm_client.extract(prompt="Test", content="Test")

        assert result == '{"result": "success"}'
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_gives_up_after_max_retries(self, llm_client):
        """Raises after max retry attempts exceeded."""
        llm_client._client.messages.create = AsyncMock(
            side_effect=anthropic.RateLimitError(
                message="Rate limited",
                response=MagicMock(status_code=429),
                body=None,
            )
        )

        with patch("tenacity.wait_exponential.__call__", return_value=0):
            with pytest.raises(anthropic.RateLimitError):
                await llm_client.extract(prompt="Test", content="Test")

        # Should have been called 3 times (initial + 2 retries)
        assert llm_client._client.messages.create.call_count == 3


class TestLLMClientContextManager:
    """Test LLMClient async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self):
        """Context manager calls close on exit."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024

            async with LLMClient() as client:
                client._client.close = AsyncMock()

            client._client.close.assert_called_once()


class TestLLMClientError:
    """Test LLMClientError exception class."""

    def test_error_has_code_message_details(self):
        """LLMClientError includes code, message, and details."""
        error = LLMClientError(
            code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
        )

        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}
        assert str(error) == "Test error message"

    def test_error_defaults_empty_details(self):
        """LLMClientError defaults to empty details dict."""
        error = LLMClientError(code="TEST", message="Test")

        assert error.details == {}


class TestLLMClientLogging:
    """Test LLMClient structured logging."""

    @pytest.fixture
    def mock_response(self):
        """Create a mock Anthropic API response."""
        response = MagicMock()
        response.content = [MagicMock(text='{"result": "test"}')]
        response.usage = MagicMock(input_tokens=100, output_tokens=50)
        return response

    @pytest.mark.asyncio
    async def test_logs_extraction_start(self, mock_response):
        """Logs extraction start with context."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024

            with patch("src.extractors.llm_client.logger") as mock_logger:
                client = LLMClient()
                client._client.messages.create = AsyncMock(return_value=mock_response)

                await client.extract(prompt="Test prompt", content="Test content")

                # Verify debug log was called for extraction start
                mock_logger.debug.assert_called()
                debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
                assert any("llm_extraction_start" in call for call in debug_calls)

    @pytest.mark.asyncio
    async def test_logs_extraction_complete(self, mock_response):
        """Logs extraction completion with token usage."""
        with patch("src.extractors.llm_client.settings") as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.llm_model = "claude-3-haiku-20240307"
            mock_settings.llm_max_tokens = 1024

            with patch("src.extractors.llm_client.logger") as mock_logger:
                client = LLMClient()
                client._client.messages.create = AsyncMock(return_value=mock_response)

                await client.extract(prompt="Test", content="Test")

                # Verify info log was called for completion
                mock_logger.info.assert_called()
                info_calls = [str(call) for call in mock_logger.info.call_args_list]
                assert any("llm_extraction_complete" in call for call in info_calls)
