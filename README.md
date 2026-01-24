🔥❄️ Heat Exchanger Design Tool
�

�
�
�
�
Load image
Load image
Load image
Load image
A professional web-based tool for designing and analyzing heat exchangers
🚀 Live Demo | 📖 Documentation | 🎯 Examples | 🐛 Report Bug
Quickly size heat exchangers, calculate performance, and visualize thermal profiles—all in your browser.
�

📋 Table of Contents
Overview
Features
Demo
Quick Start
Usage Guide
Technical Details
Project Structure
Contributing
License
Contact
🎯 Overview
The Heat Exchanger Design Tool is a comprehensive web application built for HVAC engineers, mechanical engineers, and students to design, size, and analyze heat exchangers without complex manual calculations.
What Problem Does It Solve?
Traditional heat exchanger design requires:
✗ Complex manual calculations with multiple formulas
✗ Looking up fluid properties from tables
✗ Iterative trial-and-error sizing
✗ Separate tools for graphs and analysis
This tool provides:
✓ Instant calculations with validated engineering methods
✓ Automatic fluid property lookup for multiple fluids
✓ Real-time visualization of temperature profiles
✓ Comparison between different configurations
✓ Downloadable results and reports
✨ Features
Core Calculations
🧮 LMTD Method - Design mode: Calculate required heat exchanger area
📊 NTU-Effectiveness Method - Rating mode: Analyze existing heat exchanger performance
🌡️ Temperature Profile Visualization - See how temperature changes through the exchanger
⚡ Heat Transfer Rate - Accurate Q calculations with energy balance validation
Fluid Properties
💧 Multiple Fluids Supported:
Water
Air
Ethylene Glycol (20%, 40%, 60%)
Engine Oil
R-134a Refrigerant
🔬 Accurate Properties using CoolProp library:
Density (ρ)
Specific Heat (Cp)
Thermal Conductivity (k)
Dynamic Viscosity (μ)
Prandtl Number (Pr)
Heat Exchanger Types
🔄 Counter Flow - Maximum efficiency
⇉ Parallel Flow - Simple configuration
🏭 Shell-and-Tube - Industrial standard
📄 Plate Type - Compact design
🌊 Finned Tube - Gas-to-liquid applications
Advanced Features
📈 Performance Comparison - Compare counter-flow vs parallel-flow side-by-side
🎯 Effectiveness Calculation - Real thermal performance metrics
⚠️ Input Validation - Prevents thermodynamically impossible inputs
💾 Export Results - Download calculations as text/PDF
📉 Interactive Graphs - Zoom, pan, and analyze temperature profiles
🔢 Unit Conversions - Support for metric and imperial units
🎬 Demo
Input Interface
Hot Fluid:  Water @ 90°C → 50°C, 2.0 kg/s
Cold Fluid: Water @ 25°C → ?°C,  3.0 kg/s
Configuration: Counter Flow
Method: LMTD
U-value: 500 W/(m²·K)
Output Results
✅ Heat Transfer Rate (Q): 335.2 kW
✅ Required Area: 12.4 m²
✅ LMTD: 54.1°C
✅ Effectiveness: 61.5%
✅ Cold Outlet Temp: 51.7°C
✅ NTU: 2.07
Visual Output
Temperature vs Length graph
Effectiveness vs NTU curve
Configuration comparison chart
(Screenshots will be added here once deployed)
🚀 Quick Start
Prerequisites
Python 3.8 or higher
pip package manager
Installation
Clone the repository
git clone https://github.com/yourusername/heat-exchanger-design-tool.git
cd heat-exchanger-design-tool
Create virtual environment (recommended)
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
Install dependencies
pip install -r requirements.txt
Run the application
streamlit run app.py
Open in browser
The app will automatically open at http://localhost:8501
If not, navigate to the URL shown in terminal
📖 Usage Guide
Basic Workflow
Select Configuration
Choose between Counter Flow or Parallel Flow
Select calculation method (LMTD or NTU)
Enter Hot Fluid Data
Fluid type (Water, Air, etc.)
Inlet temperature (°C)
Outlet temperature (°C)
Mass flow rate (kg/s)
Enter Cold Fluid Data
Fluid type
Inlet temperature (°C)
For LMTD: Outlet temperature
For NTU: Heat exchanger area
Mass flow rate (kg/s)
Set Heat Exchanger Parameters
Overall heat transfer coefficient (U)
Or select from typical values
Calculate
Click "Calculate" button
View results and graphs
Download report if needed
Example Use Cases
Case 1: Sizing a Chiller Heat Exchanger
Hot: Water 12°C → 7°C (chilled water return → supply)
Cold: R-134a evaporating at 2°C
Need to find: Required evaporator area
Case 2: Verifying Radiator Performance
Hot: Engine coolant 95°C inlet
Cold: Air 25°C inlet
Known: Radiator has 2.5 m² area
Need to find: Outlet temperatures and cooling capacity
Case 3: Heat Recovery Design
Hot: Exhaust air 60°C
Cold: Fresh air 20°C
Need to find: Optimal size for 70% effectiveness
🔬 Technical Details
Engineering Methods
LMTD Method (Design)
Used when inlet and outlet temperatures are known:
Q = U × A × LMTD × F

where:
LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)
ΔT₁ = T_hot_in - T_cold_out
ΔT₂ = T_hot_out - T_cold_in
NTU-Effectiveness Method (Rating)
Used when heat exchanger area is known:
ε = Q_actual / Q_maximum
NTU = UA / C_min
C = ṁ × Cp

Effectiveness correlations for:
- Counter flow: ε = (1 - exp(-NTU(1-C*))) / (1 - C*exp(-NTU(1-C*)))
- Parallel flow: ε = (1 - exp(-NTU(1+C*))) / (1 + C*)
Fluid Properties
Properties calculated using CoolProp - an industry-standard thermophysical property library:
Temperature-dependent properties
Accurate within ±1% of experimental data
Covers wide range of conditions
Validation
All calculations include:
Energy balance verification (Q_hot = Q_cold)
Second law check (no temperature crossover)
Reynolds number calculation for flow regime
Realistic U-value ranges
📁 Project Structure
heat-exchanger-design-tool/
│
├── app.py                      # Main Streamlit web application
│
├── src/
│   ├── calculations.py         # Core heat exchanger calculations
│   ├── fluid_properties.py     # Fluid property database & CoolProp interface
│   ├── hx_types.py            # Heat exchanger type definitions
│   └── utils.py               # Helper functions & unit conversions
│
├── tests/
│   └── test_calculations.py   # Unit tests for all calculations
│
├── docs/
│   ├── theory.md              # Detailed engineering theory
│   ├── formulas.md            # Formula reference guide
│   └── examples.md            # Worked examples
│
├── examples/
│   └── sample_calculations.py # Python script examples
│
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── LICENSE                    # MIT License
🛠️ Technologies Used
Technology
Purpose
Python 3.8+
Core programming language
Streamlit
Web application framework
CoolProp
Fluid thermophysical properties
NumPy
Numerical computations
Matplotlib
Static plotting
Plotly
Interactive visualizations
Pandas
Data handling
Pytest
Unit testing
🧪 Testing
Run the test suite:
pytest tests/ -v
Run with coverage report:
pytest tests/ --cov=src --cov-report=html
🤝 Contributing
Contributions are welcome! Here's how you can help:
Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
Ideas for Contribution
Add more fluid types
Implement pressure drop calculations
Add fouling factor considerations
Create more heat exchanger configurations
Improve UI/UX
Add more unit tests
Translate to other languages
🗺️ Roadmap
[x] LMTD and NTU methods
[x] Basic fluid properties
[x] Temperature visualization
[ ] Pressure drop calculation
[ ] Fouling factor adjustment
[ ] Multi-pass configurations
[ ] Cost estimation
[ ] 3D visualization
[ ] Mobile-responsive design
[ ] API endpoint for programmatic access
[ ] Database for saving designs
📚 Learn More
Heat Transfer Fundamentals
Formula Reference
Worked Examples
External Resources
Fundamentals of Heat and Mass Transfer - Bergman, Lavine, Incropera, DeWitt
CoolProp Documentation
ASHRAE Handbook - HVAC Systems and Equipment
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
👤 Contact
[Your Name]
GitHub: @yourusername
LinkedIn: Your LinkedIn
Email: your.email@example.com
Project Link: https://github.com/yourusername/heat-exchanger-design-tool
🙏 Acknowledgments
CoolProp developers for the excellent fluid property library
Streamlit team for the amazing web framework
Heat transfer textbook authors for the theoretical foundation
Open source community for inspiration
�

⭐ If you find this project useful, please consider giving it a star! ⭐
Made with ❤️ and ☕ by [Your Name]
�
