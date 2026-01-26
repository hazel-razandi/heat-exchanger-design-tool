"""
Heat Exchanger Design Tool - Main Streamlit Application
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Import modules
from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids, FluidProperties
from src.hx_types import HeatExchangerType
from src.utils import validate_temperatures, generate_temperature_profile
from src.pressure_drop import PressureDropCalculator
from src.cost_estimator import CostEstimator
from src.pdf_generator import generate_text_report
from src.design_storage import DesignStorage, DESIGN_TEMPLATES, list_available_templates

st.set_page_config(page_title="Heat Exchanger Design Tool", page_icon="🔥", layout="wide")

# Initialize Session State
if 'saved_designs' not in st.session_state:
    st.session_state.saved_designs = []
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

st.markdown("""
<style>
.main-header {font-size: 3rem; font-weight: bold; text-align: center; color: #FF4B4B;}
.sub-header {font-size: 1.2rem; text-align: center; color: #666;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🔥❄️ Heat Exchanger Design Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional thermal design with advanced analysis</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    st.subheader("📋 Templates")
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
    
    flow_type = st.selectbox("Flow Arrangement", ["Counter Flow", "Parallel Flow"])
    method = st.radio("Calculation Method", ["LMTD (Design)", "NTU (Rating)"])
    unit_system = st.selectbox("Unit System", ["Metric (°C, kW, m²)", "Imperial (°F, BTU/hr, ft²)"])
    
    st.markdown("---")
    include_fouling = st.checkbox("Include fouling resistance", value=False)
    calculate_pressure_drop = st.checkbox("Calculate pressure drop", value=True)
    estimate_costs = st.checkbox("Estimate costs", value=True)
    
    st.markdown("---")
    hx_type = st.selectbox("Heat Exchanger Type", HeatExchangerType.list_all_types())
    fluid_combo = st.selectbox("Fluid Combination", HeatExchangerType.get_fluid_combinations(hx_type))
    
    if st.button("Get Typical U-value"):
        min_u, max_u = HeatExchangerType.get_typical_U_value(hx_type, fluid_combo)
        avg_u = (min_u + max_u) / 2
        st.success(f"Range: {min_u}-{max_u} W/(m²·K) | Avg: {avg_u:.0f}")

# Main Interface Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Calculator", "📊 Results", "📄 Reports", "💾 Saved", "📚 Info"])

with tab1:
    st.header("Heat Exchanger Design Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Hot Fluid")
        hot_fluid = st.selectbox("Fluid Type (Hot)", get_available_fluids(), key="hot_fluid")
        
        # Initialize variables to avoid scope errors
        T_hot_in = 90.0
        T_hot_out = 50.0
        m_hot = 2.0
        
        if unit_system.startswith("Metric"):
            T_hot_in = st.number_input("Inlet Temp (°C)", value=90.0 if not template_data else template_data.get('T_hot_in', 90.0), step=1.0)
            if method == "LMTD (Design)":
                T_hot_out = st.number_input("Outlet Temp (°C)", value=50.0 if not template_data else template_data.get('T_hot_out', 50.0), step=1.0)
            else:
                T_hot_out = None
            m_hot = st.number_input("Mass Flow (kg/s)", value=2.0 if not template_data else template_data.get('m_hot', 2.0), step=0.1, min_value=0.01)
        else:
            T_hot_in_f = st.number_input("Inlet Temp (°F)", value=194.0, step=1.0)
            T_hot_in = (T_hot_in_f - 32) * 5/9
            if method == "LMTD (Design)":
                T_hot_out_f = st.number_input("Outlet Temp (°F)", value=122.0, step=1.0)
                T_hot_out = (T_hot_out_f - 32) * 5/9
            else:
                T_hot_out = None
            m_hot_lb = st.number_input("Mass Flow (lb/hr)", value=15873.0, step=100.0, min_value=0.01)
            m_hot = m_hot_lb / 7936.64
    
    with col2:
        st.subheader("🔵 Cold Fluid")
        cold_fluid = st.selectbox("Fluid Type (Cold)", get_available_fluids(), key="cold_fluid")
        
        # Initialize variables
        T_cold_in = 25.0
        T_cold_out = 45.0
        m_cold = 3.0

        if unit_system.startswith("Metric"):
            T_cold_in = st.number_input("Inlet Temp (°C)", value=25.0 if not template_data else template_data.get('T_cold_in', 25.0), step=1.0)
            if method == "LMTD (Design)":
                T_cold_out = st.number_input("Outlet Temp (°C)", value=45.0 if not template_data else template_data.get('T_cold_out', 45.0), step=1.0)
            else:
                T_cold_out = None
            m_cold = st.number_input("Mass Flow (kg/s)", value=3.0 if not template_data else template_data.get('m_cold', 3.0), step=0.1, min_value=0.01)
        else:
            T_cold_in_f = st.number_input("Inlet Temp (°F)", value=77.0, step=1.0)
            T_cold_in = (T_cold_in_f - 32) * 5/9
            if method == "LMTD (Design)":
                T_cold_out_f = st.number_input("Outlet Temp (°F)", value=113.0, step=1.0)
                T_cold_out = (T_cold_out_f - 32) * 5/9
            else:
                T_cold_out = None
            m_cold_lb = st.number_input("Mass Flow (lb/hr)", value=23810.0, step=100.0, min_value=0.01)
            m_cold = m_cold_lb / 7936.64
    
    st.markdown("---")
    st.subheader("🔧 Parameters")
    
    col3, col4 = st.columns(2)
    
    with col3:
        U_value_clean = st.number_input("Overall HTC (W/m²·K)", value=500.0 if not template_data else template_data.get('U_value', 500.0), step=50.0, min_value=1.0)
    
    with col4:
        if method == "NTU (Rating)":
            area = st.number_input("HX Area (m²)", value=12.4 if not template_data else template_data.get('area', 12.4), step=0.5, min_value=0.1)
        else:
            area = None
    
    if include_fouling:
        col5, col6 = st.columns(2)
        with col5:
            fouling_hot = st.number_input("Hot Fouling (m²·K/W)", value=0.0002, step=0.0001, format="%.4f", min_value=0.0)
        with col6:
            fouling_cold = st.number_input("Cold Fouling (m²·K/W)", value=0.0002, step=0.0001, format="%.4f", min_value=0.0)
        U_value = 1 / (1/U_value_clean + fouling_hot + fouling_cold)
        st.info(f"Fouled U: {U_value:.1f} W/(m²·K)")
    else:
        U_value = U_value_clean
    
    st.markdown("---")
    
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        calculate_button = st.button("🚀 Calculate", type="primary", use_container_width=True)
    with col_b:
        save_button = st.button("💾 Save", use_container_width=True)
    with col_c:
        clear_button = st.button("🗑️ Clear", use_container_width=True)

    if calculate_button:
        try:
            hx = HeatExchanger(flow_arrangement=flow_type)
            
            if method == "LMTD (Design)":
                is_valid, error_msg = validate_temperatures(T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    st.stop()
                results = hx.calculate_lmtd(T_hot_in, T_hot_out, T_cold_in, T_cold_out, m_hot, m_cold, hot_fluid, cold_fluid, U_value)
            else:
                results = hx.calculate_ntu(T_hot_in, T_cold_in, m_hot, m_cold, hot_fluid, cold_fluid, U_value, area)
            
            # Enrich results
            results['hot_fluid'] = hot_fluid
            results['cold_fluid'] = cold_fluid
            results['hx_type'] = hx_type
            results['m_hot'] = m_hot
            results['m_cold'] = m_cold
            
            # --- PRESSURE DROP CALCULATION ---
            if calculate_pressure_drop and hx_type in ['Shell-and-Tube', 'Plate']:
                try:
                    pd_calc = PressureDropCalculator(hx_type=hx_type)
                    # Use the calculated area
                    calc_area = results['area']
                    
                    geometry = pd_calc.estimate_geometry_from_area(calc_area, hx_type)
                    
                    hot_props = FluidProperties(hot_fluid)
                    cold_props = FluidProperties(cold_fluid)
                    
                    # Avg temps for properties
                    T_hot_avg = (results['T_hot_in'] + results['T_hot_out']) / 2
                    T_cold_avg = (results['T_cold_in'] + results['T_cold_out']) / 2
                    
                    hot_dp = pd_calc.calculate_tube_side_pressure_drop(
                        m_hot, hot_props.get_density(T_hot_avg), hot_props.get_dynamic_viscosity(T_hot_avg),
                        geometry.get('tube_diameter_inner', 0.022), geometry.get('tube_length', 4.0), 
                        geometry.get('n_tubes', 10), geometry.get('n_passes', 2)
                    )
                    
                    # Simplified assumption: cold fluid is shell side
                    cold_dp = pd_calc.calculate_shell_side_pressure_drop(
                        m_cold, cold_props.get_density(T_cold_avg), cold_props.get_dynamic_viscosity(T_cold_avg),
                        geometry.get('shell_diameter', 0.5), geometry.get('tube_diameter_outer', 0.025), 
                        geometry.get('n_tubes', 10), geometry.get('baffle_spacing', 0.5), geometry.get('n_baffles', 8)
                    )
                    
                    hot_pump = pd_calc.calculate_pumping_power(m_hot, hot_dp['pressure_drop_Pa'], hot_props.get_density(T_hot_avg))
                    cold_pump = pd_calc.calculate_pumping_power(m_cold, cold_dp['pressure_drop_Pa'], cold_props.get_density(T_cold_avg))
                    
                    total_power = hot_pump['actual_power_kW'] + cold_pump['actual_power_kW']
                    annual = pd_calc.calculate_annual_pumping_cost(total_power)
                    
                    results['pressure_drop'] = {
                        'hot_side': hot_dp,
                        'cold_side': cold_dp,
                        'pumping': {
                            'total_power_kW': total_power,
                            'total_power_HP': total_power * 1.341,
                            'annual_energy_kWh': annual['annual_energy_kWh'],
                            'annual_cost': annual['annual_cost_USD']
                        }
                    }
                except Exception as e:
                    st.warning(f"⚠️ Pressure drop calculation skipped: {str(e)}")

            # --- COST ESTIMATION ---
            if estimate_costs:
                try:
                    cost_est = CostEstimator()
                    eq_cost = cost_est.estimate_equipment_cost(results['area'], hx_type, 'Stainless Steel 304', 'Low')
                    
                    pump_power = results.get('pressure_drop', {}).get('pumping', {}).get('total_power_kW', 0)
                    op_cost = cost_est.estimate_annual_operating_cost(pump_power)
                    ma_cost = cost_est.estimate_maintenance_cost(eq_cost['equipment_cost'], 'Standard')
                    
                    lc_cost = cost_est.calculate_lifecycle_cost(
                        eq_cost['total_project_cost'], 
                        op_cost['annual_energy_cost'], 
                        ma_cost['annual_maintenance_total']
                    )
                    
                    results['costs'] = {
                        'equipment': eq_cost,
                        'operating': {
                            'annual_energy_cost': op_cost['annual_energy_cost'], 
                            'annual_maintenance_cost': ma_cost['annual_maintenance_total'], 
                            'total_annual': op_cost['annual_energy_cost'] + ma_cost['annual_maintenance_total']
                        },
                        'lifecycle': lc_cost
                    }
                except Exception as e:
                    st.warning(f"⚠️ Cost estimation skipped: {str(e)}")
            
            st.session_state.current_results = results
            st.success("✅ Calculation complete!")
            
        except Exception as e:
            st.error(f"❌ Calculation Error: {str(e)}")

    if clear_button:
        st.session_state.current_results = None
        st.rerun()
    
    if save_button and st.session_state.current_results:
        name = st.text_input("Name this design", f"Design_{datetime.now().strftime('%Y%m%d_%H%M')}")
        if st.button("Confirm Save"):
            storage = DesignStorage()
            snap = storage.create_design_snapshot({'results': st.session_state.current_results}, name)
            st.session_state.saved_designs.append(snap)
            st.success(f"✅ Saved: {name}")

with tab2:
    st.header("Results Analysis")
    if st.session_state.current_results:
        r = st.session_state.current_results
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Heat Transfer", f"{r.get('Q', 0):.2f} kW")
        col2.metric("Required Area", f"{r.get('area', 0):.2f} m²")
        col3.metric("Effectiveness", f"{r.get('effectiveness', 0)*100:.1f}%")
        col4.metric("NTU", f"{r.get('NTU', 0):.2f}")
        
        st.subheader("📈 Temperature Profile")
        try:
            x, Th, Tc = generate_temperature_profile(r['T_hot_in'], r['T_hot_out'], r['T_cold_in'], r['T_cold_out'], r['flow_type'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x*100, y=Th, mode='lines', name='Hot Fluid', line=dict(color='red', width=3)))
            fig.add_trace(go.Scatter(x=x*100, y=Tc, mode='lines', name='Cold Fluid', line=dict(color='blue', width=3)))
            fig.update_layout(xaxis_title="Position along Heat Exchanger (%)", yaxis_title="Temperature (°C)", height=400)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Could not generate graph.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Thermal Performance:**\n\nQ = {r['Q']:.2f} kW\n\nEnergy Balance Error = {r.get('energy_balance_error', 0):.2f}%")
        with col2:
            st.info(f"**Design Specs:**\n\nU-Value = {r['U_value']:.0f} W/m²K\n\nArea = {r['area']:.2f} m²")
        
        if 'pressure_drop' in r:
            with st.expander("⚡ Pressure Drop & Pumping Details"):
                pd = r['pressure_drop']
                st.write(f"**Hot Side Pressure Drop:** {pd['hot_side']['pressure_drop_kPa']:.2f} kPa")
                st.write(f"**Cold Side Pressure Drop:** {pd['cold_side']['pressure_drop_kPa']:.2f} kPa")
                st.write(f"**Total Pumping Power:** {pd['pumping']['total_power_kW']:.3f} kW")
                st.write(f"**Est. Annual Pumping Cost:** ${pd['pumping']['annual_cost']:.0f}/yr")
        
        if 'costs' in r:
            with st.expander("💰 Cost Estimation"):
                c = r['costs']
                st.write(f"**Capital Equipment Cost:** ${c['equipment']['total_project_cost']:,.0f}")
                st.write(f"**Total Annual Operating Cost:** ${c['operating']['total_annual']:,.0f}/yr")
                st.write(f"**20-Year Lifecycle Cost:** ${c['lifecycle']['total_lifecycle_cost']:,.0f}")
    else:
        st.info("👈 Run a calculation in the 'Calculator' tab to see results here.")

with tab3:
    st.header("Generate Reports")
    if st.session_state.current_results:
        proj = {
            'project_name': st.text_input("Project Name", "HX Design Project"),
            'engineer_name': st.text_input("Engineer Name", ""),
            'company': st.text_input("Company", ""),
            'location': st.text_input("Location", ""), 
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        if st.button("Generate Text Report"):
            report = generate_text_report(st.session_state.current_results, st.session_state.current_results.get('pressure_drop'), st.session_state.current_results.get('costs'), proj)
            st.text_area("Report Preview", report, height=400)
            st.download_button("📥 Download Report (.txt)", report, f"{proj['project_name']}_Report.txt", "text/plain")
    else:
        st.info("Run a calculation first to generate a report.")

with tab4:
    st.header("Saved Designs")
    if st.session_state.saved_designs:
        for i, d in enumerate(st.session_state.saved_designs):
            with st.expander(f"{d['design_name']} ({d['date_readable']})"):
                r = d['data'].get('results', {})
                st.write(f"Q={r.get('Q', 0):.2f} kW | Area={r.get('area', 0):.2f} m² | Eff={r.get('effectiveness', 0)*100:.1f}%")
                if st.button(f"Load Design #{i+1}", key=f"load_{i}"):
                    st.session_state.current_results = r
                    st.rerun()
    else:
        st.info("No designs saved yet. Use the 'Save' button in the Calculator tab.")

with tab5:
    st.header("Information & Theory")
    st.markdown("""
    ### Methods Used
    
    **1. LMTD Method (Design Mode):**
    Used when inlet and outlet temperatures are known. Calculates the Log Mean Temperature Difference to determine the required surface area.
    $$ Q = U \\times A \\times LMTD $$
    
    **2. NTU Method (Rating Mode):**
    Used when the heat exchanger Area (A) is known. Calculates the Number of Transfer Units (NTU) to predict effectiveness and outlet temperatures.
    $$ NTU = \\frac{UA}{C_{min}} $$
    
    ### Fluid Properties
    Thermophysical properties (Density, Specific Heat, Viscosity, Conductivity) are retrieved dynamically using **CoolProp**, an open-source database comparable to NIST Refprop.
    """)
