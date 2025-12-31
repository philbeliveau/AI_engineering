"""Real API test for LLMClient.

Run with: uv run python scripts/test_llm_client_real.py
"""

import asyncio

from src.extractors import LLMClient


async def main():
    """Test LLMClient with a real API call."""
    print("Testing LLMClient with real Anthropic API...")

    async with LLMClient() as client:
        print(f"Model: {client.model}")
        print(f"Max tokens: {client.max_tokens}")
        print()

        # Simple extraction test
        prompt = """Extract any decisions mentioned in the text below.
Return a JSON array with objects containing "question" and "options" fields.
If no decisions found, return an empty array [].
"""

        content = """When building a RAG system, you need to decide between
using a vector database like Qdrant or Pinecone, or using a simpler
approach with SQLite and full-text search. The choice depends on your
scale requirements and budget."""

        print("Sending extraction request...")
        print("-" * 40)

        response = await client.extract(prompt=prompt, content=content)

        print("Response:")
        print(response)
        print("-" * 40)
        print("\nAPI test successful!")


if __name__ == "__main__":
    asyncio.run(main())
