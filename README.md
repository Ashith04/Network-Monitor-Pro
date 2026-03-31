# 🛰️ Network Monitor Pro

> A real-time network monitoring dashboard built with Python and Streamlit that provides enterprise-grade visibility into device health, traffic analytics, packet inspection, and alerting — all from a single, premium dark-themed interface.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Usage](#-usage)
- [Features](#-features)
- [Architecture](#-architecture)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💻 Installation

To get a local copy up and running, follow these steps:

### Prerequisites

- **Python 3.10+** installed on your system
- **pip** (Python package manager)

### Steps

1. **Clone the repo:**
   ```sh
   git clone https://github.com/your_username/Network-Monitor.git
   cd Network-Monitor
   ```

2. **Create a virtual environment (recommended):**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure alerts (optional):**
   
   Create a `.env` file in the root directory for email/Slack alerting:
   ```env
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECEIVER=receiver@gmail.com
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
   > **Note:** The dashboard works perfectly without a `.env` file — it defaults to simulation mode for alerts.

---

## 🛠️ Usage

Start the dashboard with a single command:

```sh
python -m streamlit run dashboard.py
```

The dashboard will open automatically at `http://localhost:8501`.

### Optional: Live Packet Capture

To enable **real** packet capture (instead of simulation mode), run the terminal as **Administrator**:

```sh
# Right-click Terminal → "Run as Administrator"
python -m streamlit run dashboard.py
```

> Without Administrator privileges, the Packets page runs in **Interactive Simulation Mode**, generating synthetic traffic to demonstrate the UI.

---

## ✨ Features

### 📊 Dashboard (Overview)
- **Device Health Status** — Real-time ping monitoring with latency, online/offline status, and health scores
- **Overview / Alerts / Traffic / Trends** — Tabbed sub-views for quick operational insight
- **System Telemetry** — Sidebar metrics showing device count, database size, record totals, and flow counts

### 🖥️ Devices
- Full device inventory with IP, status, latency, and health index
- Color-coded badges: `ONLINE` (green), `OFFLINE` (red)
- Live ping diagnostics per device

### 🚨 Alerts
- **Multi-channel alerting** — Email (SMTP) and Slack webhook integration
- **Severity classification** — CRITICAL, HIGH, MEDIUM, LOW, INFO
- **Test broadcasting** — Dispatch test alerts to verify integrations
- Comprehensive alert log with color-coded severity indicators

### 📡 Traffic Analysis
- **Live system metrics** via `psutil` — Total Sent/Received, Active Connections, Listening Ports
- **Active Connections table** — Real-time ESTABLISHED connections with local/remote IPs and PIDs
- **Network Interfaces** — Per-NIC bandwidth, packet counts, and error rates
- **Visual analytics** — Protocol Distribution donut chart and Bandwidth by Interface bar chart

### 📝 Reports
- **Intelligence Documentation** — Generate data-driven reports on demand
- Report types: Device Summary, Alert Summary, Traffic Summary, Health Report
- Dynamic metrics, summary cards, and data tables

### 🔬 Packet Capture (Deep Packet Analytics)
- **Live packet interception** with protocol-aware coloring (TCP, UDP, ICMP, DNS, HTTP)
- **Wireshark-style UI** — Sortable packet table with source/destination IPs, ports, and payload preview
- **Frame scrubber** — Slider to navigate captured packet history
- **Auto-simulation fallback** — Generates synthetic traffic when Administrator privileges are unavailable

### 🎨 UI/UX
- Premium dark NOC-style theme with cyan/blue accent palette
- Responsive layout with glassmorphism elements
- High-contrast text and buttons for accessibility
- Smooth gradient headers and styled interactive elements

---

## 🏗️ Architecture

```
Network-Monitor/
├── dashboard.py          # Main Streamlit UI — all 6 views rendered here
├── database.py           # SQLite database layer (ping, SNMP, flow, alert, device tables)
├── packet_capture.py     # Raw socket packet capture engine with simulation fallback
├── advanced_alerts.py    # Email alerting system with severity classification
├── alert_testing.py      # Alert channel testing and dispatch utilities
├── config.py             # Environment config loader (.env integration)
├── health_score.py       # Device health score computation
├── slack_integration.py  # Slack webhook alert delivery
├── webhook_alerts.py     # Generic webhook alert sender
├── requirements.txt      # Python dependencies
├── logs/                 # SQLite database storage
│   └── network_monitor.db
└── README.md             # You are here
```

### Tech Stack

| Layer        | Technology                       |
|-------------|----------------------------------|
| **Frontend** | Streamlit, Plotly, CSS           |
| **Backend**  | Python 3.10+, psutil, ping3     |
| **Database** | SQLite3                          |
| **Alerting** | SMTP (Gmail), Slack Webhooks     |
| **Packets**  | Raw Sockets / Simulation Engine  |

---

## 📸 Screenshots

> Run `python -m streamlit run dashboard.py` and explore each tab to see the interface in action.

- **Dashboard** — Device health overview with latency metrics and health scores
- **Traffic** — Live bandwidth charts and active connection tables
- **Packets** — Wireshark-style packet capture with protocol coloring
- **Reports** — On-demand intelligence documentation generator

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. **Fork** the repository
2. **Create** your feature branch:
   ```sh
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** your changes:
   ```sh
   git commit -m "Add some AmazingFeature"
   ```
4. **Push** to the branch:
   ```sh
   git push origin feature/AmazingFeature
   ```
5. **Open** a Pull Request

### Guidelines
- Follow existing code style and naming conventions
- Test your changes locally before submitting
- Keep pull requests focused on a single feature or fix
- Update documentation if your changes affect usage

---

## 📄 License

Distributed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Network Monitor Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Built with ❤️ using Python & Streamlit
</p>
