"""
Sources Page - Source management with filters, details, and delete.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# Load env before imports
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

from src.web.utils import (
    delete_source,
    get_mongodb_stats,
    rename_source,
    render_sidebar_stats,
)

# Sidebar stats (page config is set by main web_app.py)
render_sidebar_stats()

# Main content
st.title("Source Management")

# Get fresh stats
mongo_stats = get_mongodb_stats()

if not mongo_stats["connected"]:
    st.error(f"Database not connected: {mongo_stats.get('error', 'Unknown')}")
    st.stop()

if not mongo_stats.get("recent_sources"):
    st.info("No sources ingested yet. Go to the Upload page to add documents.")
    st.stop()

# Filters
st.subheader("Filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    status_filter = st.selectbox(
        "Status",
        options=["All", "complete", "processing", "failed"],
    )

with filter_col2:
    type_filter = st.selectbox(
        "Type",
        options=["All", "book", "paper", "case_study", "reference"],
    )

with filter_col3:
    sort_by = st.selectbox(
        "Sort by",
        options=["Date (newest)", "Date (oldest)", "Title (A-Z)", "Extractions"],
    )

# Get extraction and chunk counts
extraction_counts = mongo_stats.get("extraction_counts_by_source", {})
extraction_breakdown = mongo_stats.get("extraction_breakdown_by_source", {})
chunk_counts = mongo_stats.get("chunk_counts_by_source", {})

# Build sources list with filtering
sources_data = []
source_ids = []

for src in mongo_stats["recent_sources"]:
    status = src.get("status", "-")
    src_type = src.get("type", "-")

    # Apply filters
    if status_filter != "All" and status != status_filter:
        continue
    if type_filter != "All" and src_type != type_filter:
        continue

    source_id = str(src.get("_id", ""))
    source_ids.append(source_id)
    sources_data.append({
        "Title": src.get("title", "Untitled"),
        "Type": src_type,
        "Status": status,
        "Chunks": chunk_counts.get(source_id, 0),
        "Extractions": extraction_counts.get(source_id, 0),
        "Ingested": str(src.get("ingested_at", "-"))[:19],
        "_id": source_id,
        "_breakdown": extraction_breakdown.get(source_id, {}),
        "_tags": src.get("tags", []),
        "_category": src.get("category", "-"),
    })

# Apply sorting
if sort_by == "Date (oldest)":
    sources_data = sorted(sources_data, key=lambda x: x["Ingested"])
elif sort_by == "Title (A-Z)":
    sources_data = sorted(sources_data, key=lambda x: x["Title"].lower())
elif sort_by == "Extractions":
    sources_data = sorted(sources_data, key=lambda x: x["Extractions"], reverse=True)
# Default: Date (newest) - already sorted from MongoDB

if not sources_data:
    st.info("No sources match the current filters.")
    st.stop()

# Create DataFrame for display
df = pd.DataFrame([{
    "Title": s["Title"],
    "Type": s["Type"],
    "Status": s["Status"],
    "Chunks": s["Chunks"],
    "Extractions": s["Extractions"],
    "Ingested": s["Ingested"],
} for s in sources_data])

st.divider()
st.subheader(f"Sources ({len(sources_data)} shown)")

# Editable table
edited_df = st.data_editor(
    df,
    column_config={
        "Title": st.column_config.TextColumn("Title", help="Click to edit", width="large"),
        "Type": st.column_config.TextColumn("Type", disabled=True),
        "Status": st.column_config.TextColumn("Status", disabled=True),
        "Chunks": st.column_config.NumberColumn("Chunks", disabled=True),
        "Extractions": st.column_config.NumberColumn("Extractions", disabled=True),
        "Ingested": st.column_config.TextColumn("Ingested", disabled=True),
    },
    hide_index=True,
    width='stretch',
    key="sources_table",
)

# Handle title edits
if not df["Title"].equals(edited_df["Title"]):
    for idx, (old_title, new_title) in enumerate(zip(df["Title"], edited_df["Title"])):
        if old_title != new_title and new_title.strip():
            source_id = sources_data[idx]["_id"]
            success, message = rename_source(source_id, new_title.strip())
            if success:
                st.success(message)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(message)

# Source Details Section
st.divider()
st.subheader("Source Details")

# Source selector for details
source_labels = {s["Title"]: s["_id"] for s in sources_data}
selected_source_label = st.selectbox(
    "Select a source to view details",
    options=list(source_labels.keys()),
)

if selected_source_label:
    selected_id = source_labels[selected_source_label]
    selected_source = next(s for s in sources_data if s["_id"] == selected_id)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Basic Info**")
        st.write(f"- **ID:** `{selected_id}`")
        st.write(f"- **Type:** {selected_source['Type']}")
        st.write(f"- **Status:** {selected_source['Status']}")
        st.write(f"- **Category:** {selected_source.get('_category', '-')}")
        st.write(f"- **Tags:** {', '.join(selected_source.get('_tags', [])) or '-'}")
        st.write(f"- **Ingested:** {selected_source['Ingested']}")

    with col2:
        st.markdown("**Content Stats**")
        st.write(f"- **Chunks:** {selected_source['Chunks']}")
        st.write(f"- **Total Extractions:** {selected_source['Extractions']}")

        breakdown = selected_source.get("_breakdown", {})
        if breakdown:
            st.markdown("**Extraction Breakdown:**")
            for ext_type, count in sorted(breakdown.items()):
                st.write(f"  - {ext_type}: {count}")

    # Delete button with confirmation
    st.divider()

    with st.expander("Danger Zone", expanded=False):
        st.warning("Deleting a source will permanently remove all chunks and extractions.")

        # Require typing "DELETE" for safety - not partial title which can be guessed
        st.caption(f"To delete **{selected_source['Title']}**, type DELETE below:")
        confirm_text = st.text_input(
            "Type 'DELETE' to confirm:",
            key="delete_confirm",
        )

        if st.button("Delete Source", type="secondary"):
            if confirm_text.strip().upper() == "DELETE":
                with st.spinner("Deleting..."):
                    success, message = delete_source(selected_id)

                if success:
                    st.success(message)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Type 'DELETE' to confirm. Deletion cancelled.")
