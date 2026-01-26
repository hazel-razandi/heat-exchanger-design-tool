# 🏭 ExchangerPro: Enterprise Heat Exchanger Design Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Standard](https://img.shields.io/badge/Standard-TEMA%20%2F%20API%20660-orange)
![Version](https://img.shields.io/badge/Version-3.0.0_Enterprise-purple)

**ExchangerPro** is a commercial-grade web application designed for the preliminary thermal sizing, hydraulic analysis, and techno-economic assessment of industrial heat exchangers. 

Built for mechanical engineers, process designers, and plant operators, it bridges the gap between textbook theory and industry standards (TEMA, API 661).

---

## 🚀 Key Features

### 1. 🧮 Advanced Thermal Engine
* **Dual-Mode Simulation:**
    * **Design Mode (LMTD):** Calculates required surface area based on target temperatures.
    * **Rating Mode ($\epsilon$-NTU):** Simulates performance of existing equipment given a fixed area.
* **Physics-Aware:** Automatic detection of Temperature Crosses and Second Law violations.
* **Dynamic Properties:** Integrated with **CoolProp** (NIST-traceable database) for high-accuracy fluid properties ($C_p$, $\mu$, $k$, $\rho$).

### 2. ⚙️ Hydraulic Safety (API 661)
* **Erosion Protection:** Real-time velocity monitoring against API limits (> 3 m/s).
* **Fouling Alerts:** Warnings for low-velocity zones (< 1 m/s) prone to sedimentation.
* **Flow Regime Detection:** Automatic calculation of Reynolds number ($Re$) to identify Laminar vs. Turbulent flow.

### 3. 💰 AACE Class 4 Cost Estimation
* **Parametric Estimator:** Generates preliminary CAPEX estimates (+/- 30% accuracy) based on surface area and material.
* **Lang Factor Analysis:** Breaks down costs into:
    * Base Equipment (FOB)
    * Installation Labor
    * Piping & Instrumentation
    * Engineering & Contingency
* **Material Sensitivity:** Real-time cost adjustments for exotic materials (Titanium, Hastelloy, SS316).

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.8 or higher
* PIP (Python Package Manager)

### Quick Start
1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/kakarotoncloud/heat-exchanger-design-tool.git](https://github.com/kakarotoncloud/heat-exchanger-design-tool.git)
    cd heat-exchanger-design-tool
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the Dashboard**
    ```bash
    streamlit run app.py
    ```
    The application will open automatically in your browser at `http://localhost:8501`.

---

## 📖 User Guide

### Step 1: Define Design Basis
* **Calculation Mode:** Choose **Design** if you need to size a new unit, or **Rating** to check an old one.
* **Configuration:** Select the TEMA type (e.g., *Shell-and-Tube BEM*, *Plate & Frame*).
* **Flow Arrangement:** *Counter Flow* is recommended for highest efficiency.

### Step 2: Input Process Data
* Select Fluids from the database (Water, Air, Oil, Glycols, Refrigerants).
* Enter **Mass Flow Rates** and **Inlet Temperatures**.
* (Design Mode) Enter **Target Outlet Temperatures**.

### Step 3: Mechanical Specs
* **Material:** Select construction material. Note: Exotic materials (Titanium) significantly increase cost.
* **Fouling:** Select the service type (e.g., *River Water*). The app automatically applies the correct TEMA fouling factor ($R_f$).

### Step 4: Analyze Results
* **Performance Tab:** Check the T-Q Diagram. Ensure lines do not cross.
* **Hydraulics Tab:** Verify Velocity is between 1.0 - 3.0 m/s.
* **Report Tab:** Generate and download the professional Specification Sheet.

---

## 📐 Engineering Theory

### Thermal Design
The tool solves the fundamental heat transfer equation:

$$ Q = U \cdot A \cdot \Delta T_{lm} \cdot F_t $$

Where:
* $Q$: Heat Duty (kW)
* $U$: Overall Heat Transfer Coefficient ($W/m^2K$)
* $A$: Required Surface Area ($m^2$)
* $\Delta T_{lm}$: Log Mean Temperature Difference

### Hydraulic Analysis
Pressure drop is estimated using the Darcy-Weisbach equation with friction factors derived from the Haaland approximation:

$$ \Delta P = f \cdot \frac{L}{D} \cdot \frac{\rho v^2}{2} $$

### Cost Model
Capital cost is estimated using a power-law sizing model calibrated to 2024 market rates:

$$ Cost_{FOB} = BaseCost \cdot \left(\frac{Area}{Area_{ref}}\right)^{0.65} \cdot F_{mat} \cdot F_{type} $$

---

## 📂 Project Structure

```text
ExchangerPro/
├── app.py                  # Main Application Dashboard
├── requirements.txt        # Dependency List
├── src/
│   ├── calculations.py     # Thermal Logic (LMTD/NTU)
│   ├── cost_estimator.py   # Financial Logic (Class 4 Estimates)
│   ├── pressure_drop.py    # Hydraulic Logic (API 661 Checks)
│   ├── fluid_properties.py # CoolProp Physics Engine
│   ├── hx_types.py         # Engineering Database (Materials/Standards)
│   ├── pdf_generator.py    # Report Generation Engine
│   └── utils.py            # Helper Functions & Validation
└── README.md               # Documentation

## ⚠️ Disclaimer
This tool is intended for **preliminary design and educational purposes only**. Final fabrication drawings and guarantees must be validated by a licensed Professional Engineer (PE) using specialized software (HTRI/HTFS).

## 👤 Author

**KAKAROTONCLOUD**
* *Lead Developer & Engineer*
* [GitHub Profile](https://github.com/kakarotoncloud)

