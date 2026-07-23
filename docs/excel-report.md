# Excel Report

The Excel report is generated from the SQLite database.

The database is always the source of truth.

---

## Worksheets

### Machine Status

Contains machine status history.

Columns

- Timestamp
- Machine
- State

---

### Production by Hour

Contains hourly production.

Columns

- Date
- Hour
- Machine
- Produced Parts

---

### Production by Day

Contains daily production.

Columns

- Date
- Machine
- Shift 1
- Shift 2
- Total

---

## Refresh

The workbook is updated automatically whenever new production data is synchronized.