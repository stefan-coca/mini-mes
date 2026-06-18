import sqlite3
import json
import logging
from datetime import datetime, time
import paho.mqtt.client as mqtt

DB_FILE = "production.db"
REPORT_FOLDER = "/mnt/rdrive/Share/miniMES"
STATUS_FILE = f"{REPORT_FOLDER}/mini_mes_status.txt"
LOG_FILE = f"{REPORT_FOLDER}/mini_mes.log"
EXPORT_STATUS_FILE = f"{REPORT_FOLDER}/last_export.txt"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    machine TEXT NOT NULL,
    shift INTEGER NOT NULL
)
""")

conn.commit()

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info("Mini-MES started")

# ==================================================
# SHIFT
# ==================================================

def get_shift(dt):

    t = dt.time()

    if time(6, 0) <= t < time(14, 0):
        return 1

    elif time(14, 0) <= t < time(22, 0):
        return 2

    else:
        return 3

# ==================================================
# STATUS
# ==================================================

def update_status(machine, shift):

    cursor.execute(
        "SELECT COUNT(*) FROM production"
    )

    row_count = cursor.fetchone()[0]

    with open(STATUS_FILE, "w") as f:
        last_export = "Unknown"

        try:

            with open(
                EXPORT_STATUS_FILE,
                "r"
            ) as ef:

                last_export = ef.read().strip()

        except:

            pass

        f.write("Mini-MES Status\n")
        f.write("====================\n\n")

        f.write(
            f"Last piece: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        f.write(
            f"Machine: {machine}\n"
        )

        f.write(
            f"Shift: {shift}\n"
        )

        f.write(
            f"Database rows: {row_count}\n"
        )

        f.write(
            f"Last Excel export: "
            f"{last_export}\n"
        )

        f.write(
            "Logger running: YES\n"
        )

# ==================================================
# LOG PIECE DB
# ==================================================

def log_piece_db(machine):

    now = datetime.now()

    shift = get_shift(now)

    try:

        cursor.execute(
            """
            INSERT INTO production
            (timestamp, machine, shift)
            VALUES (?, ?, ?)
            """,
            (
                now.strftime("%Y-%m-%d %H:%M:%S"),
                machine,
                shift
            )
        )

        conn.commit()

        update_status(machine, shift)

        print("Saved to SQLite")

        logging.info(
            f"Piece saved: {machine}"
        )

    except Exception as e:

        print("DB Error:", e)

        logging.error(
            f"DB Error: {e}"
        )

# ==================================================
# MQTT
# ==================================================

def on_connect(client, userdata, flags, rc, properties=None):

    print("MQTT Connected")

    logging.info("MQTT Connected")

    client.subscribe(
        "factory/+/status"
    )


def on_message(client, userdata, msg):

    try:

        payload = json.loads(
            msg.payload.decode()
        )

        machine = payload.get(
            "machine",
            "Unknown"
        )

        event = payload.get(
            "event",
            ""
        )

        if event == "piece":

            print(
                datetime.now(),
                machine,
                "piece"
            )

            log_piece_db(machine)

    except Exception as e:

        print("Error:", e)


# ==================================================
# START
# ==================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    "localhost",
    1883,
    60
)

client.loop_forever()
