"""
Extract Page - Knowledge extraction with progress tracking.
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
    run_extraction,
)
from src.extractors import ExtractionType

# Sidebar stats (page config is set by main web_app.py)
render_sidebar_stats()

# Main content
st.title("Knowledge Extraction")

st.markdown("""
Extract structured knowledge from your ingested documents. The extraction process
analyzes document content and creates:

- **Decisions** - Architectural and design decisions with trade-offs
- **Patterns** - Reusable implementation patterns
- **Warnings** - Anti-patterns and pitfalls to avoid
- **Methodologies** - Step-by-step processes and workflows
""")

# Get fresh stats
mongo_stats = get_mongodb_stats()

if not mongo_stats["connected"]:
    st.error(f"Database not connected: {mongo_stats.get('error', 'Unknown')}")
    st.stop()

# Filter for completed sources only
extraction_counts = mongo_stats.get("extraction_counts_by_source", {})
extraction_breakdown = mongo_stats.get("extraction_breakdown_by_source", {})

completed_sources = [
    src for src in mongo_stats.get("recent_sources", [])
    if src.get("status") == "complete"
]

if not completed_sources:
    st.info("No completed sources available for extraction. Upload and ingest documents first.")
    st.stop()

st.divider()

# Source selection
st.subheader("Select Sources")

# Build options
source_options = {}
for src in completed_sources:
    source_id = str(src.get("_id", ""))
    title = src.get("title", "Untitled")
    count = extraction_counts.get(source_id, 0)
    source_options[f"{title} ({count} extractions)"] = source_id

# Single or batch mode
mode = st.radio(
    "Extraction mode",
    options=["Single source", "Batch (multiple sources)"],
    horizontal=True,
)

if mode == "Single source":
    selected_label = st.selectbox(
        "Choose a source",
        options=list(source_options.keys()),
    )
    selected_sources = [source_options[selected_label]] if selected_label else []
else:
    selected_labels = st.multiselect(
        "Choose sources (select multiple)",
        options=list(source_options.keys()),
    )
    selected_sources = [source_options[label] for label in selected_labels]

# Extraction type selection
st.subheader("Extraction Types")

extraction_type_labels = {
    "Decision": ExtractionType.DECISION,
    "Pattern": ExtractionType.PATTERN,
    "Warning": ExtractionType.WARNING,
    "Methodology": ExtractionType.METHODOLOGY,
}

col1, col2 = st.columns([2, 1])

with col1:
    selected_types = st.multiselect(
        "Select extraction types (leave empty for all)",
        options=list(extraction_type_labels.keys()),
        help="Selecting specific types can speed up extraction",
    )

with col2:
    st.info(
        "**Tip:** For comprehensive extraction, leave types empty to run all extractors."
    )

# Show current status for selected sources
if selected_sources:
    st.divider()
    st.subheader("Current Status")

    for source_id in selected_sources:
        # Find source info
        source_info = next(
            (s for s in completed_sources if str(s.get("_id")) == source_id),
            None,
        )
        if source_info:
            title = source_info.get("title", "Untitled")
            count = extraction_counts.get(source_id, 0)
            breakdown = extraction_breakdown.get(source_id, {})

            with st.expander(f"**{title}** - {count} extractions", expanded=len(selected_sources) == 1):
                if count > 0:
                    cols = st.columns(4)
                    for i, ext_type in enumerate(["decision", "pattern", "warning", "methodology"]):
                        cols[i].metric(
                            ext_type.title(),
                            breakdown.get(ext_type, 0),
                        )
                else:
                    st.caption("No extractions yet")

# Run extraction
st.divider()

if selected_sources:
    # Convert selected type labels to ExtractionType enum
    extractor_types = None
    if selected_types:
        extractor_types = [extraction_type_labels[t] for t in selected_types]

    type_str = ", ".join(selected_types) if selected_types else "all types"

    if st.button(
        f"Run Extraction ({len(selected_sources)} source{'s' if len(selected_sources) > 1 else ''})",
        type="primary",
    ):
        total_extractions = 0
        total_duration = 0.0
        all_counts: dict[str, int] = {}

        # Progress tracking
        progress_bar = st.progress(0, text="Starting extraction...")
        status_text = st.empty()
        results_container = st.container()

        for i, source_id in enumerate(selected_sources):
            # Find source title
            source_info = next(
                (s for s in completed_sources if str(s.get("_id")) == source_id),
                None,
            )
            title = source_info.get("title", "Unknown") if source_info else "Unknown"

            # Update progress
            progress = (i) / len(selected_sources)
            progress_bar.progress(progress, text=f"Extracting: {title}")
            status_text.write(f"Processing {i + 1} of {len(selected_sources)}: **{title}**")

            try:
                result = run_extraction(source_id, extractor_types)

                total_extractions += result.total_extractions
                total_duration += result.duration

                # Aggregate counts
                for ext_type, count in result.extraction_counts.items():
                    all_counts[ext_type] = all_counts.get(ext_type, 0) + count

                with results_container:
                    st.success(
                        f"**{title}**: {result.total_extractions} extractions "
                        f"in {result.duration:.1f}s"
                    )

            except Exception as e:
                with results_container:
                    st.error(f"**{title}**: Failed - {str(e)}")

        # Final progress
        progress_bar.progress(1.0, text="Complete!")
        status_text.empty()

        # Summary
        st.divider()
        st.subheader("Extraction Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Extractions", total_extractions)
        with col2:
            st.metric("Total Duration", f"{total_duration:.1f}s")

        if all_counts:
            st.write("**Breakdown by Type:**")
            cols = st.columns(len(all_counts))
            for i, (ext_type, count) in enumerate(sorted(all_counts.items())):
                cols[i].metric(ext_type.title(), count)

        st.cache_data.clear()
        st.balloons()
else:
    st.caption("Select one or more sources to run extraction.")
