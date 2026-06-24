import json
import sys
from datetime import datetime

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

from config import Config, DateColumnSpec, DebitCreditSpec, ExcludeSpec


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def load_config(path: str) -> Config:
    with open(path) as f:
        return Config.model_validate(json.load(f))


def convert_dates(df: pd.DataFrame, date_columns: list[DateColumnSpec]) -> pd.DataFrame:
    for spec in date_columns:
        col = spec.source
        df[col] = df[col].apply(
            lambda v: datetime.strptime(str(v).strip(), spec.input_format).strftime(
                spec.output_format
            )
        )
    return df


def merge_debit_credit(df: pd.DataFrame, spec: DebitCreditSpec) -> pd.DataFrame:
    debit_col = spec.debit
    credit_col = spec.credit
    output_col = spec.output

    def compute(row):
        debit = str(row[debit_col]).strip()
        credit = str(row[credit_col]).strip()
        if debit and debit != "nan":
            return f"{float(debit):.2f}"
        elif credit and credit != "nan":
            return f"-{float(credit):.2f}"
        return ""

    df[output_col] = df.apply(compute, axis=1)
    return df


def filter_excluded_rows(df: pd.DataFrame, specs: list[ExcludeSpec], confirm: bool) -> pd.DataFrame:
    mask = pd.Series(False, index=df.index)
    for spec in specs:
        if spec.column in df.columns:
            mask |= df[spec.column].isin(spec.values)

    matched = df[mask]
    if matched.empty:
        return df

    if confirm:
        table = matched.fillna("").astype(str)
        widths = {col: max(len(col), table[col].str.len().max()) for col in table.columns}
        header = "  ".join(col.ljust(widths[col]) for col in table.columns)

        keep_indices = set()
        print(f"\n{len(matched)} row(s) matched exclusion rules:\n")
        for i, (idx, row) in enumerate(table.iterrows(), start=1):
            values = "  ".join(str(row[col]).ljust(widths[col]) for col in table.columns)
            if i == 1:
                print(f"    {header}")
            print(f"[{i}] {values}")
            answer = input("    Exclude? [Y/n]: ").strip().lower()
            if answer in ("n", "no"):
                keep_indices.add(idx)
            print()

        excluded = len(matched) - len(keep_indices)
        if excluded == 0:
            print("No rows excluded.")
            return df
        mask.loc[list(keep_indices)] = False
    else:
        excluded = len(matched)

    print(f"Excluded {excluded} row(s).")
    return df[~mask].reset_index(drop=True)


def apply_column_map(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    df = df.rename(columns=column_map)
    target_cols = list(column_map.values())
    return df[target_cols]


def get_sheet(spreadsheet_id: str, worksheet: str, credentials_file: str):
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(worksheet)


def align_to_sheet(df: pd.DataFrame, sheet_headers: list[str]) -> list[list]:
    rows = []
    for _, row in df.iterrows():
        aligned = [row.get(h, "") if h in df.columns else "" for h in sheet_headers]
        rows.append(aligned)
    return rows


def run(config_path: str, csv_path: str, credentials_file: str) -> None:
    config = load_config(config_path)

    if config.csv_headers:
        df = pd.read_csv(csv_path, dtype=str, header=None, names=config.csv_headers)
    else:
        df = pd.read_csv(csv_path, dtype=str)

    if config.debit_credit_columns:
        df = merge_debit_credit(df, config.debit_credit_columns)

    if config.exclude_rows:
        df = filter_excluded_rows(df, config.exclude_rows, config.confirm_exclusions)

    df = convert_dates(df, config.date_columns)
    df = apply_column_map(df, config.column_map)
    df = df.fillna("")

    sheet = get_sheet(config.sheet.spreadsheet_id, config.sheet.worksheet, credentials_file)

    sheet_headers = sheet.row_values(1)
    rows = align_to_sheet(df, sheet_headers)
    sheet.append_rows(rows, value_input_option=gspread.utils.ValueInputOption.user_entered)

    print(f"Wrote {len(df)} rows to '{config.sheet.worksheet}'.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py <config.json> <data.csv> <credentials.json>")
        sys.exit(1)

    run(sys.argv[1], sys.argv[2], sys.argv[3])
