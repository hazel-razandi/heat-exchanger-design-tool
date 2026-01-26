# 🏭 ExchangerPro: Enterprise Heat Exchanger Design Suite

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Standard](https://img.shields.io/badge/Standard-TEMA%20%2F%20API%20660-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-3.0.0_Enterprise-purple?style=for-the-badge)

**Professional thermal sizing, hydraulic analysis, and AACE Class 4 cost estimation for industrial heat exchangers.**

[View Live Demo](#) • [Report Bug](https://github.com/kakarotoncloud/heat-exchanger-design-tool/issues) • [Request Feature](https://github.com/kakarotoncloud/heat-exchanger-design-tool/issues)

</div>

---

## 📋 Table of Contents
- [📍 Overview](#-overview)
- [🚀 Key Features](#-key-features)
- [📐 Engineering Theory](#-engineering-theory)
- [🛠️ Installation](#️-installation)
- [📖 User Manual](#-user-manual)
- [💰 Cost Estimation Methodology](#-cost-estimation-methodology)
- [📂 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#-disclaimer)
- [👤 Author](#-author)

---

## 📍 Overview

**ExchangerPro** bridges the gap between academic theory and industrial application. While most open-source tools provide simple LMTD calculations, ExchangerPro integrates **Material Science**, **Hydraulic Safety Checks (API 661)**, and **Financial Modeling** into a single dashboard.

It is designed for:
* **Process Engineers:** To perform quick "sanity checks" on vendor quotes.
* **Plant Managers:** To estimate budget costs for plant expansions.
* **Students & Researchers:** To visualize T-Q diagrams and understand flow regimes.

---

## 🚀 Key Features

### 1. 🌡️ Advanced Thermal Engine
* **Dual-Mode Simulation:**
    * **Design Mode:** Calculates required area ($A$) given inlet/outlet temperatures.
    * **Rating Mode:** Predicts performance ($\epsilon$) given a fixed surface area.
* **Physics-Aware:** Automatically detects **Temperature Crosses** (infeasible for 1-pass shells) and **Second Law violations**.
* **Dynamic Properties:** Integrated with **CoolProp** (NIST-traceable database) for high-accuracy fluid properties ($C_p, \mu, k, \rho$) across wide temperature ranges.

### 2. 🌊 Hydraulic Safety & API 661
* **Erosion Protection:** Monitors tube-side velocity against API 661 limits (> 3 m/s) to prevent tube erosion.
* **Fouling Alerts:** Warns of low-velocity zones (< 1 m/s) prone to particulate settling.
* **Flow Regime Detection:** Real-time Reynolds number ($Re$) calculation to distinguish Laminar, Transitional, and Turbulent flow.

### 3. 🏗️ Material & Mechanical Database
* **Integrated Library:** Includes thermal conductivity and cost factors for **Carbon Steel, SS304, SS316, Titanium, and Hastelloy**.
* **TEMA Standards:** Automatically applies correct fouling factors ($R_f$) based on service (e.g., Sea Water vs. Distilled Water).

### 4. 💵 Techno-Economic Analysis (TEA)
* **AACE Class 4 Estimate:** Provides preliminary CAPEX estimates (+/- 30% accuracy).
* **Lang Factor Method:** Granular breakdown of costs into Equipment, Installation, Piping, Electrical, and Engineering.

---

## 📐 Engineering Theory

### 1. Thermal Design (LMTD & $\epsilon$-NTU)
The core solver uses the Log Mean Temperature Difference method, corrected for flow configuration:

$$Q = U \cdot A \cdot \Delta T_{lm} \cdot F_t$$

Where the Overall Heat Transfer Coefficient ($U$) includes fouling:

$$\frac{1}{U} = \frac{1}{h_{hot}} + \frac{1}{h_{cold}} + R_{f,hot} + R_{f,cold} + \frac{t_w}{k_w}$$

### 2. Hydraulic Model
Pressure drop is estimated using the Darcy-Weisbach equation. Friction factors ($f$) are derived dynamically using the **Haaland Equation** (for turbulent flow) or $64/Re$ (for laminar):

$$\Delta P = f \cdot \frac{L}{D} \cdot \frac{\rho v^2}{2} \cdot N_{passes}$$

### 3. Flow Regime Map
* **Laminar:** $Re < 2300$ (Poor heat transfer, high fouling risk)
* **Transitional:** $2300 < Re < 4000$ (Unstable region)
* **Turbulent:** $Re > 4000$ (Optimal for heat transfer)

---

## 🛠️ Installation

### Prerequisites
* Python 3.8+
* pip (Python Package Manager)

### Step-by-Step Guide

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/kakarotoncloud/heat-exchanger-design-tool.git](https://github.com/kakarotoncloud/heat-exchanger-design-tool.git)
    cd heat-exchanger-design-tool
    ```

2.  **Install Dependencies**
    We use a strictly pinned `requirements.txt` to ensure stability.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the Application**
    ```bash
    streamlit run app.py
    ```

4.  **Access the Dashboard**
    Open your browser to `http://localhost:8501`.

---

## 📖 User Manual

### Tab 1: Input & Calculate
1.  **Select Basis:** Choose "Design" to size a new unit or "Rating" to check an existing one.
2.  **Select Fluids:** Choose from the dropdown (Water, Oil, Glycol, etc.). The app handles the physical properties automatically.
3.  **Define Specs:** Input your mass flow rates and temperatures.
4.  **Click "Run Simulation":** The engine will solve the energy balance iteratively.

### Tab 2: Analysis & Graphs
* **T-Q Diagram:** Visualizes the temperature profile along the exchanger length. **Crucial:** Ensure the red line (Hot) stays above the blue line (Cold).
* **Hydraulics:** Check the "Velocity" gauge. If it's red (>3 m/s), increase your tube diameter or count.

### Tab 3: Reports
* **Spec Sheet:** Generates a TEMA-style text report.
* **Download:** Save the `.txt` file for your project documentation.

---

## 💰 Cost Estimation Methodology

**ExchangerPro** uses a parametric cost model calibrated to 2024 global market rates for process equipment.

$$ Cost_{FOB} = BaseCost \cdot \left(\frac{Area}{Area_{ref}}\right)^{0.65} \cdot F_{mat} \cdot F_{type} $$

| Cost Component | Factor (% of FOB) | Description |
| :--- | :--- | :--- |
| **Installation** | 45% | Foundations, structural supports, setting |
| **Piping** | 35% | Connecting piping, valves, insulation |
| **Electrical** | 15% | Instrumentation, controls, wiring |
| **Engineering** | 25% | Design, procurement, project management |
| **Contingency** | 20% | Risk buffer for unknowns |

---

## 📂 Project Structure

```text
ExchangerPro/
├── app.py                  # 🚀 Main Application Entry Point
├── requirements.txt        # 📦 Dependency Manifest
├── README.md               # 📄 Documentation
└── src/                    # 🧠 Core Logic Modules
    ├── __init__.py         # Package Initializer
    ├── calculations.py     # Thermal Solver (LMTD/NTU Logic)
    ├── cost_estimator.py   # AACE Class 4 Financial Model
    ├── pressure_drop.py    # Hydraulic Engine & API 661 Checks
    ├── fluid_properties.py # CoolProp Wrapper & Fail-safe Logic
    ├── hx_types.py         # Engineering DB (Materials/Standards)
    ├── pdf_generator.py    # Report Rendering Engine
    └── utils.py            # Validation & Graphing Helpers
🤝 Contributing
​Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
​Fork the Project
​Create your Feature Branch (git checkout -b feature/AmazingFeature)
​Commit your Changes (git commit -m 'Add some AmazingFeature')
​Push to the Branch (git push origin feature/AmazingFeature)
​Open a Pull Request
​⚠️ Disclaimer
​This tool is intended for preliminary design and educational purposes only.
​While the algorithms are based on standard engineering texts (Kern, Serth, TEMA), the results should not be used for fabrication or critical safety applications without verification by a licensed Professional Engineer (PE) using validated software (such as HTRI, HTFS, or Aspen Exchanger Design & Rating).
​The author assumes no liability for hardware failures or financial losses resulting from the use of this software.
​👤 Author
​KAKAROTONCLOUD
​Lead Developer & Mechanical Engineer
​GitHub Profile
​<div align="center">
<sub>Built with ❤️ using Python, Streamlit, and CoolProp.</sub>
</div>

