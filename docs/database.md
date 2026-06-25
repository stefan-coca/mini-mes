# Database

mini-MES stores all information in SQLite.

Database:

production.db

---

## production

Stores every produced part.

Columns

id

timestamp

machine

shift

Example

2026-06-25 08:13:22
A2
Shift 1

---

## machine_state_events

Stores machine state history.

Columns

id

machine

state

start_time

end_time

duration_sec

Possible states

RUNNING

FAULT

STOPPED

---

## Relationships

One machine

↓

Many production records

↓

Many state records
