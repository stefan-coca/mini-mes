import sqlite3
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

REPORT_FOLDER = "/mnt/rdrive/Share/ProductionData"
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
# MACHINE STATUS
# =====================================

ws_status = wb.create_sheet("Machine Status")

ws_status.append([
    "Date",
    "Machine",
    "Pieces",
    "Running (min)",
    "Fault min)",
    "Stopped (min)",
    "Utilization (%)",
    "Pieces/Hour"
])

for cell in ws_status[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center")

ws_status.freeze_panes = "A2"
ws_status.auto_filter.ref = "A1:H1"

ws_status.column_dimensions["A"].width = 15
ws_status.column_dimensions["B"].width = 15
ws_status.column_dimensions["C"].width = 18
ws_status.column_dimensions["D"].width = 18
ws_status.column_dimensions["E"].width = 18
ws_status.column_dimensions["F"].width = 18
ws_status.column_dimensions["G"].width = 18
ws_status.column_dimensions["H"].width = 18

cursor.execute("""
SELECT
    DATE(start_time),
    machine,
    state,
    SUM(duration_sec)
FROM machine_state_events
GROUP BY
    DATE(start_time),
    machine,
    state
ORDER BY
    DATE(start_time),
    machine
""")

status_data = cursor.fetchall()

status_rows = {}

for date, machine, state, duration in status_data:

    key = (date, machine)

    if key not in status_rows:

        status_rows[key] = {
            "RUNNING": 0,
            "FAULT": 0,
            "STOPPED": 0
        }

    status_rows[key][state] = duration

cursor.execute("""
SELECT
    DATE(timestamp),
    machine,
    COUNT(*)
FROM production
GROUP BY
    DATE(timestamp),
    machine
""")

piece_data = cursor.fetchall()

piece_counts = {}

for date, machine, pieces in piece_data:

    piece_counts[
        (date, machine)
    ] = pieces

for (date, machine), values in sorted(status_rows.items()):

    running = values["RUNNING"] / 60
    fault = values["FAULT"] / 60
    stopped = values["STOPPED"] / 60

    pieces = piece_counts.get(
        (date, machine),
        0
    )

    # Availability = disponibilitate tehnica
    if (running + fault) > 0:

        availability = (
            running /
            (running + fault)
        ) * 100

    else:

        availability = 0

    # Utilization = utilizare reala
    # Utilization raportata la timpul planificat
    PLANNED_TIME_MIN = 960  # 06:00 - 22:00

    utilization = (
        running /
        PLANNED_TIME_MIN
    ) * 100

    # Piese / ora
    if running > 0:

        pieces_per_hour = ( pieces / (running / 60)
        )

    else:

        pieces_per_hour = 0

    ws_status.append([
        date,
        machine,
        pieces,
        round(running, 1),
        round(fault, 1),
        round(stopped, 1),
        round(utilization, 1),
        round(pieces_per_hour, 1)
    ])

# =====================================
# SHEET PER MASINA
# =====================================

for machine in machines:

    ws = wb.create_sheet(machine)

    ws.append([
        "Date",
        "Interval",
        "Shift",
        "Pieces"
    ])

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 12

    cursor.execute("""
    SELECT
        DATE(timestamp),
        STRFTIME('%H', timestamp),
        shift,
        COUNT(*)
    FROM production
    WHERE machine = ?
    GROUP BY
        DATE(timestamp),
        STRFTIME('%H', timestamp),
        shift
    ORDER BY
        DATE(timestamp),
        STRFTIME('%H', timestamp)
    """, (machine,))

    for row in cursor.fetchall():
        row = list(row)
        hour = int(row[1])
        row[1] = f"{hour:02d} - {hour+1:02d}"
        ws.append(row)

    for cell in ws["B"][1:]:
        cell.number_format = "00"

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

