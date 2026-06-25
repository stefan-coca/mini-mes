# Mini-MES

A lightweight Manufacturing Execution System (MES) designed for production monitoring using low-cost industrial hardware and open-source software.

Mini-MES collects production data directly from manufacturing equipment, stores it in a centralized database, and provides a foundation for production analytics, OEE calculations, and real-time monitoring.

---

## Project Goal

The goal of this project is to develop a simple and affordable MES solution that can be deployed in existing manufacturing environments without modifying machine PLC programs.

The system focuses on:

- Real-time production counting
- Centralized data collection
- Historical production tracking
- Low deployment cost
- Easy scalability

---

## System Architecture

```text
+-------------+
| PLC/Machine |
+-------------+
       |
       | Digital Output Pulse
       |
       v
+-------------+
|  ESP32-POE  |
+-------------+
       |
       | MQTT
       |
       v
+-------------+
| Raspberry Pi|
+-------------+
       |
       | SQLite
       |
       v
+-------------+
| Production  |
| Database    |
+-------------+

Future:
       |
       v
+-------------+
| Dashboard   |
| Reports     |
| OEE         |
+-------------+
```

---

## Technology Stack

### Hardware

- Raspberry Pi 4
- ESP32-POE
- Industrial PLCs
- Ethernet Network

### Software

- Python 3
- MQTT
- Mosquitto Broker
- SQLite
- Systemd
- Arduino Framework

---

## Current Features

### ESP32

- Production pulse counting
- MQTT publishing
- Ethernet communication
- Automatic reconnect

### Raspberry Pi

- MQTT subscriber
- Production event processing
- SQLite data storage
- Automatic startup via systemd

---

## Repository Structure

```text
mini-mes/
│
├── esp32/
│   └── esp32-poe_mqtt.ino
│
├── raspberry/
│   ├── mini_mes.py
│   ├── excel_exporter.py
│   ├── mini-mes.service
│   ├── production.db
│   │
│   └── ai-agent/
│       ├── chat.py
│       ├── mes_agent.py
│       ├── requirements.txt
│       └── ...
│
├── docs/
│   ├── architecture.md
│   ├── mqtt-topics.md
│   ├── database.md
│   ├── state-machine.md
│   └── excel-report.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

### Raspberry Pi

Update system:

```bash
sudo apt update
sudo apt upgrade -y
```

Install Mosquitto:

```bash
sudo apt install mosquitto mosquitto-clients -y
```

Enable service:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Logger

Manual execution:

```bash
python3 mini_mes_logger.py
```

---

## Running as a Service

Copy service file:

```bash
sudo cp mini-mes.service /etc/systemd/system/
```

Reload services:

```bash
sudo systemctl daemon-reload
```

Enable startup:

```bash
sudo systemctl enable mini-mes.service
```

Start service:

```bash
sudo systemctl start mini-mes.service
```

Check status:

```bash
sudo systemctl status mini-mes.service
```

View logs:

```bash
journalctl -u mini-mes.service -f
```

---

## MQTT Topics

Example:

```text
factory/machine1/production
```

Example payload:

```json
{
  "machine_id": "M1",
  "count": 1250,
  "timestamp": "2026-06-18T10:00:00"
}
```

---

## Database

Current storage engine:

```text
SQLite
```

Database file:

```text
production.db
```

Example schema:

```sql
CREATE TABLE production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine_id TEXT NOT NULL,
    count INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);
```

---

## Roadmap

### Phase 1 - Data Collection

- [x] ESP32 production counter
- [x] MQTT communication
- [x] Raspberry Pi data logger
- [x] SQLite database

### Phase 2 - Production Monitoring

- [x] Machine status tracking
- [x] Downtime detection
- [x] Shift tracking

### Phase 3 - Analytics

- [ ] OEE calculation
- [ ] Production KPIs
- [ ] Historical trends

### Phase 4 - Web Platform

- [ ] Web dashboard
- [ ] User authentication
- [ ] Multi-user access
- [ ] Report generation

### Phase 5 - Enterprise Integration

- [ ] PostgreSQL migration
- [ ] ERP integration
- [ ] REST API
- [ ] Cloud synchronization

---

## Design Principles

- Keep machine modifications to a minimum
- Use open-source technologies
- Support industrial Ethernet environments
- Maintain low deployment costs
- Enable gradual expansion

---

## License

Private project.