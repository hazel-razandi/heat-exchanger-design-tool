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
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'results' not in st.session_state: st.session_state.results = None

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🏭 ExchangerPro")
    st.caption("v3.0.0 Enterprise | KAKAROTONCLOUD")
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
st.title("Heat Exchanger Design Suite")
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
            # Standard 3/4" tube, 2 passes
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

# --- RESULTS ---
if st.session_state.results:
    res = st.session_state.results
    
    st.divider()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Thermal Duty", f"{res['Q']:.1f} kW")
    k2.metric("Surface Area", f"{res['area']:.1f} m²")
    k3.metric("LMTD", f"{res['LMTD']:.1f} °C")
    k4.metric("Est. Cost", f"${res['financials']['total_capex']:,.0f}")

    t1, t2, t3 = st.tabs(["📈 Performance", "⚙️ Mechanical", "📄 Report"])
    
    with t1:
        x, th, tc = generate_temperature_profile(res['T_hot_in'], res['T_hot_out'], res['T_cold_in'], res['T_cold_out'], flow_arr)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x*100, y=th, name='Hot Stream', line=dict(color='#FF4B4B')))
        fig.add_trace(go.Scatter(x=x*100, y=tc, name='Cold Stream', line=dict(color='#0068C9')))
        fig.update_layout(title="Temperature Profile", xaxis_title="Length %", yaxis_title="Temp °C", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        hyd = res['hydraulics']
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Hydraulics**")
            st.write(f"Velocity: {hyd['velocity_m_s']:.2f} m/s")
            st.write(f"Pressure Drop: {hyd['pressure_drop_kPa']:.2f} kPa")
            if hyd['alerts']:
                for a in hyd['alerts']: st.warning(a)
        with c2:
            st.markdown("**Cost Breakdown**")
            fin = res['financials']
            st.write(f"Equipment: ${fin['equipment_fob']:,.2f}")
            st.write(f"Installation: ${fin['installation']:,.2f}")
            st.write(f"Indirects: ${fin['indirects']:,.2f}")

    with t3:
        pname = st.text_input("Project Reference", "HX-Project-001")
        if st.button("Generate Spec Sheet"):
            rep = generate_text_report(res, res.get('hydraulics'), res.get('financials'), res['meta'], {'project_name': pname})
            st.download_button("Download Spec (.txt)", rep, f"{pname}.txt")
