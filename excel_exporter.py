import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

REPORT_FOLDER = "/mnt/rdrive/Share/miniMES"
EXCEL_FILE = f"{REPORT_FOLDER}/production_report.xlsx"
DB_FILE = "production.db"
EXPORT_STATUS_FILE = f"{REPORT_FOLDER}/last_export.txt"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Lista masinilor
cursor.execute("""
SELECT DISTINCT machine
FROM production
ORDER BY machine
""")

machines = [row[0] for row in cursor.fetchall()]

wb = Workbook()

# =====================================
# SUMMARY
# =====================================

ws_summary = wb.active
ws_summary.title = "Summary"

headers = ["Date", "Shift"] + machines

ws_summary.append(headers)

for cell in ws_summary[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center")

ws_summary.freeze_panes = "A2"
ws_summary.auto_filter.ref = ws_summary.dimensions

ws_summary.column_dimensions["A"].width = 15
ws_summary.column_dimensions["B"].width = 10

for col in range(3, len(headers) + 1):
    ws_summary.column_dimensions[
        chr(64 + col)
    ].width = 18

# =====================================
# SUMMARY DATA
# =====================================

cursor.execute("""
SELECT
    DATE(timestamp),
    shift,
    machine,
    COUNT(*)
FROM production
GROUP BY
    DATE(timestamp),
    shift,
    machine
ORDER BY
    DATE(timestamp),
    shift,
    machine
""")

summary_data = cursor.fetchall()

summary_rows = {}

for date, shift, machine, pieces in summary_data:

    key = (date, shift)

    if key not in summary_rows:
        summary_rows[key] = {}

    summary_rows[key][machine] = pieces

for (date, shift), values in sorted(summary_rows.items()):

    row = [date, shift]

    for machine in machines:
        row.append(values.get(machine, 0))

    ws_summary.append(row)

# =====================================
# SHEET PER MASINA
# =====================================

for machine in machines:

    ws = wb.create_sheet(machine)

    ws.append([
        "Timestamp",
        "Shift"
    ])

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 10

    cursor.execute("""
    SELECT
        timestamp,
        shift
    FROM production
    WHERE machine = ?
    ORDER BY timestamp
    """, (machine,))

    for row in cursor.fetchall():
        ws.append(row)

wb.save(EXCEL_FILE)

from datetime import datetime

with open(EXPORT_STATUS_FILE, "w") as f:

    f.write(
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

conn.close()

print(f"Created {EXCEL_FILE}")
