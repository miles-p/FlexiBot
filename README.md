# FlexiBot

![Build Status](https://github.com/miles-p/FlexiBot/actions/workflows/docker-compose.yml/badge.svg)

A containerized robot control system using MQTT for real-time communication between a web-based controller and monitoring dashboard.

## Purpose

FlexiBot provides a modular, microservices-based architecture for controlling and monitoring robotic systems. It enables:

- **Real-time motor control** via an intuitive web-based joystick interface
- **Live monitoring dashboard** with real-time data visualization and speed charts
- **Decoupled communication** using MQTT pub/sub messaging for reliability and scalability

## Architecture

```
┌─────────────────┐     MQTT      ┌─────────────────┐
│   Controller    │─────────────> |   Mosquitto     |
│   (Port 8081)   │   publish     │   MQTT Broker   │
└─────────────────┘               └────────┬────────┘
                                           │ subscribe
                                           ▼
                                  ┌─────────────────┐
                                  │    Dashboard    │
                                  │   (Port 8080)   │
                                  └─────────────────┘
```

### Framework & Technologies

| Component            | Technology                            | Purpose                                      |
| -------------------- | ------------------------------------- | -------------------------------------------- |
| **UI Framework**     | [NiceGUI](https://nicegui.io/)        | Python-based web UI with reactive components |
| **Messaging**        | [MQTT](https://mqtt.org/) (Mosquitto) | Lightweight pub/sub protocol for IoT         |
| **Containerization** | Docker Compose                        | Service orchestration and isolation          |
| **Charts**           | ECharts (via NiceGUI)                 | Real-time speed visualization                |

## Project Structure

```
FlexiBot/
├── docker-compose.yml          # Orchestrates all services
├── README.md
├── .github/
│   └── workflows/
│       └── docker-compose.yml  # CI pipeline for build validation
├── services/
│   ├── controller/             # Motor control interface
│   │   ├── Dockerfile
│   │   ├── main.py             # Joystick UI & MQTT publisher
│   │   └── requirements.txt
│   └── dashboard/              # Monitoring dashboard
│       ├── Dockerfile
│       ├── main.py             # Live data display & charts
│       └── requirements.txt
└── shared/
    └── mqtt.yaml               # MQTT topics & broker configuration
```

### File Descriptions

| File                          | Description                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| `docker-compose.yml`          | Defines the three services (mosquitto, controller, dashboard) and their networking                      |
| `services/controller/main.py` | NiceGUI app with dual joystick controls that publish motor speed values (−100 to 100) to MQTT topics    |
| `services/dashboard/main.py`  | NiceGUI app that subscribes to MQTT topics and displays live values with 30-second rolling speed charts |
| `shared/mqtt.yaml`            | Shared configuration defining MQTT broker address and topic mappings with friendly names                |

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Running the System

```bash
# Start all services
docker compose up --build

# Access the interfaces
# Controller: http://localhost:8081
# Dashboard:  http://localhost:8080
```

### Stopping the System

```bash
docker compose down
```

## MQTT Topics

Defined in `shared/mqtt.yaml`:

| Topic          | Description                 |
| -------------- | --------------------------- |
| `motor1/armed` | Motor 1 armed status        |
| `motor1/speed` | Motor 1 speed (−100 to 100) |
| `motor2/armed` | Motor 2 armed status        |
| `motor2/speed` | Motor 2 speed (−100 to 100) |

## Ports

| Service    | Port | Description          |
| ---------- | ---- | -------------------- |
| Mosquitto  | 1883 | MQTT broker          |
| Mosquitto  | 9001 | WebSocket (optional) |
| Dashboard  | 8080 | Monitoring UI        |
| Controller | 8081 | Control UI           |

## CI/CD

The GitHub Actions workflow (`.github/workflows/docker-compose.yml`) automatically builds and validates the Docker Compose configuration on every commit.
