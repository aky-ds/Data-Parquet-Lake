"""Export cleaned records to JSON, CSV, and Parquet."""

from pathlib import Path
import json
import pandas as pd


def export_json(records):
    """Return cleaned records as formatted JSON text."""

    return json.dumps(
        records,
        indent=2,
        ensure_ascii=False,
        default=str,
    )


def export_csv(records):
    """Return cleaned records as CSV text."""

    dataframe = pd.DataFrame(records)

    return dataframe.to_csv(index=False)


def export_parquet(records, output_dir, partition_col=None):
    """Write records to Parquet, optionally partitioned."""

    if not records:
        return None

    dataframe = pd.DataFrame(records)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    partition_columns = []

    if partition_col:
        if partition_col not in dataframe.columns:
            raise ValueError(
                f"Partition column '{partition_col}' does not exist."
            )

        if dataframe[partition_col].isna().any():
            raise ValueError(
                "Partition column contains missing values."
            )

        partition_columns = [partition_col]

    dataframe.to_parquet(
        destination,
        engine="pyarrow",
        index=False,
        partition_cols=partition_columns or None,
    )

    return str(destination)


def save_quarantine(records, output_dir):
    """Save invalid records with their error messages."""

    if not records:
        return None

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    output_path = destination / "bad_rows.csv"

    pd.DataFrame(records).to_csv(
        output_path,
        index=False,
    )

    return str(output_path)