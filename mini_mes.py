import os
import time
import sqlite3
import json
import logging
from datetime import datetime, time, timedelta
import paho.mqtt.client as mqtt
import time as tm
import threading
import shutil
from logging.handlers import RotatingFileHandler

DB_FILE = "production.db"
LOCAL_FOLDER = "/home/admin/mini-mes/logs/"
LOG_FILE = f"{LOCAL_FOLDER}/mini_mes.log"
STATUS_FILE = f"{LOCAL_FOLDER}/machine_status.txt"
REMOTE_FOLDER = "/mnt/rdrive/Share/ProductionData"
REMOTE_LOG = f"{REMOTE_FOLDER}/mini_mes.log"
REMOTE_STATUS = f"{REMOTE_FOLDER}/machine_status.txt"

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

logger = logging.getLogger()

logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1024 * 1024,
    backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s"
)

handler.setFormatter(formatter)

logger.addHandler(handler)

logging.info("Mini-MES started")

fault_active = {}
last_piece_time = {}
machine_status = {}
state_start_time = {}

STOP_TIMEOUT = 270

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
# MACHINE STATUS
# ==================================================

def get_machine_status(machine):

    if fault_active.get(machine, False):
        return "FAULT"

    last_piece = last_piece_time.get(machine)

    if last_piece is None:
        return "STOPPED"

    delta = (
        datetime.now() - last_piece
    ).total_seconds()

    if delta > STOP_TIMEOUT:
        return "STOPPED"

    return "RUNNING"

# ==================================================
# STATE TRACKING
# ==================================================

def save_state_transition(machine, new_state):

    now = datetime.now()

    old_state = machine_status.get(machine)

    # prima stare observata
    if old_state is None:

        machine_status[machine] = new_state
        state_start_time[machine] = now

        db = sqlite3.connect(DB_FILE)
        cur = db.cursor()

        cur.execute("""
        INSERT INTO machine_status(machine, state, last_update)
        VALUES (?, ?, ?)
        ON CONFLICT(machine)
        DO UPDATE SET
            state = excluded.state,
            last_update = excluded.last_update
        """, (
            machine,
            new_state,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ))

        db.commit()
        db.close()

        update_status_file()

        logging.info(
            f"{machine}: None -> {new_state}"
        )

        return

    # nimic schimbat
    if old_state == new_state:
        return

    start_time = state_start_time[machine]

    duration = int(
        (now - start_time).total_seconds()
    )

    # Corectie pentru STOP_TIMEOUT
    if (
        old_state == "RUNNING"
        and new_state == "STOPPED"
    ):
        duration -= STOP_TIMEOUT

    if duration < 0:
        duration = 0

    db = sqlite3.connect(DB_FILE)
    cur = db.cursor()

    cur.execute("""
    INSERT INTO machine_state_events
    (
        machine,
        state,
        start_time,
        end_time,
        duration_sec
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        machine,
        old_state,
        start_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        now.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        duration
    ))

    cur.execute("""
    INSERT INTO machine_status(machine, state, last_update)
    VALUES (?, ?, ?)
    ON CONFLICT(machine)
    DO UPDATE SET
        state = excluded.state,
        last_update = excluded.last_update
    """, (
        machine,
        new_state,
        now.strftime("%Y-%m-%d %H:%M:%S")
    ))

    db.commit()
    db.close()

    logging.info(
        f"State saved: "
        f"{machine} "
        f"{old_state} "
        f"{duration}s"
    )

    logging.info(
        f"{machine}: "
        f"{old_state} -> {new_state}"
    )

    machine_status[machine] = new_state

    update_status_file()

    if (
        old_state == "RUNNING"
        and new_state == "STOPPED"
    ):
        state_start_time[machine] = (
            now - timedelta(seconds=STOP_TIMEOUT)
        )
    else:
        state_start_time[machine] = now

# ==================================================
# LOG PIECE DB
# ==================================================

def log_piece_db(machine):

    now = datetime.now()

    last_piece_time[machine] = now

    update_status_file()

    save_state_transition(
        machine,
        "RUNNING"
    )

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

        logging.info(
            f"Piece saved: {machine}"
        )

        print(
            f"Saved piece: {machine}"
        )

    except Exception as e:

        print("DB Error:", e)

        logging.error(
            f"DB Error: {e}"
        )

# ==================================================
# FAULT LOGGING
# ==================================================

def update_fault(machine, state):

    fault_active[machine] = state

    if state:

        save_state_transition(
            machine,
            "FAULT"
        )

    else:

        save_state_transition(
            machine,
            get_machine_status(machine)
        )

    logging.info(
        f"Fault {machine}: {state}"
    )

    print(
        f"FAULT {machine}: {state}"
    )

# ==================================================
# MQTT
# ==================================================

def on_connect(client, userdata, flags, rc, properties=None):

    print("MQTT Connected")

    logging.info(
        "MQTT Connected"
    )

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

        elif event == "fault":

            state = payload.get(
                "state",
                0
            )

            update_fault(
                machine,
                state == 1
            )

    except Exception as e:

        print("Error:", e)

        logging.error(
            f"Message error: {e}"
        )

# ==================================================
# STATUS MONITOR
# ==================================================

def status_monitor():

    while True:

        try:

            for machine in list(
                machine_status.keys()
            ):

                current_state = (
                    get_machine_status(
                        machine
                    )
                )

                save_state_transition(
                    machine,
                    current_state
                )

        except Exception as e:

            logging.error(
                f"Status monitor error: {e}"
            )

        tm.sleep(30)

# ==================================================
# STATUS FILE
# ==================================================

def update_status_file():

    lines = []

    lines.append("Machine Status")
    lines.append("================")
    lines.append("")

    machines = sorted(
        set(
            list(machine_status.keys())
            + list(last_piece_time.keys())
        )
    )

    for machine in machines:

        status = get_machine_status(
            machine
        )

        last_piece = (
            last_piece_time.get(machine)
        )

        if last_piece:

            last_piece_str = (
                last_piece.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        else:

            last_piece_str = "N/A"

        lines.append(
            f"{machine:<10}"
            f"{status:<10}"
            f"Last piece: "
            f"{last_piece_str}"
        )

    with open(
        STATUS_FILE,
        "w"
    ) as f:
        f.write(
            "\n".join(lines)
        )

    sync_files()

# ==================================================
# STATUS SYNC
# ==================================================

def sync_files():

    if not os.path.exists(REMOTE_FOLDER):
        return

    try:

        for file in os.listdir(LOCAL_FOLDER):

            if file.startswith("mini_mes.log"):

                shutil.copy2(
                    os.path.join(LOCAL_FOLDER, file),
                    os.path.join(REMOTE_FOLDER, file)
                )

        shutil.copy2(
            STATUS_FILE,
            REMOTE_STATUS
        )

    except Exception as e:

        logging.warning(
            f"Sync failed: {e}"
        )

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

threading.Thread(
    target=status_monitor,
    daemon=True
).start()

client.loop_forever()

