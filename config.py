from pydantic import BaseModel


class DebitCreditSpec(BaseModel):
    debit: str
    credit: str
    output: str


class DateColumnSpec(BaseModel):
    source: str
    input_format: str
    output_format: str


class ExcludeSpec(BaseModel):
    column: str
    values: list[str]


class GoogleSheetSpec(BaseModel):
    spreadsheet_id: str
    worksheet: str


class Config(BaseModel):
    sheet: GoogleSheetSpec
    csv_headers: list[str] | None = None
    debit_credit_columns: DebitCreditSpec | None = None
    column_map: dict[str, str]
    date_columns: list[DateColumnSpec]
    exclude_rows: list[ExcludeSpec] = []
    confirm_exclusions: bool = True
