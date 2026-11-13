
import re
from io import BytesIO

import pandas as pd

from database.connection import get_engine


def clean_name(name):
    """Convert a name into a safe MySQL identifier."""
    name = str(name).strip().lower()
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    if not name:
        name = "column"

    if name[0].isdigit():
        name = f"col_{name}"

    return name[:60]


def clean_columns(df):
    """Clean column names and make duplicate names unique."""
    new_columns = []
    used = set()

    for column in df.columns:
        base = clean_name(column)
        name = base
        counter = 1

        while name in used:
            suffix = f"_{counter}"
            name = base[:64 - len(suffix)] + suffix
            counter += 1

        used.add(name)
        new_columns.append(name)

    df.columns = new_columns
    return df


def upload_csv_to_mysql(uploaded_file):
    """Read an uploaded CSV and create a new MySQL table."""

    # Read CSV with common encoding fallbacks
    file_bytes = uploaded_file.getvalue()

    try:
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(BytesIO(file_bytes), encoding="latin-1")

    if df.empty:
        raise ValueError("The uploaded CSV contains no data.")

    if len(df.columns) == 0:
        raise ValueError("The CSV does not contain any columns.")

    # Clean column names
    df = clean_columns(df)

    # Generate table name from uploaded filename
    filename = uploaded_file.name.rsplit(".", 1)[0]
    table_name = "uploaded_" + clean_name(filename)
    table_name = table_name[:64]

    engine = get_engine()

    try:
        # Create a new table; never overwrite an existing table
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="fail",
            index=False,
            chunksize=1000
        )

        return {
            "table_name": table_name,
            "rows": len(df),
            "columns": list(df.columns),
            "dataframe": df
        }

    finally:
        engine.dispose()
