#!/usr/bin/env python3
"""Test extraction on 2 chunks only."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.storage.mongodb import MongoDBClient
from src.extractors import extractor_registry

async def main():
    # Connect to MongoDB
    mongo = MongoDBClient()

    # Get 2 chunks from the source
    source_id = "695c4ffed9fd318585d2fe19"
    mongo.connect()
    all_chunks = mongo.get_chunks_by_source(source_id)
    chunks = all_chunks[:2]

    print(f"Testing extraction on {len(chunks)} chunks from source: {source_id}\n")
    print("=" * 80)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n### CHUNK {i}: {chunk.id}")
        print(f"Text (first 200 chars):\n{chunk.content[:200]}...\n")

        # Run all extractors
        for extraction_type in extractor_registry.list_extraction_types():
            type_name = extraction_type if isinstance(extraction_type, str) else extraction_type.value
            try:
                extractor = extractor_registry.get_extractor(extraction_type)
                result = await extractor.extract(chunk.content, chunk.id, chunk.source_id)
                if result:
                    print(f"  ✓ {type_name.upper()}: {len(result)} items")
                    for item in result[:1]:  # Show first item
                        if hasattr(item, 'dict'):
                            d = item.dict()
                            summary = d.get('title', d.get('summary', str(d)[:80]))
                            print(f"      Sample: {summary}")
                        else:
                            print(f"      Sample: {str(item)[:80]}")
                else:
                    print(f"  - {type_name.upper()}: No extractions")
            except Exception as e:
                print(f"  ✗ {type_name.upper()}: Error - {str(e)[:80]}")

        print()

    mongo.close()
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(main())
