from io import BytesIO
from typing import Any
import pandas as pd


def write_sheets(df_dict: dict[str, pd.DataFrame], fd_or_path: BytesIO | str, header_format: dict | None = "default"):
    writer = pd.ExcelWriter(fd_or_path, engine="xlsxwriter")

    sheet_names = shorten_sheet_names([sanitize_excel_sheet_name(n) for n in df_dict.keys()])
    for sheet_name, df in zip(sheet_names, df_dict.values()):
        has_index_name = any(df.index.names)
        write_sheet(df, writer, sheet_name=sheet_name, index=has_index_name, header_format=header_format)

    return writer


def write_sheet(
    df: pd.DataFrame,
    writer: pd.ExcelWriter,
    sheet_name: str = "Sheet1",
    index: bool = True,
    header_format: dict = "default",
    **kwargs: Any,
) -> None:
    """
    Write df as an excel file to ExcelWriter, roughly similar to `df.to_excel` except that it handles
    `df` with MultiIndex columns and `index=False`.
    """

    # Avoid the "NotImplementedError: Writing to Excel with MultiIndex columns"
    # exception by temporarily changing the columns to a single-level index
    columns: pd.Index = df.columns
    df.columns = range(len(df.columns))
    df.to_excel(
        writer,
        startrow=columns.nlevels,
        header=False,
        sheet_name=sheet_name,
        index=index,
        **kwargs,
    )
    df.columns = columns

    # Get the xlsxwriter workbook and worksheet objects.
    book = writer.book
    sheet = writer.sheets[sheet_name]

    # Add a header format.
    if header_format is not None:
        header_format = book.add_format(
            {"bold": True, "text_wrap": True, "valign": "top", "bottom": 1}
            if header_format == "default"
            else header_format
        )

    col_offset = df.index.nlevels if index else 0

    # Write the column headers with the defined format.
    for level in range(columns.nlevels):
        names = columns.get_level_values(level)
        prev_name = None
        last_name_change_i = 0
        for i, name in enumerate(names):
            if prev_name == name:
                next_name = names[i + 1] if len(names) > i + 1 else None
                if next_name != name:
                    sheet.merge_range(
                        level,
                        last_name_change_i + col_offset,
                        level,
                        i + col_offset,
                        name,
                        header_format,
                    )
                continue
            if not pd.isna(name):
                sheet.write(level, i + col_offset, name, header_format)
            last_name_change_i = i
            prev_name = name

    if index and any(df.index.names):
        for i, name in enumerate(df.index.names):
            sheet.write(df.columns.nlevels - 1, i, name or "", header_format)


def sanitize_excel_sheet_name(name: str) -> str:
    sanitized = name
    for char in "[]:*?/\\":
        sanitized = sanitized.replace(char, "_")
    return sanitized


def shorten_sheet_names(names_orig: list[str], max_length: int = 27, max_iter: int = 25) -> list[str]:
    suffixes = [0] * len(names_orig)
    names_final = [name[:max_length] for name in names_orig]
    iteration = 0
    while len(set(names_final)) < len(names_final) and iteration < max_iter:
        iteration += 1
        used = {}
        for i, name in enumerate(names_final):
            if names_final.count(name) > 1:
                number = used.get(name, 0) + 1
                used[name] = number
                suffixes[i] = number
        for i in range(len(names_orig)):
            suffix = f" ({str(suffixes[i])})" if suffixes[i] > 0 else ""
            if max_length - len(suffix) < 0:
                raise ValueError(f"Suffix of sheet name {suffix} is too long!")
            if len(names_orig[i]) > max_length - len(suffix):
                suffix = "..." + suffix
            names_final[i] = f"{names_orig[i][: max_length - len(suffix)]}{suffix}"
    if len(set(names_final)) < len(names_final):
        collisions = set([name for name in names_final if names_final.count(name) > 1])
        raise ValueError(f"The colliding sheet names could not be resolved. Collisions: {collisions}")
    return names_final


def parse_tabular_file(file, header=0):
    """Parse CSV, TSV, or XLSX file and return a pandas DataFrame."""
    filename = file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(file, header=header)
    elif filename.endswith(".tsv"):
        return pd.read_csv(file, sep="\t", header=header)
    elif filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(file, header=header)
    else:
        raise ValueError(f"Unsupported file type: {filename}")
