# mini-MES Architecture

## Overview

mini-MES is a lightweight Manufacturing Execution System designed for small and medium manufacturing companies.

The system collects production events from ESP32 devices installed on production machines, stores them in a SQLite database and generates Excel production reports.

## Components

ESP32
│
├── Detects produced parts
├── Detects machine faults
└── Publishes MQTT events

↓

Mosquitto MQTT Broker

↓

mini_mes.py

├── Receives MQTT messages
├── Stores production events
├── Tracks machine state
├── Generates machine_status.txt

↓

SQLite

├── production
└── machine_state_events

↓

excel_exporter.py

↓

production_report.xlsx

## Main Technologies

- ESP32 POE
- MQTT
- Python
- SQLite
- openpyxl
- Linux (Raspberry Pi)

## Project Structure

esp32/
raspberry/
docs/
