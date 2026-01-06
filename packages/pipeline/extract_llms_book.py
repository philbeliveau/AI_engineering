#!/usr/bin/env python3
"""
Extract Methodology, Checklist, Workflow, and Persona from LLMs in Production book.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the package directory to sys.path so imports work
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))
os.chdir(str(package_dir))

# Now import from the package
from src.storage.mongodb import MongoDBClient
from src.extractors.registry import extractor_registry
from src.extractors.types import ExtractionType

# Source ID for LLMs in Production book
SOURCE_ID = "695c4ffed9fd318585d2fe19"

# Extractors to run (in priority order)
EXTRACTORS = [
    ExtractionType.METHODOLOGY,
    ExtractionType.CHECKLIST,
    ExtractionType.WORKFLOW,
    ExtractionType.PERSONA,
]


async def main():
    mongo = MongoDBClient()
    mongo.connect()

    try:
        # Get all chunks for this source
        all_chunks = mongo.get_chunks_by_source(SOURCE_ID)
        print(f"📚 Found {len(all_chunks)} chunks in LLMs in Production")

        # Track results
        results = {
            "source_id": SOURCE_ID,
            "total_chunks": len(all_chunks),
            "timestamp": datetime.now().isoformat(),
            "extractors": {},
        }

        # Run each extractor
        for extraction_type in EXTRACTORS:
            print(f"\n{'='*60}")
            print(f"Running {extraction_type.value} Extraction")
            print(f"{'='*60}")

            extractor = extractor_registry.get_extractor(extraction_type)
            extraction_results = []
            errors = []
            successful = 0

            # Extract from each chunk
            for i, chunk in enumerate(all_chunks):
                try:
                    result = await extractor.extract(
                        chunk.content, chunk.id, chunk.source_id
                    )

                    if result and len(result) > 0:
                        extraction_results.extend(result)
                        successful += 1

                    # Progress indicator
                    if (i + 1) % 50 == 0:
                        print(f"  ✓ Processed {i + 1}/{len(all_chunks)} chunks")

                except Exception as e:
                    errors.append(
                        {
                            "chunk_id": chunk.id,
                            "chunk_index": i,
                            "error": str(e),
                        }
                    )
                    print(f"  ✗ Error on chunk {i + 1}: {e}")

            # Store results
            results["extractors"][extraction_type.value] = {
                "total_extractions": len(extraction_results),
                "successful_chunks": successful,
                "failed_chunks": len(errors),
                "sample": extraction_results[:3] if extraction_results else [],
                "errors": errors[:5] if errors else [],  # First 5 errors
            }

            print(
                f"\n✅ {extraction_type.value} Complete:"
            )
            print(f"   - Extractions: {len(extraction_results)}")
            print(f"   - Successful chunks: {successful}/{len(all_chunks)}")
            if errors:
                print(f"   - Failed chunks: {len(errors)}")

        # Save results summary
        output_path = Path("extraction_results.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n{'='*60}")
        print(f"✅ Extraction Complete!")
        print(f"{'='*60}")
        print(f"\n📊 Results saved to {output_path}")
        print("\nSummary:")
        for extractor_name, data in results["extractors"].items():
            print(
                f"  {extractor_name}: {data['total_extractions']} extractions ({data['successful_chunks']} chunks)"
            )

    finally:
        mongo.close()


if __name__ == "__main__":
    asyncio.run(main())
