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

st.set_page_config(
    page_title="Heat Exchanger Design Tool",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'saved_designs' not in st.session_state:
    st.session_state.saved_designs = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

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

st.markdown('<div class="main-header">🔥❄️ Heat Exchanger Design Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional thermal design with advanced analysis</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <span class="feature-badge">⚡ Pressure Drop</span>
    <span class="feature-badge">💰 Cost Estimation</span>
    <span class="feature-badge">📄 PDF Reports</span>
    <span class="feature-badge">💾 Save/Load</span>
    <span class="feature-badge">🧼 Fouling Factors</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Configuration")
    
    st.subheader("📋 Quick Start Templates")
    templates = list_available_templates()
    template_options = ['Custom Design'] + [t['name'] for t in templates]
    selected_template = st.selectbox("Load Template", template_options)
    
    template_data = None
    if selected_template != 'Custom Design':
        for t in templates:
            if t['name'] == selected_template:
                template_key = t['key']
                template_data = DESIGN_TEMPLATES[template_key]['defaults']
                st.info(f"📝 {DESIGN_TEMPLATES[template_key]['description']}")
                break
    
    st.markdown("---")
    
    flow_type = st.selectbox(
        "Flow Arrangement",
        ["Counter Flow", "Parallel Flow"],
        help="Counter flow is more efficient"
    )
    
    method = st.radio(
        "Calculation Method",
        ["LMTD (Design)", "NTU (Rating)"],
        help="LMTD: Calculate required area | NTU: Analyze existing HX"
    )
    
    unit_system = st.selectbox(
        "Unit System",
        ["Metric (°C, kW, m²)", "Imperial (°F, BTU/hr, ft²)"]
    )
    
    st.markdown("---")
    st.subheader("🧼 Fouling Factors")
    include_fouling = st.checkbox("Include fouling resistance", value=False)
    
    st.markdown("---")
    st.subheader("🔧 Advanced Options")
    calculate_pressure_drop = st.checkbox("Calculate pressure drop", value=True)
    estimate_costs = st.checkbox("Estimate costs", value=True)
    
    st.markdown("---")
    
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
        st.success(f"Typical U-value: {min_u} - {max_u} W/(m²·K) | Average: {avg_u:.0f} W/(m²·K)")
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
            else:
                T_hot_out = None
            m_hot = st.number_input("Mass Flow Rate (kg/s)", 
                                   value=template_data.get('m_hot', 2.0) if template_data else 2.0,
                                   step=0.1, min_value=0.01, key="m_hot")
        else:
            T_hot_in_f = st.number_input("Inlet Temperature (°F)", value=194.0, step=1.0, key="T_hot_in_f")
            T_hot_in = (T_hot_in_f - 32) * 5/9
            if method == "LMTD (Design)":
                T_hot_out_f = st.number_input("Outlet Temperature (°F)", value=122.0, step=1.0, key="T_hot_out_f")
                T_hot_out = (T_hot_out_f - 32) * 5/9
            else:
                T_hot_out = None
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
            else:
                T_cold_out = None
            
            m_cold = st.number_input("Mass Flow Rate (kg/s)", 
                                    value=template_data.get('m_cold', 3.0) if template_data else 3.0,
                                    step=0.1, min_value=0.01, key="m_cold")
        else:
            T_cold_in_f = st.number_input("Inlet Temperature (°F)", value=77.0, step=1.0, key="T_cold_in_f")
            T_cold_in = (T_cold_in_f - 32) * 5/9
            
            if method == "LMTD (Design)":
                T_cold_out_f = st.number_input("Outlet Temperature (°F)", value=113.0, step=1.0, key="T_cold_out_f")
                T_cold_out = (T_cold_out_f - 32) * 5/9
            else:
                T_cold_out = None
            
            m_cold_lb = st.number_input("Mass Flow Rate (lb/hr)", value=23810.0, step=100.0, min_value=0.01, key="m_cold_lb")
            m_cold = m_cold_lb / 7936.64
    
    st.markdown("---")
    
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
        else:
            area = None
    
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
            U_value = 1 / (1/U_value_clean + fouling_hot + fouling_cold)
            degradation = ((U_value_clean - U_value)/U_value_clean * 100)
            st.info(f"Fouled U-value: {U_value:.1f} W/(m²·K) | Degradation: {degradation:.1f}%")
        else:
            U_value = U_value_clean
    
    st.markdown("---")
    
    col_calc1, col_calc2, col_calc3 = st.columns([2, 1, 1])
    with col_calc1:
        calculate_button = st.button("🚀 Calculate Heat Exchanger Performance", type="primary", use_container_width=True)
    with col_calc2:
        save_design_button = st.button("💾 Save Design", use_container_width=True)
    with col_calc3:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
        if calculate_button:
        try:
            if method == "LMTD (Design)":
                is_valid, error_msg = validate_temperatures(T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type)
                if not is_valid:
                    st.error(f"❌ Temperature Validation Error: {error_msg}")
                    st.stop()
                
                hx = HeatExchanger(flow_arrangement=flow_type)
                results = hx.calculate_lmtd(
                    T_hot_in=T_hot_in, T_hot_out=T_hot_out,
                    T_cold_in=T_cold_in, T_cold_out=T_cold_out,
                    m_hot=m_hot, m_cold=m_cold,
                    fluid_hot=hot_fluid, fluid_cold=cold_fluid,
                    U_value=U_value
                )
            else:
                hx = HeatExchanger(flow_arrangement=flow_type)
                results = hx.calculate_ntu(
                    T_hot_in=T_hot_in, T_cold_in=T_cold_in,
                    m_hot=m_hot, m_cold=m_cold,
                    fluid_hot=hot_fluid, fluid_cold=cold_fluid,
                    U_value=U_value, Area=area
                )
            
            results['hot_fluid'] = hot_fluid
            results['cold_fluid'] = cold_fluid
            results['hx_type'] = hx_type
            results['m_hot'] = m_hot
            results['m_cold'] = m_cold
            
            if calculate_pressure_drop:
                try:
                    pd_calc = PressureDropCalculator(hx_type=hx_type)
                    geometry = pd_calc.estimate_geometry_from_area(results['area'], hx_type)
                    hot_props = FluidProperties(hot_fluid)
                    cold_props = FluidProperties(cold_fluid)
                    T_hot_avg = (results['T_hot_in'] + results['T_hot_out']) / 2
                    T_cold_avg = (results['T_cold_in'] + results['T_cold_out']) / 2
                    
                    if hx_type == 'Shell-and-Tube' and 'n_tubes' in geometry:
                        hot_dp = pd_calc.calculate_tube_side_pressure_drop(
                            mass_flow=m_hot,
                            density=hot_props.get_density(T_hot_avg),
                            viscosity=hot_props.get_dynamic_viscosity(T_hot_avg),
                            tube_diameter=geometry['tube_diameter_inner'],
                            tube_length=geometry['tube_length'],
                            n_tubes=geometry['n_tubes'],
                            n_passes=geometry['n_passes']
                        )
                        cold_dp = pd_calc.calculate_shell_side_pressure_drop(
                            mass_flow=m_cold,
                            density=cold_props.get_density(T_cold_avg),
                            viscosity=cold_props.get_dynamic_viscosity(T_cold_avg),
                            shell_diameter=geometry['shell_diameter'],
                            tube_diameter=geometry['tube_diameter_outer'],
                            n_tubes=geometry['n_tubes'],
                            baffle_spacing=geometry['baffle_spacing'],
                            n_baffles=geometry['n_baffles']
                        )
                        hot_pump = pd_calc.calculate_pumping_power(
                            m_hot, hot_dp['pressure_drop_Pa'],
                            hot_props.get_density(T_hot_avg)
                        )
                        cold_pump = pd_calc.calculate_pumping_power(
                            m_cold, cold_dp['pressure_drop_Pa'],
                            cold_props.get_density(T_cold_avg)
                        )
                        total_power = hot_pump['actual_power_kW'] + cold_pump['actual_power_kW']
                        annual_cost = pd_calc.calculate_annual_pumping_cost(total_power)
                        
                        results['pressure_drop'] = {
                            'hot_side': hot_dp,
                            'cold_side': cold_dp,
                            'pumping': {
                                'hot_power_kW': hot_pump['actual_power_kW'],
                                'cold_power_kW': cold_pump['actual_power_kW'],
                                'total_power_kW': total_power,
                                'total_power_HP': total_power * 1.341,
                                'annual_energy_kWh': annual_cost['annual_energy_kWh'],
                                'annual_cost': annual_cost['annual_cost_USD']
                            }
                        }
                except Exception as e:
                    st.warning(f"⚠️ Pressure drop calculation failed: {e}")
            
            if estimate_costs:
                try:
                    cost_est = CostEstimator()
                    equipment_cost = cost_est.estimate_equipment_cost(
                        area=results['area'], hx_type=hx_type,
                        material='Stainless Steel 304', pressure_rating='Low'
                    )
                    
                    if 'pressure_drop' in results and 'pumping' in results['pressure_drop']:
                        operating_cost = cost_est.estimate_annual_operating_cost(
                            pumping_power_kW=results['pressure_drop']['pumping']['total_power_kW']
                        )
                    else:
                        operating_cost = {'annual_energy_cost': 0}
                    
                    maintenance_cost = cost_est.estimate_maintenance_cost(
                        equipment_cost=equipment_cost['equipment_cost'],
                        maintenance_type='Standard'
                    )
                    lifecycle_cost = cost_est.calculate_lifecycle_cost(
                        equipment_cost=equipment_cost['total_project_cost'],
                        annual_operating_cost=operating_cost['annual_energy_cost'],
                        annual_maintenance_cost=maintenance_cost['annual_maintenance_total']
                    )
                    
                    results['costs'] = {
                        'equipment': equipment_cost,
                        'operating': {
                            'annual_energy_cost': operating_cost['annual_energy_cost'],
                            'annual_maintenance_cost': maintenance_cost['annual_maintenance_total'],
                            'total_annual': operating_cost['annual_energy_cost'] + maintenance_cost['annual_maintenance_total']
                        },
                        'lifecycle': lifecycle_cost
                    }
                except Exception as e:
                    st.warning(f"⚠️ Cost estimation failed: {e}")
            
            st.session_state.current_results = results
            st.success("✅ Calculation completed successfully!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Calculation Error: {str(e)}")
    
    if clear_button:
        st.session_state.current_results = None
        st.rerun()
    
    if save_design_button and st.session_state.current_results:
        design_name = st.text_input("Design Name", f"Design_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if st.button("💾 Confirm Save"):
            storage = DesignStorage()
            snapshot = storage.create_design_snapshot(
                {'results': st.session_state.current_results}, design_name
            )
            st.session_state.saved_designs.append(snapshot)
            st.success(f"✅ Saved: {design_name}")
            with tab2:
    st.header("Results & Advanced Analysis")
    
    if st.session_state.current_results:
        results = st.session_state.current_results
        st.success("✅ Results Available")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Heat Transfer", f"{results.get('Q', 0):.2f} kW")
        with col2:
            st.metric("Area", f"{results.get('area', 0):.2f} m²")
        with col3:
            st.metric("Effectiveness", f"{results.get('effectiveness', 0)*100:.1f}%")
        with col4:
            st.metric("NTU", f"{results.get('NTU', 0):.2f}")
        
        st.markdown("---")
        st.subheader("📈 Temperature Profile")
        
        x, T_hot, T_cold = generate_temperature_profile(
            results['T_hot_in'], results['T_hot_out'],
            results['T_cold_in'], results['T_cold_out'],
            results['flow_type']
        )
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x*100, y=T_hot, mode='lines', name='Hot Fluid',
                                line=dict(color='red', width=3)))
        fig.add_trace(go.Scatter(x=x*100, y=T_cold, mode='lines', name='Cold Fluid',
                                line=dict(color='blue', width=3)))
        fig.update_layout(title=f"Temperature Profile - {results['flow_type']}",
                         xaxis_title="Position (%)", yaxis_title="Temperature (°C)",
                         hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Detailed Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Thermal Performance:**")
            st.write(f"- Heat Transfer Rate: {results['Q']:.2f} kW")
            st.write(f"- Heat from Hot: {results.get('Q_hot', 0):.2f} kW")
            st.write(f"- Heat to Cold: {results.get('Q_cold', 0):.2f} kW")
            st.write(f"- Energy Balance Error: {results.get('energy_balance_error', 0):.2f}%")
        
        with col2:
            st.write("**Design Parameters:**")
            st.write(f"- U-value: {results['U_value']:.1f} W/(m²·K)")
            st.write(f"- Heat Transfer Area: {results['area']:.2f} m²")
            if 'LMTD' in results:
                st.write(f"- LMTD: {results['LMTD']:.2f} °C")
            st.write(f"- NTU: {results['NTU']:.2f}")
            st.write(f"- Effectiveness: {results['effectiveness']*100:.1f}%")
        
        if 'pressure_drop' in results:
            st.markdown("---")
            with st.expander("⚡ Pressure Drop Analysis", expanded=True):
                pd_data = results['pressure_drop']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Hot Side:**")
                    if 'hot_side' in pd_data:
                        st.write(f"- ΔP: {pd_data['hot_side']['pressure_drop_kPa']:.2f} kPa")
                        st.write(f"- Velocity: {pd_data['hot_side']['velocity_m_s']:.2f} m/s")
                with col2:
                    st.write("**Cold Side:**")
                    if 'cold_side' in pd_data:
                        st.write(f"- ΔP: {pd_data['cold_side']['pressure_drop_kPa']:.2f} kPa")
                        st.write(f"- Velocity: {pd_data['cold_side']['velocity_m_s']:.2f} m/s")
                with col3:
                    st.write("**Pumping:**")
                    if 'pumping' in pd_data:
                        st.write(f"- Power: {pd_data['pumping']['total_power_kW']:.3f} kW")
                        st.write(f"- Annual: ${pd_data['pumping']['annual_cost']:.2f}/yr")
        
        if 'costs' in results:
            st.markdown("---")
            with st.expander("💰 Cost Analysis", expanded=True):
                cost_data = results['costs']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Equipment:**")
                    if 'equipment' in cost_data:
                        st.write(f"- Total: ${cost_data['equipment']['total_project_cost']:,.0f}")
                with col2:
                    st.write("**Annual Operating:**")
                    if 'operating' in cost_data:
                        st.write(f"- Total: ${cost_data['operating']['total_annual']:,.0f}/yr")
                with col3:
                    st.write("**Lifecycle (20 yrs):**")
                    if 'lifecycle' in cost_data:
                        st.write(f"- Total: ${cost_data['lifecycle']['total_lifecycle_cost']:,.0f}")
    else:
        st.info("👈 Run a calculation first to see results here")

with tab3:
    st.header("📄 Generate Professional Report")
    
    if st.session_state.current_results:
        st.subheader("Project Information")
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name", "Heat Exchanger Design")
            engineer_name = st.text_input("Engineer Name", "")
        with col2:
            company = st.text_input("Company", "")
            location = st.text_input("Location", "")
        
        project_info = {
            'project_name': project_name, 'engineer_name': engineer_name,
            'company': company, 'location': location,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        st.markdown("---")
        
        pressure_drop_data = st.session_state.current_results.get('pressure_drop', None)
        cost_data = st.session_state.current_results.get('costs', None)
        report_text = generate_text_report(st.session_state.current_results, pressure_drop_data, cost_data, project_info)
        
        st.subheader("Report Preview")
        st.text_area("", report_text, height=400)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Report (TXT)",
                data=report_text,
                file_name=f"{project_name.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            content, filename, mime = create_downloadable_report(
                st.session_state.current_results, pressure_drop_data, cost_data, project_info, format='csv'
            )
            st.download_button(
                label="📥 Download Summary (CSV)",
                data=content, file_name=filename, mime=mime,
                use_container_width=True
            )
    else:
        st.info("👈 Run a calculation first to generate a report")

with tab4:
    st.header("💾 Saved Designs")
    
    if st.session_state.saved_designs:
        for idx, design in enumerate(st.session_state.saved_designs):
            with st.expander(f"📁 {design['design_name']} - {design['date_readable']}"):
                results = design['data'].get('results', {})
                st.write(f"**Heat Transfer:** {results.get('Q', 0):.2f} kW")
                st.write(f"**Area:** {results.get('area', 0):.2f} m²")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🔄 Load", key=f"load_{idx}"):
                        st.session_state.current_results = results
                        st.success("Design loaded!")
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_{idx}"):
                        st.session_state.saved_designs.pop(idx)
                        st.success("Design deleted!")
                        st.rerun()
    else:
        st.info("No saved designs yet.")

with tab5:
    st.header("📚 Information & Help")
    st.markdown("""
    ## 🎯 How to Use This Tool
    
    ### LMTD Method (Design Mode)
    - All temperatures known
    - Finds required area
    
    ### NTU Method (Rating Mode)
    - Area known
    - Finds outlet temperatures
    
    ## 💡 Tips
    1. Counter flow is more efficient
    2. Check energy balance error (< 1%)
    3. Typical U-values: Water-Water 800-1500 W/(m²·K)
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    Made with ❤️ using Streamlit | Heat Exchanger Design Tool v2.0
</div>
""", unsafe_allow_html=True)
