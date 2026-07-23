import sqlite3
from datetime import datetime, time

DB_FILE = "production.db"

def get_current_shift():

    now = datetime.now().time()

    if time(6, 0) <= now < time(14, 0):
        return 1

    elif time(14, 0) <= now < time(22, 0):
        return 2

    else:
        return 3

def get_shift_count(machine, shift):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        SELECT COUNT(*)
        FROM production
        WHERE machine = ?
        AND DATE(timestamp) = ?
        AND shift = ?
    """, (machine, today, shift))

    count = cur.fetchone()[0]

    conn.close()

    return count

def get_machine_status():

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    cur.execute("""
        SELECT
            ms.machine,
            ms.state,
            (
                SELECT COUNT(*)
                FROM production p
                WHERE p.machine = ms.machine
            ) AS pieces
        FROM machine_status ms
        ORDER BY ms.machine
    """)

    rows = cur.fetchall()

    conn.close()

    result = []

    for r in rows:
        row = dict(r)

        row["shift1"] = get_shift_count(row["machine"], 1)
        row["shift2"] = get_shift_count(row["machine"], 2)

        result.append(row)

    return result
