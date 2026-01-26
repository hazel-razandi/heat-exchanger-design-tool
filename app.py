"""
Heat Exchanger Design Tool
Developed by KAKAROTONCLOUD
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Import Custom Modules
from src.calculations import HeatExchanger
from src.fluid_properties import get_available_fluids
from src.hx_types import HeatExchangerType
from src.utils import validate_temperatures, generate_temperature_profile
from src.pressure_drop import PressureDropCalculator
from src.cost_estimator import CostEstimator
from src.pdf_generator import generate_text_report
from src.design_storage import DesignStorage

# Page Config
st.set_page_config(page_title="HX Design by KAKAROTONCLOUD", page_icon="🔥", layout="wide")

# State Init
if 'results' not in st.session_state: st.session_state.results = None
if 'saved' not in st.session_state: st.session_state.saved = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ KAKAROTONCLOUD HX")
    st.caption("Professional Design Tool v2.0")
    
    st.markdown("---")
    method = st.radio("Method", ["LMTD (Design)", "NTU (Rating)"])
    flow_type = st.selectbox("Arrangement", ["Counter Flow", "Parallel Flow"])
    hx_type = st.selectbox("HX Type", HeatExchangerType.list_all_types())
    
    st.markdown("---")
    # Default to False for now to prevent confusion if files aren't synced
    st.checkbox("Calculate Pressure Drop", key="calc_dp", value=True)
    st.checkbox("Estimate Costs", key="calc_cost", value=True)

# --- MAIN PAGE ---
st.title("🔥 Heat Exchanger Design Tool")
st.markdown("Build reliable thermal designs instantly.")

tab1, tab2, tab3 = st.tabs(["📝 Input & Calculate", "📊 Analysis & Graphs", "💾 Report & Save"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Hot Side")
        hot_fluid = st.selectbox("Fluid", get_available_fluids(), key="hf")
        mh = st.number_input("Mass Flow (kg/s)", value=2.0, key="mh")
        Thi = st.number_input("Inlet Temp (°C)", value=90.0, key="thi")
        
        if method == "LMTD (Design)":
            Tho = st.number_input("Outlet Temp (°C)", value=50.0, key="tho")
        else:
            Tho = None # Calculated later

    with col2:
        st.subheader("🔵 Cold Side")
        cold_fluid = st.selectbox("Fluid", get_available_fluids(), key="cf")
        mc = st.number_input("Mass Flow (kg/s)", value=3.0, key="mc")
        Tci = st.number_input("Inlet Temp (°C)", value=25.0, key="tci")
        
        if method == "LMTD (Design)":
            Tco = st.number_input("Outlet Temp (°C)", value=45.0, key="tco")
        else:
            Tco = None

    st.markdown("---")
    col_u, col_a = st.columns(2)
    with col_u:
        U = st.number_input("U-Value (W/m²K)", value=800.0, help="Overall Heat Transfer Coefficient")
    with col_a:
        if method == "NTU (Rating)":
            Area = st.number_input("Surface Area (m²)", value=10.0)
        else:
            Area = None

    if st.button("🚀 Run Calculation", type="primary", use_container_width=True):
        try:
            # 1. Initialize Engine
            hx = HeatExchanger(flow_arrangement=flow_type)
            
            # 2. Run Core Math
            if method == "LMTD (Design)":
                # Validate Input Physics
                valid, msg = validate_temperatures(Thi, Tho, Tci, Tco, flow_type)
                if not valid:
                    st.error(f"❌ Physical Error: {msg}")
                    st.stop()
                    
                res = hx.calculate_lmtd(Thi, Tho, Tci, Tco, mh, mc, hot_fluid, cold_fluid, U)
            else:
                res = hx.calculate_ntu(Thi, Tci, mh, mc, hot_fluid, cold_fluid, U, Area)

            # 3. Optional Modules
            if st.session_state.calc_dp:
                pd = PressureDropCalculator(hx_type)
                geo = pd.estimate_geometry_from_area(res['area'], hx_type)
                
                # FIXED: Added '2' (passes) as the last argument to prevent "missing argument" error
                res['dp_hot'] = pd.calculate_tube_side_pressure_drop(mh, 997, 0.001, 0.025, 4, 10, 2)
                res['pump_hot'] = pd.calculate_pumping_power(mh, res['dp_hot']['pressure_drop_kPa']*1000, 997)

            if st.session_state.calc_cost:
                ce = CostEstimator()
                res['costs'] = ce.estimate_equipment_cost(res['area'], hx_type, "SS304", "Low")

            st.session_state.results = res
            st.success("✅ Calculation Successful!")
            
        except Exception as e:
            st.error(f"❌ System Error: {str(e)}")

with tab2:
    if st.session_state.results:
        r = st.session_state.results
        
        # Metrics
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Heat Load", f"{r['Q']:.2f} kW")
        k2.metric("Area", f"{r['area']:.2f} m²")
        k3.metric("Effectiveness", f"{r['effectiveness']*100:.1f}%")
        k4.metric("LMTD", f"{r['LMTD']:.2f} °C")
        
        # Graph
        st.subheader("Temperature Profile")
        x, th, tc = generate_temperature_profile(r['T_hot_in'], r['T_hot_out'], r['T_cold_in'], r['T_cold_out'], r['flow_type'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x*100, y=th, name='Hot Fluid', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x*100, y=tc, name='Cold Fluid', line=dict(color='blue')))
        fig.update_layout(xaxis_title="% Length", yaxis_title="Temperature (C)")
        st.plotly_chart(fig, use_container_width=True)
        
        if 'costs' in r:
            st.info(f"💰 Estimated Cost: ${r['costs']['total_project_cost']:,.2f}")

    else:
        st.info("Run calculation to view results.")

with tab3:
    if st.session_state.results:
        pname = st.text_input("Project Name", "New Design")
        
        if st.button("Generate Report"):
            rep = generate_text_report(st.session_state.results, None, st.session_state.results.get('costs'), {'project_name': pname})
            st.text_area("Report", rep, height=300)
            st.download_button("Download .txt", rep, "report.txt")
            
        if st.button("Save Design"):
            ds = DesignStorage()
            st.session_state.saved.append(ds.create_design_snapshot(st.session_state.results, pname))
            st.success("Saved!")
