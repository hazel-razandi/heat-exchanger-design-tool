"""
Heat Exchanger Design Tool - Main Streamlit Application
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids
from src.hx_types import HeatExchangerType
from src.utils import (
    validate_temperatures, 
    generate_temperature_profile,
    format_result_string,
    celsius_to_fahrenheit,
    kw_to_btu_per_hour,
    square_meters_to_square_feet
)

# Page configuration
st.set_page_config(
    page_title="Heat Exchanger Design Tool",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔥❄️ Heat Exchanger Design Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional thermal design and analysis for engineers</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/temperature.png", width=80)
    st.title("⚙️ Configuration")
    
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
    
    st.markdown("---")
    
    # Heat exchanger type selector
    st.subheader("📊 HX Type Reference")
    hx_type = st.selectbox(
        "Select Type for U-value Reference",
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
tab1, tab2, tab3 = st.tabs(["📝 Design Calculator", "📊 Results & Graphs", "📚 Information"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Hot Fluid")
        hot_fluid = st.selectbox("Fluid Type (Hot)", get_available_fluids(), key="hot_fluid")
        
        if unit_system.startswith("Metric"):
            T_hot_in = st.number_input("Inlet Temperature (°C)", value=90.0, step=1.0, key="T_hot_in")
            T_hot_out = st.number_input("Outlet Temperature (°C)", value=50.0, step=1.0, key="T_hot_out")
            m_hot = st.number_input("Mass Flow Rate (kg/s)", value=2.0, step=0.1, min_value=0.01, key="m_hot")
        else:
            T_hot_in_f = st.number_input("Inlet Temperature (°F)", value=194.0, step=1.0, key="T_hot_in_f")
            T_hot_out_f = st.number_input("Outlet Temperature (°F)", value=122.0, step=1.0, key="T_hot_out_f")
            T_hot_in = (T_hot_in_f - 32) * 5/9
            T_hot_out = (T_hot_out_f - 32) * 5/9
            m_hot_lb = st.number_input("Mass Flow Rate (lb/hr)", value=15873.0, step=100.0, min_value=0.01, key="m_hot_lb")
            m_hot = m_hot_lb / 7936.64
    
    with col2:
        st.subheader("🔵 Cold Fluid")
        cold_fluid = st.selectbox("Fluid Type (Cold)", get_available_fluids(), key="cold_fluid")
        
        if unit_system.startswith("Metric"):
            T_cold_in = st.number_input("Inlet Temperature (°C)", value=25.0, step=1.0, key="T_cold_in")
            
            if method == "LMTD (Design)":
                T_cold_out = st.number_input("Outlet Temperature (°C)", value=45.0, step=1.0, key="T_cold_out")
            
            m_cold = st.number_input("Mass Flow Rate (kg/s)", value=3.0, step=0.1, min_value=0.01, key="m_cold")
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
    
    col3, col4 = st.columns(2)
    
    with col3:
        if unit_system.startswith("Metric"):
            U_value = st.number_input(
                "Overall Heat Transfer Coefficient U (W/m²·K)",
                value=500.0,
                step=50.0,
                min_value=1.0,
                help="Typical ranges: Water-Water: 800-1500, Water-Air: 10-50"
            )
        else:
            U_value_imp = st.number_input(
                "Overall Heat Transfer Coefficient U (BTU/hr·ft²·°F)",
                value=88.0,
                step=5.0,
                min_value=1.0
            )
            U_value = U_value_imp * 5.678
    
    with col4:
        if method == "NTU (Rating)":
            if unit_system.startswith("Metric"):
                area = st.number_input(
                    "Heat Exchanger Area (m²)",
                    value=12.4,
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
    
    # Calculate button
    st.markdown("---")
    calculate_button = st.button("🚀 Calculate Heat Exchanger Performance", type="primary", use_container_width=True)

with tab2:
    if calculate_button:
        try:
            # Validation
            if method == "LMTD (Design)":
                is_valid, error_msg = validate_temperatures(
                    T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type
                )
                
                if not is_valid:
                    st.error(f"❌ Invalid temperatures: {error_msg}")
                else:
                    # Perform LMTD calculation
                    hx = HeatExchanger(flow_arrangement=flow_type)
                    results = hx.calculate_lmtd(
                        T_hot_in, T_hot_out, T_cold_in, T_cold_out,
                        m_hot, m_cold, hot_fluid, cold_fluid, U_value
                    )
                    
                    # Display results
                    st.success("✅ Calculation Complete!")
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if unit_system.startswith("Metric"):
                            st.metric("Heat Transfer Rate", f"{results['Q']:.2f} kW")
                        else:
                            st.metric("Heat Transfer Rate", f"{kw_to_btu_per_hour(results['Q']):.0f} BTU/hr")
                    
                    with col2:
                        if unit_system.startswith("Metric"):
                            st.metric("Required Area", f"{results['area']:.2f} m²")
                        else:
                            st.metric("Required Area", f"{square_meters_to_square_feet(results['area']):.2f} ft²")
                    
                    with col3:
                        st.metric("Effectiveness", f"{results['effectiveness']*100:.1f}%")
                    
                    with col4:
                        st.metric("NTU", f"{results['NTU']:.2f}")
                    
                    # Additional details
                    with st.expander("📊 Detailed Results"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Temperature Data:**")
                            if unit_system.startswith("Metric"):
                                st.write(f"- LMTD: {results['LMTD']:.2f} °C")
                                st.write(f"- ΔT₁: {results['delta_T1']:.2f} °C")
                                st.write(f"- ΔT₂: {results['delta_T2']:.2f} °C")
                            else:
                                st.write(f"- LMTD: {results['LMTD']*9/5:.2f} °F")
                                st.write(f"- ΔT₁: {results['delta_T1']*9/5:.2f} °F")
                                st.write(f"- ΔT₂: {results['delta_T2']*9/5:.2f} °F")
                        
                        with col2:
                            st.write("**Heat Capacity Rates:**")
                            st.write(f"- C_hot: {results['C_hot']:.0f} W/K")
                            st.write(f"- C_cold: {results['C_cold']:.0f} W/K")
                            st.write(f"- C_ratio: {results['C_ratio']:.3f}")
                            st.write(f"- Energy Balance Error: {results['energy_balance_error']:.2f}%")
                    
                    # Temperature profile graph
                    st.subheader("🌡️ Temperature Profile")
                    
                    x, T_hot, T_cold = generate_temperature_profile(
                        T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type
                    )
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=x*100, y=T_hot,
                        mode='lines',
                        name='Hot Fluid',
                        line=dict(color='red', width=3)
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=x*100, y=T_cold,
                        mode='lines',
                        name='Cold Fluid',
                        line=dict(color='blue', width=3)
                    ))
                    
                    fig.update_layout(
                        title=f"Temperature Profile - {flow_type}",
                        xaxis_title="Position (%)",
                        yaxis_title="Temperature (°C)" if unit_system.startswith("Metric") else "Temperature (°F)",
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download results
                    result_text = format_result_string(results)
                    st.download_button(
                        label="📥 Download Results",
                        data=result_text,
                        file_name="heat_exchanger_results.txt",
                        mime="text/plain"
                    )
            
            else:  # NTU method
                # Perform NTU calculation
                hx = HeatExchanger(flow_arrangement=flow_type)
                results = hx.calculate_ntu(
                    T_hot_in, T_cold_in,
                    m_hot, m_cold, hot_fluid, cold_fluid, U_value, area
                )
                
                # Validate calculated temperatures
                is_valid, error_msg = validate_temperatures(
                    results['T_hot_in'], results['T_hot_out'],
                    results['T_cold_in'], results['T_cold_out'], flow_type
                )
                
                if not is_valid:
                    st.warning(f"⚠️ Calculated temperatures may be unrealistic: {error_msg}")
                
                # Display results
                st.success("✅ Calculation Complete!")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if unit_system.startswith("Metric"):
                        st.metric("Heat Transfer Rate", f"{results['Q']:.2f} kW")
                    else:
                        st.metric("Heat Transfer Rate", f"{kw_to_btu_per_hour(results['Q']):.0f} BTU/hr")
                
                with col2:
                    if unit_system.startswith("Metric"):
                        st.metric("Hot Outlet Temp", f"{results['T_hot_out']:.2f} °C")
                    else:
                        st.metric("Hot Outlet Temp", f"{celsius_to_fahrenheit(results['T_hot_out']):.2f} °F")
                
                with col3:
                    if unit_system.startswith("Metric"):
                        st.metric("Cold Outlet Temp", f"{results['T_cold_out']:.2f} °C")
                    else:
                        st.metric("Cold Outlet Temp", f"{celsius_to_fahrenheit(results['T_cold_out']):.2f} °F")
                
                with col4:
                    st.metric("Effectiveness", f"{results['effectiveness']*100:.1f}%")
                
                # Additional details (same as LMTD)
                with st.expander("📊 Detailed Results"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Performance:**")
                        st.write(f"- NTU: {results['NTU']:.2f}")
                        if unit_system.startswith("Metric"):
                            st.write(f"- Q_max: {results['Q_max']:.2f} kW")
                        else:
                            st.write(f"- Q_max: {kw_to_btu_per_hour(results['Q_max']):.0f} BTU/hr")
                    
                    with col2:
                        st.write("**Heat Capacity Rates:**")
                        st.write(f"- C_hot: {results['C_hot']:.0f} W/K")
                        st.write(f"- C_cold: {results['C_cold']:.0f} W/K")
                        st.write(f"- C_ratio: {results['C_ratio']:.3f}")
                        st.write(f"- Energy Balance Error: {results['energy_balance_error']:.2f}%")
                
                # Temperature profile
                st.subheader("🌡️ Temperature Profile")
                
                x, T_hot, T_cold = generate_temperature_profile(
                    results['T_hot_in'], results['T_hot_out'],
                    results['T_cold_in'], results['T_cold_out'], flow_type
                )
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=x*100, y=T_hot,
                    mode='lines',
                    name='Hot Fluid',
                    line=dict(color='red', width=3)
                ))
                
                fig.add_trace(go.Scatter(
                    x=x*100, y=T_cold,
                    mode='lines',
                    name='Cold Fluid',
                    line=dict(color='blue', width=3)
                ))
                
                fig.update_layout(
                    title=f"Temperature Profile - {flow_type}",
                    xaxis_title="Position (%)",
                    yaxis_title="Temperature (°C)" if unit_system.startswith("Metric") else "Temperature (°F)",
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Download results
                result_text = format_result_string(results)
                st.download_button(
                    label="📥 Download Results",
                    data=result_text,
                    file_name="heat_exchanger_results.txt",
                    mime="text/plain"
                )
        
        except Exception as e:
            st.error(f"❌ Error in calculation: {str(e)}")
            st.info("Please check your inputs and try again.")
    else:
        st.info("👈 Configure parameters and click Calculate to see results")

with tab3:
    st.header("📚 How to Use This Tool")
    
    st.markdown("""
    ### LMTD Method (Design Mode)
    Use when you know:
    - All inlet and outlet temperatures
    - Mass flow rates
    - Want to find: **Required heat exchanger area**
    
    **Formula:** `Q = U × A × LMTD`
    
    ### NTU Method (Rating Mode)
    Use when you know:
    - Inlet temperatures
    - Heat exchanger area (existing HX)
    - Want to find: **Outlet temperatures and performance**
    
    **Formula:** `ε = f(NTU, C_ratio)`
    
    ---
    
    ### Tips for Accurate Results
    1. **Counter flow is more efficient** than parallel flow
    2. **Check energy balance error** - should be < 1%
    3. **Typical U-values:**
       - Water-Water: 800-1500 W/(m²·K)
       - Water-Oil: 100-400 W/(m²·K)
       - Water-Air: 10-50 W/(m²·K)
    4. **Validate temperatures** - hot outlet must be > cold inlet
    
    ---
    
    ### About This Tool
    Built with Python, Streamlit, and CoolProp for accurate fluid properties.
    
    **GitHub:** [View Source Code](#)
    
    **Created by:** Your Name
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit | Heat Exchanger Design Tool v1.0
</div>
""", unsafe_allow_html=True)
