# Database

Mini-MES stores all production data in a SQLite database.

Database:

```
production.db
```

---

## production

Stores one record for every produced part.

Columns

| Column | Description |
|---------|-------------|
| id | Primary key |
| timestamp | Production timestamp |
| machine | Machine identifier |
| shift | Production shift |

---

## machine_status

Stores only the latest machine state.

| Column | Description |
|---------|-------------|
| machine | Primary key |
| state | Current machine state |
| last_update | Last state change |

Possible states

- RUNNING
- STOPPED
- FAULT

---

## machine_state_events

Stores complete machine history.

| Column | Description |
|---------|-------------|
| id | Primary key |
| machine | Machine identifier |
| state | Machine state |
| start_time | State start |
| end_time | State end |
| duration_sec | Duration |

---

## Relationships

One machine

↓

Many production events

↓

Many state history events

↓

One current status