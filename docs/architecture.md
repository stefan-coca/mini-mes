# Mini-MES Architecture

## Overview

Mini-MES is a lightweight Manufacturing Execution System (MES) designed for small and medium-sized manufacturing companies.

The system collects production and machine state events from ESP32 devices connected to production equipment, stores them in a SQLite database and provides real-time monitoring through a Flask web dashboard.

The architecture is designed to be modular, scalable and easy to deploy on a Raspberry Pi.

---

## System Architecture

```text
                +------------------+
                |   PLC / Machine  |
                +------------------+
                         |
                  Digital Signals
                         |
                         v
                +------------------+
                |    ESP32-POE     |
                +------------------+
                         |
                        MQTT
                         |
                         v
              +----------------------+
              | Mosquitto MQTT Broker|
              +----------------------+
                         |
                         v
              +----------------------+
              | mini_mes.py          |
              |----------------------|
              | MQTT Subscriber      |
              | Event Processing     |
              | State Machine        |
              | SQLite Storage       |
              +----------------------+
                         |
             +-----------+-----------+
             |                       |
             v                       v
     +----------------+     +----------------+
     | production.db  |     | Excel Export   |
     +----------------+     +----------------+
             |
             v
     +----------------------+
     | Flask Web Dashboard  |
     +----------------------+
             |
             v
      Web Browser (Live View)
```

---

## Main Components

### ESP32

- Detects production pulses
- Detects machine faults
- Publishes MQTT messages

### Raspberry Pi

- MQTT subscriber
- Event processing
- Machine state tracking
- Shift calculation
- SQLite storage
- Excel export
- Flask REST API

### Dashboard

Displays in real time:

- Machine state
- Shift 1 production
- Shift 2 production
- Total production
- Live date and clock

Dashboard refresh interval: **2 seconds**

---

## Main Technologies

- ESP32 POE
- MQTT
- Mosquitto
- Python
- Flask
- SQLite
- Bootstrap 5
- JavaScript
- openpyxl
- Raspberry Pi OS