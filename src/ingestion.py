
"""Read uploaded CSV files with robust parsing and error messages."""

from io import BytesIO
import pandas as pd


def read_uploaded_csv(uploaded_file):
    """Read an uploaded CSV file into a DataFrame."""

    if uploaded_file is None:
        raise ValueError("Please upload a CSV file.")

    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    encodings = ["utf-8-sig", "cp1252", "latin-1"]
    separators = [",", ";", "\t", "|"]

    last_error = None

    for encoding in encodings:
        for separator in separators:
            for engine in ["c", "python"]:
                try:
                    dataframe = pd.read_csv(
                        BytesIO(file_bytes),
                        sep=separator,
                        dtype=str,
                        keep_default_na=False,
                        encoding=encoding,
                        engine=engine,
                        on_bad_lines="error",
                        skipinitialspace=True,
                    )

                    if len(dataframe.columns) > 1:
                        dataframe.columns = [
                            str(column).strip()
                            for column in dataframe.columns
                        ]

                        if dataframe.empty:
                            raise ValueError(
                                "The CSV contains no data rows."
                            )

                        return dataframe

                except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
                    last_error = exc

    raise ValueError(
        "Unable to parse this CSV consistently. "
        "Check line 3 and other rows for extra commas, "
        "incorrect quotation marks, or inconsistent columns. "
        f"Last parser error: {last_error}"
    )
