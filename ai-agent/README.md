# mini-MES AI Agent

## Overview

This project is an AI Agent built on top of the mini-MES system.

The agent has read-only access to:

* SQLite production database (`production.db`)
* Machine status file (`machine_status.txt`)
* System logs (`mini_mes.log`)

The goal is to allow natural language interaction with the MES system.

Example questions:

* How many parts were produced today?
* What is the current machine status?
* When was the last part produced?
* How much fault time occurred today?
* How is production performing today?

---

## Architecture

```text
User
  |
  v
GPT-5
  |
  v
Tool Calling
  |
  +------------------+
  |                  |
  v                  v

production.db    mini_mes.log
machine_status.txt

  |
  v

tools.py
```

---

## Project Structure

```text
ai-agent/
│
├── mes_agent.py
├── tools.py
├── config.py
├── test_tools.py
├── requirements.txt
└── README.md
```

---

## Files

### config.py

Contains paths to all data sources:

* production.db
* machine_status.txt
* mini_mes.log

---

### tools.py

Contains all functions available to the AI agent.

Current tools:

* get_today_count()
* get_last_piece()
* get_machine_status()
* get_fault_today()
* get_recent_logs()

All functions operate in read-only mode.

---

### mes_agent.py

Main AI Agent application.

Responsibilities:

* Receive user questions
* Send requests to GPT
* Allow GPT to select the required tools
* Execute tool functions
* Send tool results back to GPT
* Generate a final answer

---

## How It Works

Example:

User asks:

> What is the current machine status?

Workflow:

1. GPT selects `get_machine_status()`
2. Python executes the function
3. The status file is read
4. The result is returned to GPT
5. GPT generates the final response

---

## Tool Calling

The agent uses OpenAI native Tool Calling.

GPT decides:

* Which function should be called
* How many functions should be called

Example:

User asks:

> How is production performing today?

GPT may choose:

* get_today_count()
* get_machine_status()
* get_last_piece()
* get_fault_today()
* get_recent_logs()

The tool results are aggregated and used to generate a single response.

---

## Safety

The agent is configured in read-only mode.

It never performs:

* INSERT
* UPDATE
* DELETE

It does not modify:

* production.db
* machine_status.txt
* mini_mes.log

The agent only reads and analyzes existing data.

---

## Requirements

Python 3

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Agent

Activate virtual environment:

```bash
source venv/bin/activate
```

Start the agent:

```bash
python3 mes_agent.py
```

Exit the application:

```text
exit
```

---

## Current Features (v0.1)

* SQLite integration
* Machine status integration
* Log file integration
* OpenAI GPT-5 integration
* Native Tool Calling
* Production monitoring
* Fault monitoring
* Natural language queries

---

## Roadmap

### v0.2

* get_state_events_today()
* Fault analysis
* Downtime analysis

### v0.3

* get_shift_production(shift)
* get_shift_summary(shift)

### v0.4

* analyze_last_hour()
* diagnose_machine()

### v1.0

* AI Production Assistant
* Automatic diagnostics
* Shift summaries
* Fault root-cause explanations
* Production insights and recommendations

---

## Author

Created as an experimental AI layer on top of the mini-MES project to learn and explore:

* Python
* SQLite
* MQTT
* Industrial data collection
* AI Agents
* OpenAI Tool Calling
* Production monitoring systems
