# 🏭 ExchangerPro: Advanced Heat Exchanger Design Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/Version-3.0.0_Enterprise-purple)
![Author](https://img.shields.io/badge/Engineer-KAKAROTONCLOUD-green)

**ExchangerPro** is a professional-grade web application for the preliminary thermal design, hydraulic analysis, and cost estimation of industrial heat exchangers. Designed for mechanical engineers, process designers, and plant managers.

---

## 🚀 Enterprise Features

### 1. Thermal Design Core
* **Dual-Mode Engine:** Switch between **Design Mode (LMTD)** for sizing and **Rating Mode (NTU)** for performance verification.
* **TEMA Compliance:** Includes standard fouling factors and configuration types (BEM, AES, etc.).
* **Physics-Aware:** Automatic detection of temperature crosses and Second Law violations.

### 2. Hydraulic Analysis
* **Flow Regime Detection:** Real-time calculation of Reynolds number ($Re$), identifying Laminar, Transition, or Turbulent flow.
* **Pressure Drop:** Simplified Darcy-Weisbach estimation for tube-side hydraulics.
* **Velocity Validation:** warnings against API 661 erosion velocity limits.

### 3. Techno-Economic Assessment (TEA)
* **Material Library:** integrated database of materials (CS, SS304, SS316, Titanium, CuNi) affecting both cost and thermal limits.
* **Class 4 Cost Estimation:** AACE International Class 4 preliminary cost estimate (+/- 30% accuracy) covering CAPEX and OPEX.

---

## 🛠️ Installation & Deployment

### Local Development
```bash
# 1. Clone the repository
git clone [https://github.com/kakarotoncloud/heat-exchanger-design-tool.git](https://github.com/kakarotoncloud/heat-exchanger-design-tool.git)

# 2. Install dependencies (Pinned for stability)
pip install -r requirements.txt

# 3. Launch the Engineering Dashboard
streamlit run app.py
