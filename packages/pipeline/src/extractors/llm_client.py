"""LLM client for automated knowledge extraction.

Provides a client wrapper around the Anthropic API for batch
extraction of structured knowledge from document chunks.
"""

import anthropic
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import settings

logger = structlog.get_logger()


class LLMClientError(Exception):
    """Base exception for LLM client errors."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class LLMClient:
    """Client for LLM-based knowledge extraction.

    Uses Claude Haiku for cost-effective batch extraction.
    Includes retry logic with exponential backoff for resilience.

    Example:
        client = LLMClient()
        response = await client.extract(
            prompt="Extract decisions from this text...",
            content="The text to extract from..."
        )
    """

    def __init__(
        self,
        model: str | None = None,
        max_tokens: int | None = None,
        api_key: str | None = None,
    ):
        """Initialize the LLM client.

        Args:
            model: LLM model to use. Defaults to settings.llm_model.
            max_tokens: Maximum tokens in response. Defaults to settings.llm_max_tokens.
            api_key: Anthropic API key. Defaults to settings.anthropic_api_key.
        """
        self._api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.llm_model
        self.max_tokens = max_tokens or settings.llm_max_tokens

        # Create async client
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key)

        logger.debug(
            "llm_client_initialized",
            model=self.model,
            max_tokens=self.max_tokens,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(
            (anthropic.APIConnectionError, anthropic.RateLimitError)
        ),
        reraise=True,
    )
    async def extract(self, prompt: str, content: str) -> str:
        """Extract structured knowledge using LLM.

        Sends a prompt and content to the LLM and returns the raw response.
        Includes retry logic for transient API errors.

        Args:
            prompt: Extraction prompt with instructions.
            content: Chunk content to extract from.

        Returns:
            Raw LLM response text (expected to be JSON).

        Raises:
            LLMClientError: If extraction fails after retries.
        """
        logger.debug(
            "llm_extraction_start",
            model=self.model,
            prompt_length=len(prompt),
            content_length=len(content),
        )

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n---\n\nCONTENT TO EXTRACT FROM:\n{content}",
                    }
                ],
            )

            result = response.content[0].text

            logger.info(
                "llm_extraction_complete",
                model=self.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                response_length=len(result),
            )

            return result

        except (anthropic.APIConnectionError, anthropic.RateLimitError):
            # Let tenacity handle retryable errors - re-raise for retry
            raise

        except anthropic.AuthenticationError as e:
            logger.error(
                "llm_authentication_failed",
                error=str(e),
            )
            raise LLMClientError(
                code="AUTH_ERROR",
                message="Anthropic API authentication failed",
                details={"error": str(e)},
            ) from e

        except anthropic.BadRequestError as e:
            logger.error(
                "llm_bad_request",
                error=str(e),
                model=self.model,
            )
            raise LLMClientError(
                code="BAD_REQUEST",
                message="Invalid request to Anthropic API",
                details={"error": str(e), "model": self.model},
            ) from e

        except anthropic.APIStatusError as e:
            logger.error(
                "llm_api_error",
                status_code=e.status_code,
                error=str(e),
            )
            raise LLMClientError(
                code="API_ERROR",
                message=f"Anthropic API error: {e.status_code}",
                details={"status_code": e.status_code, "error": str(e)},
            ) from e

    async def close(self) -> None:
        """Close the async client connection."""
        await self._client.close()
        logger.debug("llm_client_closed")

    async def __aenter__(self) -> "LLMClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
