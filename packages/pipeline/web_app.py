"""
Knowledge Pipeline Web Interface
Multi-page Streamlit app for document ingestion, extraction, and search.

Run: uv run streamlit run web_app.py
"""

import os
from pathlib import Path

# Explicitly load .env BEFORE importing settings
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Knowledge Pipeline",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import shared utilities (AFTER loading .env)
from src.web.utils import render_sidebar_stats

# Render sidebar stats on all pages and store in session state
mongo_stats, qdrant_stats = render_sidebar_stats()

# Always update session state with fresh stats from sidebar render
st.session_state.mongo_stats = mongo_stats
st.session_state.qdrant_stats = qdrant_stats

# Main page content
st.title("Knowledge Pipeline")

st.markdown("""
Welcome to the Knowledge Pipeline! This tool helps you:

1. **Upload** - Ingest documents (PDF, Markdown, Word, HTML)
2. **Sources** - Manage your ingested sources
3. **Extract** - Run AI extraction to create structured knowledge
4. **Search** - Query your knowledge base

Use the sidebar to navigate between pages.
""")

# Quick stats
if mongo_stats["connected"]:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sources", mongo_stats["sources"])
    with col2:
        st.metric("Total Chunks", mongo_stats["chunks"])
    with col3:
        st.metric("Total Extractions", mongo_stats["extractions"])

# Footer
st.divider()
st.caption("Knowledge Pipeline | Built with Streamlit")
