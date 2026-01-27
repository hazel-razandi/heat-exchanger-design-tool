import streamlit as st
import pandas as pd
import plotly.express as px

from src.core.segmental_solver import SegmentalSolver
from src.core.optimizer import DesignOptimizer
from src.core.properties import get_available_fluids
from src.data.materials import MaterialDB
# CHANGED IMPORT:
from src.safety_checks.vibration import VibrationCheck
from src.safety_checks.api_660 import API660Validator

from src.platform.auth import render_login
from src.platform.project_db import save_project, load_project, get_project_list
from src.business.tema_exporter import generate_tema_sheet
from src.business.quote_generator import create_pdf_quote

st.set_page_config(page_title="ExchangerAI Enterprise", layout="wide", page_icon="🏭")

# Custom CSS
st.markdown("""<style>.main-header {font-size: 2.5rem; color: #0F172A; font-weight: 700;}.metric-card {background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 10px; text-align: center;}.success-box {padding:15px; background-color:#DCFCE7; color:#166534; border-radius:8px; border: 1px solid #86EFAC;}.warning-box {padding:15px; background-color:#FEF9C3; color:#854D0E; border-radius:8px; border: 1px solid #FDE047;}.error-box {padding:15px; background-color:#FEE2E2; color:#991B1B; border-radius:8px; border: 1px solid #FCA5A5;}div[data-testid="stMetricValue"] {font-size: 24px; font-weight: bold; color: #0F172A;}</style>""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = None

def main_app():
    with st.sidebar:
        st.markdown(f"### 👤 Engineer: {st.session_state['user']}")
        menu = st.radio("Navigation", ["📂 Project Hub", "🛠️ Design Workspace", "🚪 Logout"])
        st.markdown("---")
        st.info("Version 6.0 Enterprise\n\n© 2026 ExchangerAI")
    if menu == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()
    elif menu == "📂 Project Hub":
        render_projects()
    elif menu == "🛠️ Design Workspace":
        render_designer()

def render_projects():
    st.markdown('<p class="main-header">📂 Project Hub</p>', unsafe_allow_html=True)
    projects = get_project_list()
    if not projects:
        st.info("No saved projects found.")
        return
    for p in projects:
        with st.container():
            c1, c2 = st.columns([5, 1])
            c1.subheader(f"📄 {p}")
            if c2.button("Load", key=p):
                st.session_state['loaded_project'] = load_project(p)
                st.success(f"Loaded '{p}'")

def render_designer():
    st.markdown('<p class="main-header">🛠️ Thermal & Mechanical Workspace</p>', unsafe_allow_html=True)
    c_proj, c_save = st.columns([3, 1])
    proj_name = c_proj.text_input("Project Reference Name", value="Design-001")
    defaults = st.session_state.get('loaded_project', {}).get('inputs', {})
    
    with st.form("design_form"):
        st.markdown("### 1. Geometry & Construction")
        c1, c2, c3, c4 = st.columns(4)
        shell_id = c1.number_input("Shell Diameter (m)", 0.2, 5.0, defaults.get('shell_id', 0.6))
        length = c2.number_input("Tube Length (m)", 1.0, 10.0, defaults.get('length', 3.0))
        n_tubes = c3.number_input("Tube Count", 10, 5000, defaults.get('n_tubes', 150))
        baffle_spacing = c4.number_input("Baffle Spacing (m)", 0.1, 2.0, defaults.get('baffle_spacing', 0.3))
        st.markdown("### 2. Process Conditions")
        c5, c6 = st.columns(2)
        with c5:
            st.markdown("**Hot Side (Tube)**")
            h_f = st.selectbox("Fluid", get_available_fluids(), key='h')
            h_m = st.number_input("Mass Flow (kg/s)", 0.1, 500.0, defaults.get('m_hot', 12.0))
            h_t = st.number_input("Inlet Temp (°C)", 0.0, 500.0, defaults.get('T_hot_in', 90.0))
        with c6:
            st.markdown("**Cold Side (Shell)**")
            c_f = st.selectbox("Fluid", get_available_fluids(), key='c', index=1)
            c_m = st.number_input("Mass Flow (kg/s)", 0.1, 500.0, defaults.get('m_cold', 15.0))
            c_t = st.number_input("Inlet Temp (°C)", 0.0, 500.0, defaults.get('T_cold_in', 25.0))
        st.markdown("---")
        c_btn1, c_btn2 = st.columns([1, 1])
        with c_btn1: submitted = st.form_submit_button("🚀 Run Analysis", type="primary")
        with c_btn2: optimize_btn = st.form_submit_button("✨ AI Auto-Optimize")

    if c_save.button("💾 Save Project"): st.toast("Project Saved!")
    if optimize_btn:
        st.info("🤖 AI is iterating...")
        base_inputs = {'length': length, 'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_cut': 25, 'n_passes': 2, 'fouling': 0.0002, 'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_t, 'T_cold_in': c_t, 'hot_fluid': h_f, 'cold_fluid': c_f}
        optimizer = DesignOptimizer()
        best = optimizer.run_optimization(base_inputs)
        if not best.empty:
            st.success("✅ Top Safe Designs:")
            st.dataframe(best, use_container_width=True, hide_index=True)
        else: st.warning("⚠️ No safe designs found.")

    if submitted:
        inputs = {'shell_id': shell_id, 'length': length, 'n_tubes': n_tubes, 'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing, 'baffle_cut': 25, 'n_passes': 2, 'fouling': 0.0002, 'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_t, 'T_cold_in': c_t, 'hot_fluid': h_f, 'cold_fluid': c_f}
        try:
            solver = SegmentalSolver(n_zones=10)
            res = solver.run(inputs)
            vib = VibrationCheck(inputs, res).run_check()
            hyd = API660Validator(inputs, res).check_rho_v2()
            st.divider()
            t1, t2, t3, t4 = st.tabs(["📊 Performance", "📈 Zone Analysis", "🛡️ Mechanical Audit", "📥 Exports"])
            with t1:
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Duty", f"{res['Q']/1000:.1f} kW"); k2.metric("U-Value", f"{res['U']:.1f}"); k3.metric("Area", f"{res['Area']:.1f} m²"); k4.metric("Outlet T", f"{res['T_hot_out']:.1f} °C")
            with t2:
                st.subheader("Temperature Profile"); st.line_chart(res['zone_df'][['T_Hot (°C)', 'T_Cold (°C)']]); st.dataframe(res['zone_df'], use_container_width=True)
            with t3:
                c1, c2 = st.columns(2)
                with c1: 
                    st.markdown("#### 〰️ Vibration"); 
                    if vib['status']=="PASS": st.markdown('<div class="success-box">✅ PASS</div>', unsafe_allow_html=True)
                    else: st.markdown(f'<div class="error-box">❌ {vib["msg"]}</div>', unsafe_allow_html=True)
                    st.json(vib['data'])
                with c2: 
                    st.markdown("#### 🌊 API 660"); 
                    if hyd['status']=="PASS": st.markdown('<div class="success-box">✅ PASS</div>', unsafe_allow_html=True)
                    else: st.markdown(f'<div class="warning-box">{hyd["msg"]}</div>', unsafe_allow_html=True)
                    st.json(hyd['data'])
            with t4:
                c1, c2 = st.columns(2)
                c1.download_button("📥 TEMA Sheet", generate_tema_sheet(proj_name, inputs, res), f"{proj_name}.xlsx")
                c2.download_button("📄 PDF Quote", create_pdf_quote(proj_name, inputs, res, 15000), f"{proj_name}.pdf")
        except Exception as e: st.error(f"Error: {str(e)}")

if st.session_state['logged_in']: main_app()
else: render_login()
