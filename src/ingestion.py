from io import BytesIO
import pandas as pd

def run_csv_file(uploaded_file):
    """ A function to injust the csv files"""
    if uploaded_file is None:
        raise ValueError
    file_bytes=uploaded_file.getvalue()

    # confirming the size of file
    if not file_bytes:
        raise ValueError("The file is Empty")

    # run the csvs safely
    try:
        df=pd.read_csv(BytesIO(file_bytes), dtype=str, keep_default_na=False, encoding="latin-1")
    except UnicodeEncodeError:
        df=pd.read_csv(BytesIO(file_bytes), dtype=str, keep_default_na=False, encoding="utf-8")
    if len(df.columns)==0:
        raise ValueError("There are no columns")
    if df.empty:
        raise ValueError("There are no rows")
    return df



