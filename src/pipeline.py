"""Orchestrate CSV cleaning and output generation."""

from pathlib import Path

from src.config import load_config
from src.transform import (
    normalize_headers,
    coerce_record,
    enrich_record,
)
from src.validation import validate_records
from src.exporters import export_json, export_csv, export_parquet, save_quarantine


def run_pipeline(
    dataframe,
    config_path="config/schema.yaml",
    output_dir="data/output/parquet",
    quarantine_dir="data/quarantine",
    partition_col=None,
):
    """Process a DataFrame and return cleaned and rejected rows."""

    config = load_config(config_path)
    schema = config["columns"]

    cleaned_records = []
    rejected_records = []
    header_errors = []

    # Normalize headers once, before processing individual rows.
    try:
        original_columns = list(dataframe.columns)
        normalized_columns = [
            normalize_headers({column: column})[
                normalize_headers({column: column})[column]
            ]
            for column in original_columns
        ]

        if len(normalized_columns) != len(set(normalized_columns)):
            raise ValueError(
                "Multiple CSV columns normalize to the same name."
            )

        dataframe = dataframe.copy()
        dataframe.columns = normalized_columns

    except Exception as exc:
        header_errors.append(str(exc))

    if header_errors:
        raise ValueError("Invalid CSV headers: " + "; ".join(header_errors))

    # Process each row independently so bad rows do not stop the batch.
    for row_number, raw_record in enumerate(
        dataframe.to_dict(orient="records"),
        start=2,
    ):
        try:
            record = coerce_record(raw_record, schema)

            errors = validate_records(record, schema)

            if errors:
                raise ValueError("; ".join(errors))

            cleaned_records.append(
                enrich_record(
                    record,
                    config["project_title"],
                )
            )

        except (ValueError, TypeError, OverflowError) as exc:
            rejected = dict(raw_record)
            rejected["source_row"] = row_number
            rejected["error"] = str(exc)
            rejected_records.append(rejected)

    # Deduplicate only accepted records.
    deduplicate_columns = config.get(
        "deduplicate_on",
        ["record_id"],
    )

    if cleaned_records:
        import pandas as pd

        cleaned_df = pd.DataFrame(cleaned_records)

        missing_keys = [
            key for key in deduplicate_columns
            if key not in cleaned_df.columns
        ]

        if missing_keys:
            raise ValueError(
                f"Deduplication columns missing: {missing_keys}"
            )

        before = len(cleaned_df)

        cleaned_df = cleaned_df.drop_duplicates(
            subset=deduplicate_columns,
            keep="first",
        )

        cleaned_records = cleaned_df.to_dict(orient="records")
        duplicates_removed = before - len(cleaned_records)

    else:
        duplicates_removed = 0

    # Create exports.
    json_output = export_json(cleaned_records)
    csv_output = export_csv(cleaned_records)

    parquet_path = export_parquet(
        cleaned_records,
        output_dir,
        partition_col,
    )

    quarantine_path = save_quarantine(
        rejected_records,
        quarantine_dir,
    )

    summary = {
        "rows_seen": len(dataframe),
        "rows_cleaned": len(cleaned_records),
        "duplicates_removed": duplicates_removed,
        "rows_quarantined": len(rejected_records),
    }

    return {
        "records": cleaned_records,
        "rejected": rejected_records,
        "json": json_output,
        "csv": csv_output,
        "parquet_path": parquet_path,
        "quarantine_path": quarantine_path,
        "summary": summary,
    }