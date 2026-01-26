"""
ExchangerPro: Enterprise Design Tool
Developed by KAKAROTONCLOUD
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- IMPORT CORE MODULES ---
from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids
from src.hx_types import EngineeringDB
from src.utils import validate_temperatures, generate_temperature_profile
from src.pressure_drop import PressureDropCalculator
from src.cost_estimator import CostEstimator
from src.pdf_generator import generate_text_report
from src.design_storage import DesignStorage

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ExchangerPro | KAKAROTONCLOUD",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR "PAID APP" FEEL ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;}
    .report-view {font-family: 'Courier New', monospace; background-color: #262730; color: #ffffff; padding: 15px;}
    .main-header {font-size: 2.5rem; font-weight: 700; color: #1E1E1E;}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'results' not in st.session_state: st.session_state.results = None

# --- SIDEBAR: PROJECT SETTINGS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=50) # Generic Icon
    st.title("ExchangerPro")
    st.caption(f"v3.0.0 Enterprise | User: KAKAROTONCLOUD")
    st.divider()
    
    st.subheader("⚙️ Design Basis")
    calc_mode = st.selectbox("Calculation Mode", ["Design (Calculate Area)", "Rating (Verify Performance)"])
    hx_config = st.selectbox("Configuration", EngineeringDB.get_hx_types())
    flow_arr = st.radio("Flow Arrangement", ["Counter Flow", "Parallel Flow"], horizontal=True)
    
    st.divider()
    st.subheader("🏗️ Mechanical Specs")
    material = st.selectbox("Material of Construction", EngineeringDB.get_material_list())
    fouling_service = st.selectbox("Fouling Service", EngineeringDB.get_fouling_services())
    fouling_factor = EngineeringDB.FOULING_SERVICES[fouling_service]
    st.info(f"Fouling Factor: {fouling_factor} m²K/W")

# --- MAIN DASHBOARD ---
st.markdown('<div class="main-header">🏭 Heat Exchanger Design Suite</div>', unsafe_allow_html=True)
st.markdown("---")

# INPUT SECTION
col_main_1, col_main_2, col_main_3 = st.columns([1, 1, 0.8])

with col_main_1:
    st.markdown("### 🔴 Hot Stream")
    h_fluid = st.selectbox("Fluid", get_available_fluids(), key="hf")
    h_flow = st.number_input("Mass Flow (kg/s)", value=5.0, min_value=0.1, key="hf_m")
    h_tin = st.number_input("Inlet Temp (°C)", value=95.0, key="hf_ti")
    if calc_mode.startswith("Design"):
        h_tout = st.number_input("Target Outlet (°C)", value=60.0, key="hf_to")
    else:
        h_tout = None

with col_main_2:
    st.markdown("### 🔵 Cold Stream")
    c_fluid = st.selectbox("Fluid", get_available_fluids(), key="cf")
    c_flow = st.number_input("Mass Flow (kg/s)", value=8.0, min_value=0.1, key="cf_m")
    c_tin = st.number_input("Inlet Temp (°C)", value=25.0, key="cf_ti")
    if calc_mode.startswith("Design"):
        c_tout = st.number_input("Target Outlet (°C)", value=40.0, key="cf_to")
    else:
        c_tout = None

with col_main_3:
    st.markdown("### 🧮 Parameters")
    
    # Smart U-Value Suggestion
    base_u = EngineeringDB.HX_TYPES[hx_config]['base_u']
    u_val = st.number_input("Overall U (W/m²K)", value=float(base_u), help="Includes fouling impact")
    
    if calc_mode.startswith("Rating"):
        area_val = st.number_input("Surface Area (m²)", value=50.0)
    else:
        area_val = None
        
    st.markdown("##")
    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        with st.spinner("Solving Energy Balance & Hydraulics..."):
            try:
                # 1. THERMAL CALC
                hx = HeatExchanger(flow_arrangement=flow_arr)
                if calc_mode.startswith("Design"):
                    # Validate
                    valid, msg = validate_temperatures(h_tin, h_tout, c_tin, c_tout, flow_arr)
                    if not valid:
                        st.error(f"Physics Violation: {msg}")
                        st.stop()
                    res = hx.calculate_lmtd(h_tin, h_tout, c_tin, c_tout, h_flow, c_flow, h_fluid, c_fluid, u_val)
                else:
                    res = hx.calculate_ntu(h_tin, c_tin, h_flow, c_flow, h_fluid, c_fluid, u_val, area_val)
                
                # 2. HYDRAULICS
                pd = PressureDropCalculator(hx_config)
                # Pass explicit arguments to avoid argument mismatch
                res['hydraulics'] = pd.calculate_tube_side_pressure_drop(
                    h_flow, 990, 0.0008, 0.025, 6.0, 50, 2
                )
                
                # 3. FINANCIALS
                ce = CostEstimator()
                res['financials'] = ce.estimate_project_budget(res.get('area', 10), hx_config, material)
                
                # 4. METADATA
                res['meta'] = {
                    'material': material,
                    'fouling': fouling_factor,
                    'config': hx_config
                }
                
                st.session_state.results = res
                st.success("Simulation Converged Successfully")
                
            except Exception as e:
                st.error(f"Simulation Failed: {str(e)}")

# RESULTS SECTION
if st.session_state.results:
    res = st.session_state.results
    
    st.markdown("---")
    
    # KPI CARDS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Thermal Duty", f"{res['Q']:.1f} kW", delta="Heat Load")
    k2.metric("Required Area", f"{res['area']:.1f} m²", help="Heat Transfer Surface")
    k3.metric("Effectiveness", f"{res['effectiveness']*100:.1f} %")
    k4.metric("Est. CAPEX", f"${res['financials']['total_capex']/1000:.1f}k", delta_color="inverse")

    # TABS FOR DETAILS
    tab_perf, tab_mech, tab_doc = st.tabs(["📈 Performance Analysis", "⚙️ Mechanical & Cost", "📄 Export Report"])
    
    with tab_perf:
        col_graph, col_data = st.columns([2, 1])
        with col_graph:
            x, th, tc = generate_temperature_profile(res['T_hot_in'], res['T_hot_out'], res['T_cold_in'], res['T_cold_out'], flow_arr)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x*100, y=th, name='Hot Stream', line=dict(color='#FF4B4B', width=4)))
            fig.add_trace(go.Scatter(x=x*100, y=tc, name='Cold Stream', line=dict(color='#0068C9', width=4)))
            fig.update_layout(
                title="Temperature Profile (T-Q Diagram)",
                xaxis_title="Heat Exchanger Length (%)",
                yaxis_title="Temperature (°C)",
                template="plotly_white",
                height=400,
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_data:
            st.markdown("#### Hydraulic Data (Tube Side)")
            hyd = res['hydraulics']
            st.write(f"**Velocity:** {hyd['velocity_m_s']:.2f} m/s")
            st.write(f"**Reynolds No:** {hyd['reynolds']:.0f}")
            
            if hyd['reynolds'] > 4000:
                st.success(f"Flow is {hyd['regime']}")
            else:
                st.warning(f"Flow is {hyd['regime']} (Low Efficiency)")
                
            st.metric("Pressure Drop", f"{hyd['pressure_drop_kPa']:.2f} kPa")

    with tab_mech:
        fin = res['financials']
        st.markdown(f"### Class 4 Cost Estimate (+/- 30%)")
        st.markdown(f"**Basis:** {res['meta']['material']} | {res['meta']['config']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Direct Costs**")
            st.progress(fin['equipment_fob'] / fin['total_capex'])
            st.write(f"- Equipment (FOB): ${fin['equipment_fob']:,.2f}")
            st.write(f"- Installation: ${fin['installation_labor']:,.2f}")
            st.write(f"- Bulk Materials: ${fin['bulk_materials']:,.2f}")
            
        with c2:
            st.write("**Indirect Costs**")
            st.progress(fin['indirects'] / fin['total_capex'])
            st.write(f"- Engineering & Contingency: ${fin['indirects']:,.2f}")
            st.divider()
            st.metric("Total Installed Cost (TIC)", f"${fin['total_capex']:,.2f}")

    with tab_doc:
        st.markdown("### 🖨️ Project Documentation")
        p_name = st.text_input("Project Reference ID", "HX-2024-001")
        
        if st.button("Generate Engineering Report"):
            # Pass dictionary structures correctly
            report_text = generate_text_report(
                res, 
                res.get('hydraulics'), 
                {'total_project_cost': res['financials']['total_capex'], 
                 'base_equipment': res['financials']['equipment_fob'],
                 'installation': res['financials']['installation_labor']}, 
                {'project_name': p_name}
            )
            st.code(report_text, language='text')
            st.download_button("Download Spec Sheet (.txt)", report_text, f"{p_name}_Spec.txt")

