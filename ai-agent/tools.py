import sqlite3
from config import DB_FILE, STATUS_FILE, LOG_FILE


def get_today_count():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM production
        WHERE DATE(timestamp)=DATE('now','localtime')
    """)

    result = cur.fetchone()[0]

    conn.close()

    return result


def get_last_piece():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp
        FROM production
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    conn.close()

    return row[0] if row else None


def get_fault_today():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(duration_sec),0)
        FROM machine_state_events
        WHERE state='FAULT'
        AND DATE(start_time)=DATE('now','localtime')
    """)

    result = cur.fetchone()[0]

    conn.close()

    return round(result / 60, 1)


def get_machine_status():

    with open(STATUS_FILE, "r") as f:
        return f.read()


def get_recent_logs(lines=50):

    with open(LOG_FILE, "r") as f:
        return "".join(f.readlines()[-lines:])

def get_system_snapshot():

    return {
        "status": get_machine_status(),
        "pieces_today": get_today_count(),
        "last_piece": get_last_piece(),
        "fault_today": get_fault_today()
    }

def get_state_events_today():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            state,
            start_time,
            end_time,
            duration_sec
        FROM machine_state_events
        WHERE DATE(start_time)=DATE('now','localtime')
        ORDER BY start_time
    """)

    rows = cur.fetchall()

    conn.close()

    return rows
