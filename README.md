# CSVDock

Imports CSV files into Google Sheets with correct date formatting and configurable column mapping.

## Requirements

- Python 3.11+
- [Pkl](https://pkl-lang.org) (`brew install pkl`)
- A Google Cloud service account with Sheets and Drive APIs enabled

## Setup

**1. Clone and create a virtual environment:**
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Get Google credentials:**
- Create a service account in [Google Cloud Console](https://console.cloud.google.com)
- Enable Google Sheets API and Google Drive API
- Download the service account JSON key and save it as `credentials.json` in the project folder
- Share your target Google Sheet with the service account's email (Editor access)

## Configuration

Config is defined in Pkl and compiled to `config.json` at run time. The schema lives in `config/schema/Config.pkl`. Each import job gets its own `.pkl` file in `config/`:

```
config/
  schema/Config.pkl   # type schema — edit this to add new fields
  main.pkl            # your import job — amends the schema
```

**`config/main.pkl` example:**
```pkl
amends "schema/Config.pkl"

sheet = new GoogleSheetSpec {
  spreadsheet_id = "your-spreadsheet-id"
  worksheet = "Sheet1"
}

csv_headers = new Listing<String> { "date"; "shop"; "debit"; "credit"; "balance" }

column_map = new Mapping<String, String> {
  ["date"] = "date"
  ["shop"] = "shop"
  ["amount"] = "amount"
}

date_columns = new Listing<DateColumnSpec> {
  new {
    source = "date"
    input_format = "%m/%d/%Y"
    output_format = "%Y-%m-%d"
  }
}
```

- **`sheet`** — target spreadsheet ID and worksheet/tab name
- **`csv_headers`** — optional, define column names if your CSV has no header row
- **`debit_credit_columns`** — optional, merge separate debit/credit columns into one signed amount
- **`column_map`** — maps CSV column names to sheet column names; only mapped columns are written
- **`date_columns`** — columns to reformat, with explicit `input_format`/`output_format` strings

To add a new import job (e.g. mileage), create `config/mileage.pkl` and pass it as the second argument to `run.sh`.

## Usage

```bash
./run.sh data.csv                      # uses config/main.pkl
./run.sh data.csv config/mileage.pkl   # use a different config
```

`run.sh` compiles the Pkl config to `config.json` then runs the import. `credentials.json` must be present in the project folder.

## Next time

The venv only needs to be created once. On subsequent sessions just activate it:

```bash
source venv/bin/activate
```
