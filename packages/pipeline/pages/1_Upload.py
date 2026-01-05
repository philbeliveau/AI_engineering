"""
Upload Page - Document ingestion interface.
"""

import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import requests
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

# Input method selection
input_method = st.radio(
    "Input method",
    options=["Upload File", "Fetch from URL"],
    horizontal=True,
)

col1, col2 = st.columns([2, 1])

with col1:
    if input_method == "Upload File":
        st.subheader("Select File")
        uploaded_file = st.file_uploader(
            "Drag and drop a file here",
            type=["pdf", "md", "markdown", "docx", "html", "pptx"],
            help="Supported formats: PDF, Markdown, Word, HTML, PowerPoint",
        )
        url_input = None
    else:
        st.subheader("Web Page URL")
        url_input = st.text_input(
            "Enter URL",
            placeholder="https://example.com/article",
            help="Paste a URL to fetch and ingest the web page",
        )
        uploaded_file = None

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
def run_auto_extraction(stdout: str):
    """Run auto-extraction if enabled and source_id found."""
    if not auto_extract:
        return

    st.divider()
    st.subheader("Auto-Extraction")

    # Parse source_id from stdout (look for "Source ID:" line)
    source_id = None
    for line in stdout.split("\n"):
        if "source_id" in line.lower() or "Source ID" in line:
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


# Handle file upload
if uploaded_file:
    st.divider()
    st.info(f"**{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("Ingest Document", type="primary"):
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
                run_auto_extraction(stdout)
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Ingestion failed")
                st.code(stderr, language="text")
        finally:
            os.unlink(tmp_path)

# Handle URL input
elif url_input:
    st.divider()

    # Validate URL
    try:
        parsed = urlparse(url_input)
        if not parsed.scheme or not parsed.netloc:
            st.error("Please enter a valid URL (e.g., https://example.com)")
            st.stop()
    except Exception:
        st.error("Invalid URL format")
        st.stop()

    st.info(f"**URL:** {url_input}")

    if st.button("Fetch & Ingest", type="primary"):
        try:
            # Fetch the web page
            with st.spinner("Fetching web page..."):
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; KnowledgePipeline/1.0)"
                }
                response = requests.get(url_input, headers=headers, timeout=30)
                response.raise_for_status()

            # Save to temp HTML file
            domain = parsed.netloc.replace(".", "_")
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".html",
                prefix=f"{domain}_",
            ) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            try:
                with st.spinner("Processing web page..."):
                    stdout, stderr, returncode = run_ingestion(
                        tmp_path,
                        category or None,
                        tags or None,
                        year if year else None,
                    )

                if returncode == 0:
                    st.success("Ingestion complete!")
                    st.code(stdout, language="text")
                    run_auto_extraction(stdout)
                    st.balloons()
                    st.cache_data.clear()
                else:
                    st.error("Ingestion failed")
                    st.code(stderr, language="text")
            finally:
                os.unlink(tmp_path)

        except requests.exceptions.Timeout:
            st.error("Request timed out. The website took too long to respond.")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP error: {e.response.status_code} - {e.response.reason}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch URL: {str(e)}")

else:
    st.caption("Select a file or enter a URL to begin ingestion.")
