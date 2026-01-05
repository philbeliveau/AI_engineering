"""
Search Page - Semantic search across the knowledge base.
"""

from pathlib import Path

import streamlit as st

# Load env before imports
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

from src.web.utils import (
    get_mongodb_stats,
    render_sidebar_stats,
    search_knowledge,
)

# Sidebar stats (page config is set by main web_app.py)
render_sidebar_stats()

# Main content
st.title("Knowledge Search")

st.markdown("""
Search your knowledge base using natural language. The search uses semantic similarity
to find relevant extractions across all your ingested documents.
""")

# Get stats for source filter
mongo_stats = get_mongodb_stats()

if not mongo_stats["connected"]:
    st.error(f"Database not connected: {mongo_stats.get('error', 'Unknown')}")
    st.stop()

if mongo_stats.get("extractions", 0) == 0:
    st.info("No extractions in the knowledge base yet. Run extraction on your sources first.")
    st.stop()

# Search interface
st.divider()

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Search query",
        placeholder="e.g., How to implement RAG with vector databases?",
        help="Enter a natural language question or topic",
    )

with col2:
    limit = st.number_input(
        "Max results",
        min_value=5,
        max_value=50,
        value=20,
        help="Maximum number of results to return",
    )

# Filters
st.subheader("Filters")
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    extraction_types = ["All", "decision", "pattern", "warning", "methodology"]
    selected_type = st.selectbox(
        "Extraction type",
        options=extraction_types,
    )

with filter_col2:
    # Build source options
    source_options = {"All sources": None}
    for src in mongo_stats.get("recent_sources", []):
        source_id = str(src.get("_id", ""))
        title = src.get("title", "Untitled")
        source_options[title] = source_id

    selected_source_label = st.selectbox(
        "Source",
        options=list(source_options.keys()),
    )

# Search button
if st.button("Search", type="primary", disabled=not query):
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching..."):
            try:
                # Apply filters
                extraction_type = None if selected_type == "All" else selected_type
                source_id = source_options[selected_source_label]

                results = search_knowledge(
                    query=query,
                    limit=limit,
                    extraction_type=extraction_type,
                    source_id=source_id,
                )

                if not results:
                    st.info("No results found. Try a different query or adjust filters.")
                else:
                    st.success(f"Found {len(results)} results")

                    st.divider()

                    for i, result in enumerate(results, 1):
                        payload = result.get("payload", {})
                        score = result.get("score", 0)
                        ext_type = payload.get("extraction_type", "unknown")

                        # Result card
                        with st.expander(
                            f"**{i}. {payload.get('extraction_title', 'Untitled')}** "
                            f"[{ext_type.upper()}] "
                            f"(Score: {score:.3f})",
                            expanded=i <= 3,  # Expand first 3
                        ):
                            # Metadata row
                            meta_col1, meta_col2, meta_col3 = st.columns(3)
                            with meta_col1:
                                st.caption(f"**Type:** {ext_type}")
                            with meta_col2:
                                st.caption(f"**Source:** {payload.get('source_title', '-')}")
                            with meta_col3:
                                topics = payload.get("topics", [])
                                if topics:
                                    st.caption(f"**Topics:** {', '.join(topics[:5])}")

                            st.divider()

                            # Content
                            content = payload.get("content", "")
                            if content:
                                st.markdown(content)
                            else:
                                st.caption("No content available")

                            # Additional metadata
                            with st.expander("Raw metadata"):
                                st.json({
                                    k: v for k, v in payload.items()
                                    if k not in ["content", "embedding"]
                                })

            except Exception as e:
                st.error(f"Search failed: {str(e)}")

# Tips
st.divider()
with st.expander("Search Tips"):
    st.markdown("""
    - **Be specific**: "RAG chunking strategies" works better than just "RAG"
    - **Use questions**: "How do I handle rate limiting?" finds relevant patterns
    - **Filter by type**: Use the extraction type filter to find specific knowledge:
        - **Decisions**: Architectural choices and trade-offs
        - **Patterns**: Reusable implementation approaches
        - **Warnings**: Common pitfalls and anti-patterns
        - **Methodologies**: Step-by-step processes
    - **Filter by source**: Narrow down to a specific book or paper
    """)
