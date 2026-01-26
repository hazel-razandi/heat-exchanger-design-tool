"""
ExchangerPro: Enterprise Design Tool
Developed by KAKAROTONCLOUD
"""
import streamlit as st
import plotly.graph_objects as go
import math
from datetime import datetime

# --- IMPORT CORE MODULES ---
from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids
from src.hx_types import EngineeringDB
from src.utils import validate_temperatures, generate_temperature_profile
from src.pressure_drop import PressureDropCalculator
from src.cost_estimator import CostEstimator
from src.pdf_generator import generate_text_report
# NEW IMPORTS FOR PRO FEATURES
from src.excel_exporter import generate_excel_datasheet
from src.geometry_plotter import plot_tube_layout

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ExchangerPro | KAKAROTONCLOUD",
    page_icon="🏭",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .big-metric {font-size: 32px !important; font-weight: bold;}
    .stAlert {border-radius: 8px;}
    .main-header {font-size: 2rem; font-weight: 700; color: #333;}
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'results' not in st.session_state: st.session_state.results = None

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=50)
    st.markdown("### ExchangerPro")
    st.caption("v3.1 Enterprise | KAKAROTONCLOUD")
    st.divider()
    
    st.subheader("⚙️ Design Basis")
    calc_mode = st.selectbox("Mode", ["Design (Calculate Area)", "Rating (Verify Performance)"])
    hx_config = st.selectbox("Config", EngineeringDB.get_configs())
    flow_arr = st.radio("Arrangement", ["Counter Flow", "Parallel Flow"])
    
    st.divider()
    st.subheader("🏗️ Materials & Fouling")
    material = st.selectbox("Material", EngineeringDB.get_material_list())
    fouling_service = st.selectbox("Service", EngineeringDB.get_fouling_services())
    fouling_factor = EngineeringDB.FOULING_SERVICES[fouling_service]
    st.info(f"Fouling Factor: {fouling_factor} m²K/W")

# --- MAIN DASHBOARD ---
st.markdown('<div class="main-header">🔥 Heat Exchanger Design Suite</div>', unsafe_allow_html=True)
st.markdown("---")

col_main_1, col_main_2, col_main_3 = st.columns([1, 1, 0.8])

with col_main_1:
    st.subheader("🔴 Hot Stream")
    h_fluid = st.selectbox("Fluid", get_available_fluids(), key="hf")
    h_flow = st.number_input("Mass Flow (kg/s)", value=5.0, min_value=0.1, key="hf_m")
    h_tin = st.number_input("Inlet Temp (°C)", value=95.0, key="hf_ti")
    if calc_mode.startswith("Design"):
        h_tout = st.number_input("Target Outlet (°C)", value=60.0, key="hf_to")
    else:
        h_tout = None

with col_main_2:
    st.subheader("🔵 Cold Stream")
    c_fluid = st.selectbox("Fluid", get_available_fluids(), key="cf")
    c_flow = st.number_input("Mass Flow (kg/s)", value=8.0, min_value=0.1, key="cf_m")
    c_tin = st.number_input("Inlet Temp (°C)", value=25.0, key="cf_ti")
    if calc_mode.startswith("Design"):
        c_tout = st.number_input("Target Outlet (°C)", value=40.0, key="cf_to")
    else:
        c_tout = None

with col_main_3:
    st.subheader("🧮 Specs")
    base_u = EngineeringDB.HX_CONFIGS[hx_config]['base_u']
    u_val = st.number_input("U-Value (W/m²K)", value=float(base_u))
    
    if calc_mode.startswith("Rating"):
        area_val = st.number_input("Area (m²)", value=50.0)
    else:
        area_val = None
        
    st.markdown("##")
    if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
        try:
            # 1. THERMAL
            hx = HeatExchanger(flow_arrangement=flow_arr)
            if calc_mode.startswith("Design"):
                valid, msg = validate_temperatures(h_tin, h_tout, c_tin, c_tout, flow_arr)
                if not valid:
                    st.error(msg)
                    st.stop()
                res = hx.calculate_lmtd(h_tin, h_tout, c_tin, c_tout, h_flow, c_flow, h_fluid, c_fluid, u_val)
            else:
                res = hx.calculate_ntu(h_tin, c_tin, h_flow, c_flow, h_fluid, c_fluid, u_val, area_val)
            
            # 2. HYDRAULICS (Tube Side)
            pd = PressureDropCalculator(hx_config)
            tube_data = pd.estimate_geometry_from_area(res.get('area', 10), hx_config)
            res['hydraulics'] = pd.calculate_tube_side_pressure_drop(
                h_flow, 990, 0.0008, 0.019, 6.0, tube_data['n_tubes'], 2
            )
            
            # 3. FINANCIALS
            ce = CostEstimator()
            res['financials'] = ce.estimate_project_budget(res.get('area', 10), hx_config, material)
            res['meta'] = {'material': material, 'fouling': fouling_factor, 'config': hx_config}
            
            st.session_state.results = res
            st.success("Simulation Complete")
            
        except Exception as e:
            st.error(f"Simulation Error: {str(e)}")

# --- RESULTS DASHBOARD ---
if st.session_state.results:
    res = st.session_state.results
    
    st.divider()
    # KPI METRICS
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Thermal Duty", f"{res['Q']:.1f} kW")
    k2.metric("Surface Area", f"{res['area']:.1f} m²")
    k3.metric("LMTD", f"{res['LMTD']:.1f} °C")
    k4.metric("Est. Cost", f"${res['financials']['total_capex']:,.0f}")

    # TABS
    t1, t2, t3 = st.tabs(["📈 Thermal Profile", "⚙️ Mechanical & Hydraulics", "💰 Cost & Report"])
    
    # TAB 1: THERMAL GRAPH
    with t1:
        x, th, tc = generate_temperature_profile(res['T_hot_in'], res['T_hot_out'], res['T_cold_in'], res['T_cold_out'], flow_arr)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x*100, y=th, name='Hot Stream', line=dict(color='#FF4B4B', width=3)))
        fig.add_trace(go.Scatter(x=x*100, y=tc, name='Cold Stream', line=dict(color='#0068C9', width=3)))
        fig.update_layout(title="Temperature Profile (T-Q Diagram)", xaxis_title="Length %", yaxis_title="Temp °C", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: MECHANICAL LAYOUT (NEW FEATURE)
    with t2:
        col_mech_1, col_mech_2 = st.columns([1, 1])
        
        with col_mech_1:
            st.markdown("#### 📐 Tube Bundle Layout (TEMA)")
            # Calculate Geometry for Plotter
            tube_od = 0.01905 # 3/4 inch standard
            # Estimate Number of Tubes based on Area
            calc_area = res.get('area', 10)
            if calc_area < 1: calc_area = 1
            # Approx 6m tube length
            est_n_tubes = int(calc_area / (math.pi * tube_od * 6.0)) 
            if est_n_tubes < 5: est_n_tubes = 5 # Minimum to show plot
            
            # Estimate Shell Diameter
            est_shell_id = math.sqrt(est_n_tubes) * tube_od * 1.5 
            
            # Draw Plot
            img_buf = plot_tube_layout(est_n_tubes, est_shell_id, tube_od)
            st.image(img_buf, caption=f"Generated Cross-Section ({est_n_tubes} Tubes)", use_column_width=True)

        with col_mech_2:
            st.markdown("#### 🌊 Hydraulic Data")
            hyd = res['hydraulics']
            st.write(f"**Tube Velocity:** {hyd['velocity_m_s']:.2f} m/s")
            st.write(f"**Reynolds No:** {hyd['reynolds']:.0f}")
            
            # Flow Regime Badge
            if hyd['reynolds'] > 4000:
                st.success(f"Regime: {hyd['regime']} (Efficient)")
            elif hyd['reynolds'] < 2300:
                st.warning(f"Regime: {hyd['regime']} (Poor Heat Transfer)")
            else:
                st.info(f"Regime: {hyd['regime']}")
                
            st.metric("Pressure Drop", f"{hyd['pressure_drop_kPa']:.2f} kPa")
            
            # Alerts
            if hyd.get('alerts'):
                st.markdown("---")
                for alert in hyd['alerts']:
                    st.error(f"⚠️ {alert}")

    # TAB 3: COST & REPORT (NEW EXCEL BUTTON)
    with t3:
        fin = res['financials']
        st.markdown("#### 💵 Class 4 Cost Estimate")
        
        cost_cols = st.columns(3)
        cost_cols[0].metric("Equipment (FOB)", f"${fin['equipment_fob']:,.0f}")
        cost_cols[1].metric("Installation", f"${fin['installation']:,.0f}")
        cost_cols[2].metric("Total CAPEX", f"${fin['total_capex']:,.0f}", delta_color="inverse")
        
        st.divider()
        st.markdown("#### 📄 Project Documentation")
        pname = st.text_input("Project Reference ID", "HX-2024-001")
        
        c_txt, c_xls = st.columns(2)
        
        with c_txt:
            if st.button("📄 Download Spec Sheet (.txt)"):
                rep = generate_text_report(res, res.get('hydraulics'), res.get('financials'), res['meta'], {'project_name': pname})
                st.download_button("Click to Download Text Report", rep, f"{pname}_Spec.txt")
        
        with c_xls:
            if st.button("📊 Download Datasheet (.xlsx)"):
                excel_file = generate_excel_datasheet(res, {'project_name': pname})
                st.download_button(
                    label="Click to Download Excel",
                    data=excel_file,
                    file_name=f"{pname}_Datasheet.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
