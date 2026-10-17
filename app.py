"""Streamlit interface for the CSV Cleaner and Parquet Lake."""

from pathlib import Path
import json

import pandas as pd
import streamlit as st

from src.pipeline import run_pipeline


st.set_page_config(
    page_title="CSV Cleaner | Comstech",
    page_icon="🗄️",
    layout="wide",
)

st.title("CSV Cleaner & Parquet Data Lake")
st.caption(
    "Upload a CSV, validate its schema, clean records, "
    "and export JSON, CSV, and Parquet."
)

# Create working directories.
Path("data/input").mkdir(parents=True, exist_ok=True)
Path("data/output/parquet").mkdir(parents=True, exist_ok=True)
Path("data/quarantine").mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.header("Pipeline Settings")

    config_path = st.text_input(
        "Schema configuration",
        value="config/schema.yaml",
    )

    partition_col = st.text_input(
        "Parquet partition column (optional)",
        value="",
        help="Example: city. Leave empty for an unpartitioned dataset.",
    ).strip()

    st.info(
        "Update config/schema.yaml to change required fields "
        "and data types."
    )

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
)

if uploaded_file is not None:
    st.subheader("Source Preview")

    try:
        # Use the same ingestion function as the processing pipeline.
        from src.ingestion import read_uploaded_csv

        source_df = read_uploaded_csv(uploaded_file)

        st.write(
            f"Rows: {len(source_df)} | "
            f"Columns: {len(source_df.columns)}"
        )

        st.dataframe(
            source_df.head(10),
            use_container_width=True,
        )

        if st.button(
            "Clean and Validate CSV",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Processing CSV records..."):
                try:
                    # Save the uploaded source for traceability.
                    input_path = (
                        Path("data/input") / uploaded_file.name
                    )
                    input_path.write_bytes(
                        uploaded_file.getvalue()
                    )

                    result = run_pipeline(
                        dataframe=source_df,
                        config_path=config_path,
                        output_dir="data/output/parquet",
                        quarantine_dir="data/quarantine",
                        partition_col=partition_col or None,
                    )

                    st.session_state["pipeline_result"] = result

                except Exception as exc:
                    st.error(f"Pipeline failed: {exc}")

    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")

result = st.session_state.get("pipeline_result")

if result:
    st.divider()
    st.subheader("Processing Summary")

    summary = result["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows Processed", summary["rows_seen"])
    col2.metric("Cleaned Records", summary["rows_cleaned"])
    col3.metric("Duplicates Removed", summary["duplicates_removed"])
    col4.metric("Rejected Rows", summary["rows_quarantined"])

    st.subheader("Cleaned Records")

    records = result["records"]

    if records:
        search = st.text_input(
            "Search cleaned records",
            placeholder="Search by name, city, or any field...",
        )

        visible_records = records

        if search:
            query = search.lower()

            visible_records = [
                record
                for record in records
                if query in json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                ).lower()
            ]

        st.write(
            f"Showing {len(visible_records)} of "
            f"{len(records)} cleaned records."
        )

        for index, record in enumerate(visible_records, start=1):
            with st.expander(
                f"Record {index} — {record.get('record_id', '')[:12]}"
            ):
                st.json(record)

        st.download_button(
            "Download cleaned JSON",
            data=result["json"],
            file_name="cleaned.json",
            mime="application/json",
            use_container_width=True,
        )

        st.download_button(
            "Download cleaned CSV",
            data=result["csv"],
            file_name="cleaned.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.dataframe(
            pd.DataFrame(records),
            use_container_width=True,
        )

        if result["parquet_path"]:
            st.success(
                "Parquet dataset saved to: "
                + result["parquet_path"]
            )

    else:
        st.warning(
            "No records passed validation. "
            "Review the quarantine output."
        )

    st.subheader("Rejected Rows")

    rejected = result["rejected"]

    if rejected:
        st.dataframe(
            pd.DataFrame(rejected),
            use_container_width=True,
        )

        st.download_button(
            "Download rejected rows",
            data=pd.DataFrame(rejected).to_csv(index=False),
            file_name="bad_rows.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.success("No invalid rows were found.")

    with st.expander("View complete JSON output"):
        st.code(result["json"], language="json")