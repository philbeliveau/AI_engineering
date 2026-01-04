"""
Knowledge Pipeline Web Interface
Simple drag-and-drop ingestion with database status monitoring.

Run: uv run streamlit run web_app.py
"""

import streamlit as st
import subprocess
import tempfile
import os
from pathlib import Path

# Import pipeline components
from src.config import settings
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient


@st.cache_data(ttl=60)  # Cache for 60 seconds, manual refresh clears it
def get_mongodb_stats():
    """Get MongoDB collection statistics."""
    client = None
    try:
        client = MongoDBClient()
        client.connect()  # Must connect before using
        db = client._client[settings.mongodb_database]

        # Get collection stats using settings properties (not hardcoded names)
        sources_count = db[settings.sources_collection].count_documents({})
        chunks_count = db[settings.chunks_collection].count_documents({})
        extractions_count = db[settings.extractions_collection].count_documents({})

        # Get recent sources
        recent_sources = list(
            db[settings.sources_collection]
            .find({}, {"title": 1, "status": 1, "ingested_at": 1, "type": 1})
            .sort("ingested_at", -1)
            .limit(5)
        )

        return {
            "connected": True,
            "sources": sources_count,
            "chunks": chunks_count,
            "extractions": extractions_count,
            "recent_sources": recent_sources,
            "database": settings.mongodb_database,
            "project_id": settings.project_id,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
    finally:
        if client:
            client.close()


@st.cache_data(ttl=60)  # Cache for 60 seconds, manual refresh clears it
def get_qdrant_stats():
    """Get Qdrant collection statistics."""
    try:
        client = QdrantStorageClient()  # Uses settings internally

        # Ensure collection exists (creates if not)
        client.ensure_knowledge_collection()

        # Get collection info
        collection_name = "knowledge_vectors"
        info = client.client.get_collection(collection_name)

        return {
            "connected": True,
            "collection": collection_name,
            "vectors_count": info.points_count,
            "vector_dimension": info.config.params.vectors.size,
            "status": info.status.value,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


def run_ingestion(file_path: str, category: str, tags: str, year: int | None):
    """Run the ingestion pipeline."""
    cmd = ["uv", "run", "scripts/ingest.py", file_path]

    if category:
        cmd.extend(["--category", category])
    if tags:
        cmd.extend(["--tags", tags])
    if year:
        cmd.extend(["--year", str(year)])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )

    return result.stdout, result.stderr, result.returncode


# Page config
st.set_page_config(
    page_title="Knowledge Pipeline",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Knowledge Pipeline Ingestion")

# Sidebar: Database Status
with st.sidebar:
    st.header("Database Status")

    if st.button("🔄 Refresh Status"):
        st.cache_data.clear()

    # MongoDB Status
    st.subheader("MongoDB")
    mongo_stats = get_mongodb_stats()

    if mongo_stats["connected"]:
        st.success(f"✅ Connected to `{mongo_stats['database']}`")
        st.metric("Sources", mongo_stats["sources"])
        st.metric("Chunks", mongo_stats["chunks"])
        st.metric("Extractions", mongo_stats["extractions"])
        st.caption(f"Project: `{mongo_stats['project_id']}`")
    else:
        st.error(f"❌ Disconnected: {mongo_stats.get('error', 'Unknown')}")

    st.divider()

    # Qdrant Status
    st.subheader("Qdrant")
    qdrant_stats = get_qdrant_stats()

    if qdrant_stats["connected"]:
        st.success(f"✅ Connected")
        st.metric("Vectors", qdrant_stats["vectors_count"])
        st.caption(f"Dimension: {qdrant_stats['vector_dimension']}d")
        st.caption(f"Collection: `{qdrant_stats['collection']}`")
        st.caption(f"Status: {qdrant_stats['status']}")
    else:
        st.error(f"❌ Disconnected: {qdrant_stats.get('error', 'Unknown')}")

# Main content: File Upload
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Drag and drop a file here",
        type=["pdf", "md", "markdown", "docx", "html", "pptx"],
        help="Supported formats: PDF, Markdown, Word, HTML, PowerPoint",
    )

with col2:
    st.subheader("Metadata")

    category = st.selectbox(
        "Category",
        options=["", "foundational", "advanced", "reference", "case_study"],
        help="Categorize the document for filtering",
    )

    tags = st.text_input(
        "Tags",
        placeholder="rag, llm, production",
        help="Comma-separated tags",
    )

    year = st.number_input(
        "Publication Year",
        min_value=1900,
        max_value=2100,
        value=2024,
        help="Year of publication",
    )

# Ingestion
if uploaded_file:
    st.divider()

    # File info
    st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("🚀 Ingest Document", type="primary"):
        with st.spinner("Processing document..."):
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(uploaded_file.name).suffix,
            ) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            try:
                # Run ingestion
                stdout, stderr, returncode = run_ingestion(
                    tmp_path,
                    category or None,
                    tags or None,
                    year if year else None,
                )

                if returncode == 0:
                    st.success("✅ Ingestion complete!")
                    st.code(stdout, language="text")

                    # Show updated stats
                    st.balloons()
                else:
                    st.error("❌ Ingestion failed")
                    st.code(stderr, language="text")

            finally:
                # Cleanup temp file
                os.unlink(tmp_path)

# Recent Sources Table
st.divider()
st.subheader("Recent Sources")

mongo_stats = get_mongodb_stats()
if mongo_stats["connected"] and mongo_stats.get("recent_sources"):
    sources_data = []
    for src in mongo_stats["recent_sources"]:
        sources_data.append({
            "Title": src.get("title", "Untitled"),
            "Type": src.get("type", "-"),
            "Status": src.get("status", "-"),
            "Ingested": str(src.get("ingested_at", "-"))[:19],
        })
    st.table(sources_data)
else:
    st.caption("No sources ingested yet.")

# Footer
st.divider()
st.caption("Knowledge Pipeline | [Architecture](_bmad-output/architecture.md)")
