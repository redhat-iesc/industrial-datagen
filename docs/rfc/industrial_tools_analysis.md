# Industrial Tools & Open Source Alternatives Analysis
**Project:** Turnkey Operational Technology (OT) Assistant  
**Date:** April 17, 2026  
**Source:** John / Melvin IESC Sync Notes

## 1. Proprietary Tools vs. Open Source Alternatives

The following table identifies the specific industrial tools mentioned in the meeting and provides corresponding open-source or flexible alternatives to achieve the same objectives.

| Category | Proprietary Tool / Application | Open Source / Flexible Alternative |
| :--- | :--- | :--- |
| **Data Historian** | **OSIsoft PI**: The industry standard for high-volume bulk data. | **InfluxDB**, **TimescaleDB** (PostgreSQL-based), or **VictoriaMetrics**. |
| **SCADA & MES** | **Ignition** (with **Sepasoft**), **Critical Manufacturing**, and **Corber**. | **Apache OFBiz**, **Fledge**, or custom OEE dashboards on **Grafana**. |
| **Asset Management** | **IBM Maximo**: Used for workforce and field asset management. | **Apache OFBiz** or custom integration via **MCP (Model Context Protocol)** wrappers. |
| **OT AI Models** | **Palantir** and **Edgecale AI**: Specialized OT foundational models. | **Grid FM** (LF Energy project) or custom models hosted on **OpenShift AI**. |
| **Development IDE** | **Claude Desktop**, **Cursor**, and **Warp**. | **VS Code (OSS)**, **Ollama** (for local models), and **Llama 3**. |

---

## 2. Technical Requirements & Protocols

To build the OT assistant as "middleware glue," the following protocols and methodologies were identified:

### Industrial Connectivity
* **Modbus**: Legacy protocol support.
* **OPC UA**: Specifically the **GDS (Global Discovery Server)** extension.
* **MQTT Sparkplug B**: Recommended for state management and plug-and-play interoperability.

### Analytical Focus
* **Predictive Maintenance**: Monitoring vibration, heat, and flow rates to predict equipment failure.
* **Causal AI**: Moving beyond simple prediction to **Root Cause Analysis (RCA)** using multivariate data.
* **OEE (Overall Equipment Effectiveness)**: The core KPI for the project, measuring Availability, Performance, and Quality Yield.

---

## 3. Minimum Viable Product (MVP) Strategy

The team aligned on the following immediate steps for the infrastructure:

1.  **Simulated Telemetry**: Use of flow rates, pressure, and vibration sensors with "anomaly injectors" to mimic real-world faults (e.g., bearing wear).
2.  **Context Management**: Use of **Atomic Prompts** and **Mermaid/UML sequence diagrams** to keep the AI within context window limits and reduce token costs.
3.  **Database**: Deployment of a time-series database (e.g., MongoDB or Timescale) to capture telemetry for model training and inference.

---

## 4. Next Steps (Action Items)
* **Architectural BOM**: John Archer to create a Bill of Materials for the MVP.
* **Logic Flowchart**: Create a high-level Mermaid diagram illustrating the data flow from raw infrastructure to the OT assistant.
