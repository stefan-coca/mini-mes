# MQTT Topics

## Topic

factory/<machine>/status

Example:

factory/A2/status

---

## Piece Event

```json
{
    "machine": "A2",
    "event": "piece"
}
```

Meaning:

A new part has been produced.

---

## Fault Event

```json
{
    "machine": "A2",
    "event": "fault",
    "state": 1
}
```

Meaning:

Machine entered FAULT state.

---

## Fault Reset

```json
{
    "machine": "A2",
    "event": "fault",
    "state": 0
}
```

Meaning:

Machine fault cleared.

---

## State Priority

FAULT

↓

RUNNING

↓

STOPPED

STOPPED is detected automatically if no part is produced for more than STOP_TIMEOUT seconds.
