# Plan: Reduce MCP Server Docker Image Size (7.8 GB → ~800 MB)

## Status: ⏸️ DEFERRED

**Decision:** Keep `sentence-transformers` (heavy library) for now. Revisit after more sources are ingested.

**Reason:** Switching to `fastembed` requires re-indexing all documents. Better to do this once after all books are ingested rather than multiple times.

---

## Problem
Docker image is 7.8 GB, causing:
- Slow deployments on Railway
- High storage costs
- Long container startup times

## Root Cause Analysis

**Culprit: `sentence-transformers>=4.0.0`** in `pyproject.toml`

This package requires **PyTorch** which adds ~4-5 GB to the image:
- PyTorch CPU: ~2 GB
- CUDA libraries (even when not used): ~2 GB
- Model files downloaded at runtime: ~500 MB

**Current dependency chain:**
```
sentence-transformers → torch → ~4 GB
                      → transformers → ~500 MB
                      → huggingface-hub → ~100 MB
```

## ⚠️ CRITICAL RISK ANALYSIS

### Risk 1: Embedding Space Incompatibility (HIGH)
**Source:** [GitHub Issue #368](https://github.com/qdrant/fastembed/issues/368)

FastEmbed (ONNX) and sentence-transformers (PyTorch) can produce **different embeddings** for the same model. One reported case showed only **0.609 cosine similarity** instead of expected ~1.0.

**Impact:**
- Pipeline uses `sentence-transformers` to index documents
- MCP server uses `sentence-transformers` to query
- If we ONLY change MCP server → search will break

**Mitigation:** Must change BOTH packages OR test nomic-v1.5 specifically for compatibility.

### Risk 2: Instruction Prefix Handling (MEDIUM)
**Source:** [Qdrant Nomic Docs](https://qdrant.tech/documentation/embeddings/nomic/)

FastEmbed does NOT automatically apply `search_query:`/`search_document:` prefixes.

**Impact:** Must manually prepend prefixes (same as current code)

**Mitigation:** Keep prefix logic in our code - no change needed.

### Risk 3: Model File Location (LOW)
FastEmbed uses ONNX files from HuggingFace. The nomic-embed-text-v1.5 ONNX files must exist.

**Status:** ✅ Confirmed - FastEmbed lists `nomic-ai/nomic-embed-text-v1.5` as supported.

## Solution Options

### Option A: FastEmbed for BOTH packages (Recommended if re-indexing OK)
- Change both `packages/pipeline` AND `packages/mcp-server` to use fastembed
- **Requires re-indexing all documents** (one-time cost)
- Guaranteed compatibility
- Image size: ~800 MB

### Option B: CPU-only PyTorch (Safe, less dramatic)
- Add `--index-url https://download.pytorch.org/whl/cpu` for PyTorch
- Keeps sentence-transformers, removes CUDA
- No re-indexing needed
- Image size: ~2-3 GB (still large but safer)

### Option C: FastEmbed MCP only + Test compatibility (Risky)
- Change only MCP server to fastembed
- Test that nomic-v1.5 ONNX ≈ PyTorch embeddings
- If cosine similarity < 0.99, abort
- Image size: ~800 MB (if it works)

## Step 0: Compatibility Test (FIRST)

Before deciding on an approach, test if nomic-embed-text-v1.5 produces compatible embeddings between PyTorch and ONNX.

### Test Script
```python
"""Test embedding compatibility between sentence-transformers and fastembed."""
import numpy as np

# Test texts
test_texts = [
    "search_query: What is RAG?",
    "search_query: How to chunk documents for embeddings?",
    "search_document: Retrieval-Augmented Generation combines retrieval with generation.",
]

# 1. Generate with sentence-transformers (PyTorch)
from sentence_transformers import SentenceTransformer
st_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
st_embeddings = st_model.encode(test_texts, normalize_embeddings=True)

# 2. Generate with fastembed (ONNX)
from fastembed import TextEmbedding
fe_model = TextEmbedding(model_name="nomic-ai/nomic-embed-text-v1.5")
fe_embeddings = np.array(list(fe_model.embed(test_texts)))

# 3. Compare cosine similarity
def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("Embedding Compatibility Test")
print("=" * 50)
for i, text in enumerate(test_texts):
    sim = cosine_sim(st_embeddings[i], fe_embeddings[i])
    status = "✅ PASS" if sim > 0.99 else "⚠️ WARN" if sim > 0.95 else "❌ FAIL"
    print(f"{status} Similarity: {sim:.6f} - {text[:40]}...")

avg_sim = np.mean([cosine_sim(st_embeddings[i], fe_embeddings[i]) for i in range(len(test_texts))])
print(f"\nAverage similarity: {avg_sim:.6f}")
print(f"Verdict: {'COMPATIBLE' if avg_sim > 0.99 else 'INCOMPATIBLE - requires re-indexing'}")
```

### Expected Results
- If similarity > 0.99: Can safely use FastEmbed for MCP only (Option C)
- If similarity < 0.99: Must use Option A (re-index) or Option B (CPU PyTorch)

---

## Recommended: Option A (FastEmbed for both)

This ensures embedding compatibility by using the same ONNX model for both indexing and querying.

## Files to Modify

### MCP Server Package
| File | Change |
|------|--------|
| `packages/mcp-server/pyproject.toml` | Replace `sentence-transformers` with `fastembed` |
| `packages/mcp-server/src/embeddings/embedding_service.py` | Update to use `fastembed` API |
| `packages/mcp-server/uv.lock` | Regenerate lockfile |

### Pipeline Package (for consistency)
| File | Change |
|------|--------|
| `packages/pipeline/pyproject.toml` | Replace `sentence-transformers` with `fastembed` |
| `packages/pipeline/src/embeddings/local_embedder.py` | Update to use `fastembed` API |
| `packages/pipeline/uv.lock` | Regenerate lockfile |

## Implementation Steps

### Step 1: Update MCP Server Dependencies
In `packages/mcp-server/pyproject.toml`, replace:
```diff
-    "sentence-transformers>=4.0.0",
-    "einops>=0.8.0",
+    "fastembed>=0.4.0",
```

### Step 2: Update MCP Server Embedding Service
Rewrite `packages/mcp-server/src/embeddings/embedding_service.py`:
```python
"""Embedding service using FastEmbed (ONNX Runtime)."""
from fastembed import TextEmbedding
import structlog

logger = structlog.get_logger()

EMBEDDING_MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_VECTOR_SIZE = 768
QUERY_PREFIX = "search_query: "

_embedding_model: TextEmbedding | None = None

def get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        logger.info("embedding_model_loading", model=EMBEDDING_MODEL_ID)
        _embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL_ID)
        logger.info("embedding_model_loaded", model=EMBEDDING_MODEL_ID)
    return _embedding_model

def embed_query(text: str) -> list[float]:
    model = get_embedding_model()
    prefixed_text = QUERY_PREFIX + text
    # fastembed returns generator, convert to list
    embeddings = list(model.embed([prefixed_text]))
    return embeddings[0].tolist()

class EmbeddingService:
    def embed_query(self, text: str) -> list[float]:
        return embed_query(text)
```

### Step 3: Update Pipeline Dependencies
In `packages/pipeline/pyproject.toml`, replace:
```diff
-    "sentence-transformers>=4.0.0",
+    "fastembed>=0.4.0",
```

### Step 4: Update Pipeline Embedder
Rewrite `packages/pipeline/src/embeddings/local_embedder.py` to use fastembed:
```python
from fastembed import TextEmbedding

DOCUMENT_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "

class LocalEmbedder:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = TextEmbedding(model_name="nomic-ai/nomic-embed-text-v1.5")
        return self._model

    def embed_text(self, text: str) -> list[float]:
        prefixed = DOCUMENT_PREFIX + text
        return list(self.model.embed([prefixed]))[0].tolist()

    def embed_query(self, text: str) -> list[float]:
        prefixed = QUERY_PREFIX + text
        return list(self.model.embed([prefixed]))[0].tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        prefixed = [DOCUMENT_PREFIX + t for t in texts]
        return [e.tolist() for e in self.model.embed(prefixed)]
```

### Step 5: Regenerate Lockfiles
```bash
cd packages/mcp-server && uv lock
cd packages/pipeline && uv lock
```

### Step 6: Test Locally
```bash
# Test MCP server
cd packages/mcp-server && uv run pytest

# Test pipeline embedding
cd packages/pipeline && uv run python -c "from src.embeddings import get_embedder; e = get_embedder(); print(len(e.embed_text('test')))"
```

### Step 7: Build and Verify Image Size
```bash
cd packages/mcp-server
docker build -t knowledge-mcp-test .
docker images knowledge-mcp-test  # Should be ~800 MB
```

### Step 8: Re-index Documents (REQUIRED)
Since embeddings will be different, must re-ingest all sources:
```bash
cd packages/pipeline
# Clear existing vectors in Qdrant
# Re-run ingestion for all sources
```

### Step 9: Commit and Deploy
```bash
git add -A
git commit -m "perf: Replace sentence-transformers with fastembed

- Switch to ONNX Runtime for embedding generation
- Reduces Docker image from 7.8 GB to ~800 MB
- Must re-index documents due to embedding space change"
git push origin main
```

## Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Image size | 7.8 GB | ~800 MB |
| Deploy time | ~5 min | ~1 min |
| Cold start | ~30s | ~10s |
| Memory usage | ~2 GB | ~500 MB |

## ⚠️ Required Post-Deploy Action
**RE-INDEX ALL DOCUMENTS** after deploying, because ONNX embeddings differ from PyTorch embeddings.

## Verification
```bash
# Check image size
docker images | grep knowledge-mcp

# Test embedding endpoint (after re-indexing)
curl -s "https://knowledge-mcp-production.up.railway.app/search_knowledge?query=rag+chunking&limit=3"
```

## Alternative: Option B (CPU-only PyTorch)

If re-indexing is not acceptable, use CPU-only PyTorch:

### Dockerfile changes:
```dockerfile
# In builder stage, install CPU-only PyTorch first
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### pyproject.toml changes:
```toml
# Keep sentence-transformers, but add torch-cpu marker
# This is more complex and may require custom pip configuration
```

**Tradeoff:** Image still ~2-3 GB but no re-indexing needed.
