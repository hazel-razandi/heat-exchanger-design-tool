"""
Heat Exchanger Design Tool - Main Streamlit Application
Enhanced with Pressure Drop, Cost Estimation, PDF Reports, Design Storage, and Fouling Factors
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
from datetime import datetime

from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids, FluidProperties
from src.hx_types import HeatExchangerType
from src.utils import (
    validate_temperatures, 
    generate_temperature_profile,
    celsius_to_fahrenheit,
    kw_to_btu_per_hour,
    square_meters_to_square_feet
)
from src.pressure_drop import PressureDropCalculator
from src.cost_estimator import CostEstimator
from src.pdf_generator import generate_text_report, create_downloadable_report
from src.design_storage import DesignStorage, DESIGN_TEMPLATES, list_available_templates

# Page configuration
st.set_page_config(
    page_title="Heat Exchanger Design Tool",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'saved_designs' not in st.session_state:
    st.session_state.saved_designs = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔥❄️ Heat Exchanger Design Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional thermal design with advanced analysis</div>', unsafe_allow_html=True)

# Feature badges
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <span class="feature-badge">⚡ Pressure Drop</span>
    <span class="feature-badge">💰 Cost Estimation</span>
    <span class="feature-badge">📄 PDF Reports</span>
    <span class="feature-badge">💾 Save/Load</span>
    <span class="feature-badge">🧼 Fouling Factors</span>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Design Templates
    st.subheader("📋 Quick Start Templates")
    templates = list_available_templates()
    template_options = ['Custom Design'] + [t['name'] for t in templates]
    selected_template = st.selectbox("Load Template", template_options)
    
    # Load template if selected
    template_data = None
    if selected_template != 'Custom Design':
        for t in templates:
            if t['name'] == selected_template:
                template_key = t['key']
                template_data = DESIGN_TEMPLATES[template_key]['defaults']
                st.info(f"📝 {DESIGN_TEMPLATES[template_key]['description']}")
                break
    
    st.markdown("---")
    
    # Flow arrangement
    flow_type = st.selectbox(
        "Flow Arrangement",
        ["Counter Flow", "Parallel Flow"],
        help="Counter flow is more efficient"
    )
    
    # Calculation method
    method = st.radio(
        "Calculation Method",
        ["LMTD (Design)", "NTU (Rating)"],
        help="LMTD: Calculate required area | NTU: Analyze existing HX"
    )
    
    # Unit system
    unit_system = st.selectbox(
        "Unit System",
        ["Metric (°C, kW, m²)", "Imperial (°F, BTU/hr, ft²)"]
    )
    
    # Fouling factors toggle
    st.markdown("---")
    st.subheader("🧼 Fouling Factors")
    include_fouling = st.checkbox("Include fouling resistance", value=False)
    
    # Advanced options
    st.markdown("---")
    st.subheader("🔧 Advanced Options")
    calculate_pressure_drop = st.checkbox("Calculate pressure drop", value=True)
    estimate_costs = st.checkbox("Estimate costs", value=True)
    
    st.markdown("---")
    
    # Heat exchanger type selector
    st.subheader("📊 HX Type Reference")
    hx_type = st.selectbox(
        "Heat Exchanger Type",
        HeatExchangerType.list_all_types()
    )
    
    fluid_combo = st.selectbox(
        "Fluid Combination",
        HeatExchangerType.get_fluid_combinations(hx_type)
    )
    
    if st.button("Get Typical U-value"):
        min_u, max_u = HeatExchangerType.get_typical_U_value(hx_type, fluid_combo)
        avg_u = (min_u + max_u) / 2
        st.success(f"**Typical U-value Range:**\n\n{min_u} - {max_u} W/(m²·K)\n\n**Average:** {avg_u:.0f} W/(m²·K)")

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Design Calculator", "📊 Results & Analysis", "📄 Reports", "💾 Saved Designs", "📚 Information"])

with tab1:
    st.header("Heat Exchanger Design Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Hot Fluid")
        hot_fluid = st.selectbox("Fluid Type (Hot)", get_available_fluids(), 
                                key="hot_fluid",
                                index=0 if not template_data else get_available_fluids().index(template_data.get('hot_fluid', 'Water')))
        
        if unit_system.startswith("Metric"):
            T_hot_in = st.number_input("Inlet Temperature (°C)", 
                                      value=template_data.get('T_hot_in', 90.0) if template_data else 90.0,
                                      step=1.0, key="T_hot_in")
            if method == "LMTD (Design)":
                T_hot_out = st.number_input("Outlet Temperature (°C)", 
                                           value=template_data.get('T_hot_out', 50.0) if template_data else 50.0,
                                           step=1.0, key="T_hot_out")
            m_hot = st.number_input("Mass Flow Rate (kg/s)", 
                                   value=template_data.get('m_hot', 2.0) if template_data else 2.0,
                                   step=0.1, min_value=0.01, key="m_hot")
        else:
            T_hot_in_f = st.number_input("Inlet Temperature (°F)", value=194.0, step=1.0, key="T_hot_in_f")
            T_hot_in = (T_hot_in_f - 32) * 5/9
            if method == "LMTD (Design)":
                T_hot_out_f = st.number_input("Outlet Temperature (°F)", value=122.0, step=1.0, key="T_hot_out_f")
                T_hot_out = (T_hot_out_f - 32) * 5/9
            m_hot_lb = st.number_input("Mass Flow Rate (lb/hr)", value=15873.0, step=100.0, min_value=0.01, key="m_hot_lb")
            m_hot = m_hot_lb / 7936.64
    
    with col2:
        st.subheader("🔵 Cold Fluid")
        cold_fluid = st.selectbox("Fluid Type (Cold)", get_available_fluids(), 
                                 key="cold_fluid",
                                 index=0 if not template_data else get_available_fluids().index(template_data.get('cold_fluid', 'Water')))
        
        if unit_system.startswith("Metric"):
            T_cold_in = st.number_input("Inlet Temperature (°C)", 
                                       value=template_data.get('T_cold_in', 25.0) if template_data else 25.0,
                                       step=1.0, key="T_cold_in")
            
            if method == "LMTD (Design)":
                T_cold_out = st.number_input("Outlet Temperature (°C)", 
                                            value=template_data.get('T_cold_out', 45.0) if template_data else 45.0,
                                            step=1.0, key="T_cold_out")
            
            m_cold = st.number_input("Mass Flow Rate (kg/s)", 
                                    value=template_data.get('m_cold', 3.0) if template_data else 3.0,
                                    step=0.1, min_value=0.01, key="m_cold")
        else:
            T_cold_in_f = st.number_input("Inlet Temperature (°F)", value=77.0, step=1.0, key="T_cold_in_f")
            T_cold_in = (T_cold_in_f - 32) * 5/9
            
            if method == "LMTD (Design)":
                T_cold_out_f = st.number_input("Outlet Temperature (°F)", value=113.0, step=1.0, key="T_cold_out_f")
                T_cold_out = (T_cold_out_f - 32) * 5/9
            
            m_cold_lb = st.number_input("Mass Flow Rate (lb/hr)", value=23810.0, step=100.0, min_value=0.01, key="m_cold_lb")
            m_cold = m_cold_lb / 7936.64
    
    st.markdown("---")
    
    # Heat exchanger parameters
    st.subheader("🔧 Heat Exchanger Parameters")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if unit_system.startswith("Metric"):
            U_value_clean = st.number_input(
                "Overall HTC - Clean (W/m²·K)",
                value=template_data.get('U_value', 500.0) if template_data else 500.0,
                step=50.0,
                min_value=1.0,
                help="U-value for clean surfaces"
            )
        else:
            U_value_imp = st.number_input(
                "Overall HTC - Clean (BTU/hr·ft²·°F)",
                value=88.0,
                step=5.0,
                min_value=1.0
            )
            U_value_clean = U_value_imp * 5.678
    
    with col4:
        if method == "NTU (Rating)":
            if unit_system.startswith("Metric"):
                area = st.number_input(
                    "Heat Exchanger Area (m²)",
                    value=template_data.get('area', 12.4) if template_data else 12.4,
                    step=0.5,
                    min_value=0.1
                )
            else:
                area_ft2 = st.number_input(
                    "Heat Exchanger Area (ft²)",
                    value=133.0,
                    step=5.0,
                    min_value=1.0
                )
                area = area_ft2 / 10.7639
    
    with col5:
        if include_fouling:
            fouling_hot = st.number_input(
                "Hot Side Fouling (m²·K/W)",
                value=0.0002,
                step=0.0001,
                format="%.4f",
                min_value=0.0,
                help="Typical: 0.0002-0.0009"
            )
            fouling_cold = st.number_input(
                "Cold Side Fouling (m²·K/W)",
                value=0.0002,
                step=0.0001,
                format="%.4f",
                min_value=0.0,
                help="Typical: 0.0002-0.0009"
            )
            # Calculate dirty U-value
            U_value = 1 / (1/U_value_clean + fouling_hot + fouling_cold)
            st.info(f"**Fouled U-value:** {U_value:.1f} W/(m²·K)\n\n**Degradation:** {((U_value_clean - U_value)/U_value_clean * 100):.1f}%")
        else:
            U_value = U_value_clean
    
    # Calculate button
    st.markdown("---")
    
    col_calc1, col_calc2, col_calc3 = st.columns([2, 1, 1])
    with col_calc1:
        calculate_button = st.button("🚀 Calculate Heat Exchanger Performance", type="primary", use_container_width=True)
    with col_calc2:
        save_design = st.button("💾 Save Design", use_container_width=True)
    with col_calc3:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
        with tab2:
    st.header("Results & Advanced Analysis")
    
    if st.session_state.current_results:
        results = st.session_state.current_results
        st.success("✅ Results Available")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Heat Transfer", f"{results.get('Q', 0):.2f} kW")
        with col2:
            st.metric("Area", f"{results.get('area', 0):.2f} m²")
        with col3:
            st.metric("Effectiveness", f"{results.get('effectiveness', 0)*100:.1f}%")
        with col4:
            st.metric("NTU", f"{results.get('NTU', 0):.2f}")
        
        # Show stored pressure drop and cost data if available
        if 'pressure_drop' in results:
            with st.expander("⚡ Pressure Drop Details", expanded=True):
                st.json(results['pressure_drop'])
        
        if 'costs' in results:
            with st.expander("💰 Cost Details", expanded=True):
                st.json(results['costs'])
    else:
        st.info("👈 Run a calculation first to see results here")

with tab3:
    st.header("📄 Generate Professional Report")
    
    if st.session_state.current_results:
        st.subheader("Project Information (Optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name", "Heat Exchanger Design")
            engineer_name = st.text_input("Engineer Name", "")
        with col2:
            company = st.text_input("Company", "")
            location = st.text_input("Location", "")
        
        project_info = {
            'project_name': project_name,
            'engineer_name': engineer_name,
            'company': company,
            'location': location,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        st.markdown("---")
        
        # Generate report
        pressure_drop_data = st.session_state.current_results.get('pressure_drop', None)
        cost_data = st.session_state.current_results.get('costs', None)
        
        report_text = generate_text_report(
            st.session_state.current_results,
            pressure_drop_data,
            cost_data,
            project_info
        )
        
        st.subheader("Report Preview")
        st.text_area("", report_text, height=400)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            # Download as TXT
            st.download_button(
                label="📥 Download Report (TXT)",
                data=report_text,
                file_name=f"{project_name.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Download as CSV
            content, filename, mime = create_downloadable_report(
                st.session_state.current_results,
                pressure_drop_data,
                cost_data,
                project_info,
                format='csv'
            )
            st.download_button(
                label="📥 Download Summary (CSV)",
                data=content,
                file_name=filename,
                mime=mime,
                use_container_width=True
            )
    else:
        st.info("👈 Run a calculation first to generate a report")

with tab4:
    st.header("💾 Saved Designs")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Design Library")
        
        if st.session_state.saved_designs:
            for idx, design in enumerate(st.session_state.saved_designs):
                with st.expander(f"📁 {design['design_name']} - {design['date_readable']}"):
                    st.write(f"**Flow Type:** {design['data'].get('results', {}).get('flow_type', 'N/A')}")
                    st.write(f"**Method:** {design['data'].get('results', {}).get('method', 'N/A')}")
                    st.write(f"**Heat Transfer:** {design['data'].get('results', {}).get('Q', 0):.2f} kW")
                    st.write(f"**Area:** {design['data'].get('results', {}).get('area', 0):.2f} m²")
                    st.write(f"**Effectiveness:** {design['data'].get('results', {}).get('effectiveness', 0)*100:.1f}%")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("🔄 Load", key=f"load_{idx}"):
                            st.session_state.current_results = design['data'].get('results')
                            st.success("Design loaded!")
                            st.rerun()
                    with col_b:
                        design_json = json.dumps(design, indent=2)
                        st.download_button(
                            label="📥 Export",
                            data=design_json,
                            file_name=f"{design['design_name']}.json",
                            mime="application/json",
                            key=f"export_{idx}"
                        )
                    with col_c:
                        if st.button("🗑️ Delete", key=f"delete_{idx}"):
                            st.session_state.saved_designs.pop(idx)
                            st.success("Design deleted!")
                            st.rerun()
        else:
            st.info("No saved designs yet. Calculate and save a design to see it here!")
    
    with col2:
        st.subheader("Import Design")
        uploaded_file = st.file_uploader("Upload JSON", type=['json'])
        
        if uploaded_file is not None:
            try:
                design_json = json.loads(uploaded_file.read())
                storage = DesignStorage()
                imported_design = storage.import_design_json(json.dumps(design_json))
                
                if imported_design:
                    if st.button("✅ Add to Library"):
                        st.session_state.saved_designs.append(imported_design)
                        st.success(f"Imported: {imported_design['design_name']}")
                        st.rerun()
                else:
                    st.error("Invalid design file")
            except Exception as e:
                st.error(f"Error importing: {e}")

# Save design functionality
if save_design and st.session_state.current_results:
    st.sidebar.markdown("---")
    design_name = st.sidebar.text_input("Design Name", f"Design_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    if st.sidebar.button("💾 Confirm Save"):
        storage = DesignStorage()
        snapshot = storage.create_design_snapshot(
            {'results': st.session_state.current_results},
            design_name
        )
        st.session_state.saved_designs.append(snapshot)
        st.sidebar.success(f"✅ Saved: {design_name}")

with tab5:
    st.header("📚 Information & Help")
    
    st.markdown("""
    ## 🎯 How to Use This Tool
    
    ### LMTD Method (Design Mode)
    Use when you know:
    - All inlet and outlet temperatures
    - Mass flow rates
    - Want to find: **Required heat exchanger area**
    
    ### NTU Method (Rating Mode)
    Use when you know:
    - Inlet temperatures
    - Heat exchanger area (existing HX)
    - Want to find: **Outlet temperatures and performance**
    
    ---
    
    ## 🆕 New Features
    
    ### ⚡ Pressure Drop Calculation
    - Automatically estimates geometry from area
    - Calculates pressure drop on both sides
    - Shows pumping power requirements
    - Estimates annual energy costs
    
    ### 💰 Cost Estimation
    - Equipment cost based on area, type, material
    - Installation, piping, instrumentation costs
    - Annual operating costs (energy + maintenance)
    - 20-year lifecycle cost analysis
    
    ### 🧼 Fouling Factors
    - Account for surface fouling over time
    - Shows performance degradation
    - Typical values provided
    
    ### 📄 PDF Reports
    - Professional formatted reports
    - Include all calculations and results
    - Project information section
    - Downloadable as TXT or CSV
    
    ### 💾 Save/Load Designs
    - Save designs to library
    - Export as JSON files
    - Import previously saved designs
    - Compare multiple designs
    
    ---
    
    ## 💡 Tips for Accurate Results
    
    1. **Counter flow is more efficient** than parallel flow
    2. **Check energy balance error** - should be < 1%
    3. **Typical U-values:**
       - Water-Water: 800-1500 W/(m²·K)
       - Water-Oil: 100-400 W/(m²·K)
       - Water-Air: 10-50 W/(m²·K)
    4. **Fouling resistance:** 0.0002-0.0009 m²·K/W for most fluids
    5. **Validate temperatures** - hot outlet must be > cold inlet
    
    ---
    
    ## 📖 Additional Resources
    
    - [Theory Documentation](https://github.com/yourusername/heat-exchanger-design-tool/blob/main/docs/theory.md)
    - [Formula Reference](https://github.com/yourusername/heat-exchanger-design-tool/blob/main/docs/formulas.md)
    - [Worked Examples](https://github.com/yourusername/heat-exchanger-design-tool/blob/main/docs/examples.md)
    
    ---
    
    ## 👤 About
    
    **Created by:** KAKAROTONCLOUD 
    
    **GitHub:** [View Source Code](https://github.com/yourusername/heat-exchanger-design-tool)
    
    **Version:** 2.0 (Enhanced with 5 advanced features)
    
    ---
    
    ## 🐛 Found a Bug?
    
    Report issues on [GitHub Issues](https://github.com/yourusername/heat-exchanger-design-tool/issues)
    
    ---
    
    ## ⭐ Like This Tool?
    
    Give it a star on [GitHub](https://github.com/yourusername/heat-exchanger-design-tool)!
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit | Heat Exchanger Design Tool v2.0<br>
    Enhanced with Pressure Drop, Cost Estimation, PDF Reports, Design Storage & Fouling Factors
</div>
""", unsafe_allow_html=True)
