"""
Upload Page - Document ingestion interface.
"""

import os
import tempfile
from pathlib import Path

import streamlit as st

# Load env before imports
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

from src.web.utils import (
    get_mongodb_stats,
    render_sidebar_stats,
    run_ingestion,
    run_extraction,
)
from src.extractors import ExtractionType

# Sidebar stats (page config is set by main web_app.py)
render_sidebar_stats()

# Main content
st.title("Upload Document")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Select File")

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

    # Auto-extract option
    auto_extract = st.checkbox(
        "Auto-extract after ingestion",
        value=False,
        help="Automatically run extraction after ingestion completes",
    )

# Ingestion
if uploaded_file:
    st.divider()

    # File info
    st.info(f"**{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("Ingest Document", type="primary"):
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(uploaded_file.name).suffix,
        ) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        try:
            with st.spinner("Processing document..."):
                stdout, stderr, returncode = run_ingestion(
                    tmp_path,
                    category or None,
                    tags or None,
                    year if year else None,
                )

            if returncode == 0:
                st.success("Ingestion complete!")
                st.code(stdout, language="text")

                # Auto-extract if enabled
                if auto_extract:
                    st.divider()
                    st.subheader("Auto-Extraction")

                    # Parse source_id from stdout (look for "Source ID:" line)
                    source_id = None
                    for line in stdout.split("\n"):
                        if "source_id" in line.lower() or "Source ID" in line:
                            # Try to extract the ID
                            parts = line.split(":")
                            if len(parts) >= 2:
                                source_id = parts[-1].strip()
                                break

                    if source_id:
                        with st.spinner("Running extraction..."):
                            try:
                                result = run_extraction(source_id)
                                st.success(
                                    f"Extraction complete! "
                                    f"Created {result.total_extractions} extractions "
                                    f"in {result.duration:.1f}s"
                                )

                                if result.extraction_counts:
                                    cols = st.columns(len(result.extraction_counts))
                                    for i, (ext_type, count) in enumerate(
                                        sorted(result.extraction_counts.items())
                                    ):
                                        cols[i].metric(ext_type.title(), count)
                            except Exception as e:
                                st.error(f"Extraction failed: {str(e)}")
                    else:
                        st.warning(
                            "Could not determine source ID from ingestion output. "
                            "Please run extraction manually from the Extract page."
                        )

                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Ingestion failed")
                st.code(stderr, language="text")

        finally:
            # Cleanup temp file
            os.unlink(tmp_path)
else:
    st.caption("Select a file to begin ingestion.")
