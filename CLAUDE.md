# CLAUDE.md

## Project: CSVDock

A Python tool that imports CSV files into Google Sheets with correct date
formatting and configurable column mapping.

## Problem it solves

Google Sheets misparses CSV dates on import (locale-dependent mm/dd/yyyy vs
yyyy-mm-dd ambiguity), and column orders/names don't always match between the
source CSV and the target sheet. This tool normalizes dates and maps columns
before writing to Sheets, so no manual cell-reformatting is needed.

## Stack

- Python 3
- `gspread` (Google Sheets API client)
- `pandas` (CSV parsing, date conversion)
- Config: JSON file defining column mapping + date formats

## Config file (`config.json`)

Defines, per import job:
- CSV column name → target Sheet column name mapping
- Source date format (e.g. `%m/%d/%Y`) → target format (`%Y-%m-%d`)
- Target spreadsheet ID + worksheet/tab name
- Any columns to skip/exclude

Example:

```json
{
  "spreadsheet_id": "your-sheet-id",
  "worksheet": "Expenses",
  "column_map": {
    "Date": "date",
    "Description": "description",
    "Amount": "amount"
  },
  "date_columns": [
    {
      "source": "Date",
      "input_format": "%m/%d/%Y",
      "output_format": "%Y-%m-%d"
    }
  ]
}
```

## Core flow

1. Load `config.json`
2. Read source CSV with `pandas`
3. Apply column mapping (rename/reorder/drop)
4. Convert date columns using explicit `input_format` → `output_format`
   (never rely on locale auto-detection)
5. Authenticate with Google Sheets API (service account JSON)
6. Write resulting rows to target worksheet via `gspread`

## Conventions

- All date conversion must use explicit `strptime`/`strftime` formats from
  config — never let pandas or Sheets auto-infer date formats.
- Config-driven: no hardcoded column names or sheet IDs in the script body.
- One config file per recurring import job (e.g. `expenses.json`,
  `mileage.json`) so the same script handles multiple CSV sources.

## Not yet decided

- Whether to append rows or overwrite the full sheet on each run
- Error handling for malformed/missing date values
