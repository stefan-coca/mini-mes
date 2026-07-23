# MQTT Topics

## Machine Status

```
factory/<machine>/status
```

Example

```
factory/A2/status
```

---

## Production Event

```json
{
    "machine":"A2",
    "event":"piece"
}
```

---

## Fault Event

```json
{
    "machine":"A2",
    "event":"fault",
    "state":1
}
```

---

## Fault Reset

```json
{
    "machine":"A2",
    "event":"fault",
    "state":0
}
```

---

## State Priority

```
FAULT
   ↓
RUNNING
   ↓
STOPPED
```

STOPPED is generated automatically after a configurable timeout without production.

---

## Future Topics

```
factory/<machine>/alarm

factory/<machine>/cycle

factory/<machine>/recipe

factory/<machine>/heartbeat
```