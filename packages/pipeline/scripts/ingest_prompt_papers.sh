#!/usr/bin/env bash
set -euo pipefail

# Batch ingest all prompt engineering papers
# Uses knowledge-pipeline project to store in knowledge-pipeline_chunks collection

PAPER_DIR="/Users/philippebeliveau/Desktop/Notebook/AI_engineering/_bmad-output/data/download-script/prompt-engineering"
PROJECT="knowledge-pipeline"
CATEGORY="reference"
TAGS="prompt-engineering,llm"

cd /Users/philippebeliveau/Desktop/Notebook/AI_engineering/packages/pipeline

echo "========================================"
echo "Ingesting Prompt Engineering Papers"
echo "========================================"
echo "Source: $PAPER_DIR"
echo "Project: $PROJECT"
echo "Category: $CATEGORY"
echo "Tags: $TAGS"
echo ""

# Counter
total=0
success=0
failed=0

for pdf in "$PAPER_DIR"/*.pdf; do
    if [ -f "$pdf" ]; then
        filename=$(basename "$pdf")
        total=$((total + 1))
        echo ""
        echo "[$total] Processing: $filename"
        echo "----------------------------------------"

        if uv run scripts/ingest.py "$pdf" --project "$PROJECT" --category "$CATEGORY" --tags "$TAGS" --year 2024; then
            success=$((success + 1))
            echo "SUCCESS: $filename"
        else
            failed=$((failed + 1))
            echo "FAILED: $filename"
        fi
    fi
done

echo ""
echo "========================================"
echo "BATCH INGESTION COMPLETE"
echo "========================================"
echo "Total:   $total"
echo "Success: $success"
echo "Failed:  $failed"
echo "========================================"
