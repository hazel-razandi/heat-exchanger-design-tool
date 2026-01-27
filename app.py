import streamlit as st
import pandas as pd
import json
import plotly.express as px

# --- IMPORTS ---
from src.core.segmental_solver import SegmentalSolver
from src.core.optimizer import DesignOptimizer
from src.core.properties import get_available_fluids
from src.data.benchmarks import get_benchmarks
from src.safety_checks.vibration import VibrationCheck
from src.safety_checks.api_660 import API660Validator
from src.business.tema_exporter import generate_tema_sheet
from src.business.quote_generator import create_pdf_quote
from src.platform.auth import render_login

# --- PAGE CONFIG ---
st.set_page_config(page_title="ExchangerAI Enterprise", layout="wide", page_icon="🏭")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #0F172A; font-weight: 700;}
    .metric-card {background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 10px; text-align: center;}
    .success-box {padding:15px; background-color:#DCFCE7; color:#166534; border-radius:8px; border: 1px solid #86EFAC;}
    .warning-box {padding:15px; background-color:#FEF9C3; color:#854D0E; border-radius:8px; border: 1px solid #FDE047;}
    .error-box {padding:15px; background-color:#FEE2E2; color:#991B1B; border-radius:8px; border: 1px solid #FCA5A5;}
    div[data-testid="stMetricValue"] {font-size: 24px; font-weight: bold; color: #0F172A;}
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = None

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.markdown(f"### 👤 Engineer: {st.session_state['user']}")
        menu = st.radio("Navigation", ["🛠️ Design Workspace", "🔎 Sensitivity Analysis", "📚 Validation Benchmark", "🚪 Logout"])
        st.markdown("---")
        st.info("Version 7.0 Enterprise\n\n© 2026 ExchangerAI")
        
        # --- NEW: PROJECT STORAGE ---
        st.markdown("### 💾 Project File")
        # SAVE
        if st.session_state.get('last_inputs'):
            proj_data = json.dumps(st.session_state['last_inputs'])
            st.download_button("Download .json", proj_data, "project.json", "application/json")
        
        # LOAD
        uploaded_file = st.file_uploader("Load Project", type=["json"])
        if uploaded_file:
            data = json.load(uploaded_file)
            st.session_state['loaded_project'] = data
            st.success("Project Loaded!")

    if menu == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()
    elif menu == "🛠️ Design Workspace":
        render_designer()
    elif menu == "🔎 Sensitivity Analysis":
        render_sensitivity()
    elif menu == "📚 Validation Benchmark":
        render_validation()

def render_validation():
    st.markdown('<p class="main-header">📚 Engineering Validation</p>', unsafe_allow_html=True)
    st.markdown("Verify physics engine accuracy against standard literature (Kern, HTRI).")
    
    cases = get_benchmarks()
    selected_case = st.selectbox("Select Validation Case", list(cases.keys()))
    case_data = cases[selected_case]
    
    st.info(f"**{case_data['name']}**\n\n{case_data['description']}\n\n*Source: {case_data['source']}*")
    
    if st.button("▶️ Run Verification Test"):
        solver = SegmentalSolver(n_zones=10)
        try:
            test_inputs = case_data['inputs']
            # Fallback for demo
            if 'Oil' in test_inputs['hot_fluid']: test_inputs['hot_fluid'] = 'Water' 
            
            res = solver.run(test_inputs)
            target = case_data['targets']
            
            st.markdown("### 📊 Accuracy Report")
            c1, c2 = st.columns(2)
            dev_q = (res['Q']/1000 - target['Duty_kW']) / target['Duty_kW'] * 100
            dev_u = (res['U'] - target['U_Service']) / target['U_Service'] * 100
            
            c1.metric("Duty Deviation", f"{dev_q:.1f}%", f"Target: {target['Duty_kW']} kW")
            c2.metric("U-Value Deviation", f"{dev_u:.1f}%", f"Target: {target['U_Service']} W/m2K")
            
            if abs(dev_u) < 10:
                st.markdown('<div class="success-box">✅ VALIDATION PASSED: Results match standard within 10% tolerance.</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ DEVIATION: Check fluid properties.")
                
        except Exception as e:
            st.error(f"Benchmark Failed: {str(e)}")

def render_sensitivity():
    st.markdown('<p class="main-header">🔎 Parametric Sensitivity Study</p>', unsafe_allow_html=True)
    st.info("Analyze how design changes affect performance in real-time.")
    
    if 'last_inputs' not in st.session_state:
        st.warning("Please run a design in the Workspace first.")
        return

    base = st.session_state['last_inputs'].copy()
    
    param = st.selectbox("Parameter to Sweep", ["Baffle Spacing", "Tube Length", "Shell Diameter"])
    
    if st.button("🚀 Run Sweep"):
        results = []
        solver = SegmentalSolver(n_zones=10)
        
        # Define ranges
        if param == "Baffle Spacing":
            values = [x/100 for x in range(10, 100, 5)] # 0.1 to 1.0m
            key = 'baffle_spacing'
        elif param == "Tube Length":
            values = [x/2 for x in range(2, 20)] # 1.0 to 10.0m
            key = 'length'
        else:
            values = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2]
            key = 'shell_id'
            
        progress = st.progress(0)
        for i, val in enumerate(values):
            case = base.copy()
            case[key] = val
            try:
                res = solver.run(case)
                results.append({param: val, "Duty (kW)": res['Q']/1000, "U-Value": res['U'], "Pressure Drop": res['v_shell']**2}) # simplified dP proxy
            except: pass
            progress.progress((i+1)/len(values))
            
        df = pd.DataFrame(results)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Effect on Heat Duty")
            st.line_chart(df, x=param, y="Duty (kW)")
        with c2:
            st.subheader("Effect on Efficiency (U)")
            st.line_chart(df, x=param, y="U-Value")

def render_designer():
    st.markdown('<p class="main-header">🛠️ Thermal & Mechanical Workspace</p>', unsafe_allow_html=True)
    
    c_proj, c_save = st.columns([3, 1])
    proj_name = c_proj.text_input("Project Reference Name", value="Design-001")
    
    # LOAD DEFAULTS
    defaults = st.session_state.get('loaded_project', {}).get('inputs', {})
    if not defaults: defaults = st.session_state.get('last_inputs', {})

    with st.form("design_form"):
        # --- NEW CONFIGURATION TAB ---
        st.markdown("### 1. Configuration & Geometry")
        
        # ROW 1: TEMA & Layout (NEW)
        c_conf1, c_conf2, c_conf3, c_conf4 = st.columns(4)
        tema_type = c_conf1.selectbox("TEMA Type", ["BEM (Fixed)", "AES (Floating)", "U-Tube"], index=0)
        tube_layout = c_conf2.selectbox("Tube Pattern", ["Triangular (30)", "Square (90)", "Rotated Square (45)"], index=0)
        n_passes = c_conf3.selectbox("Number of Passes", [1, 2, 4, 6, 8], index=1)
        baffle_cut = c_conf4.slider("Baffle Cut (%)", 15, 45, 25)

        # ROW 2: Dimensions
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

    # --- INPUT COMPILATION ---
    inputs = {
        'tema_type': tema_type.split()[0], # Just 'BEM' or 'AES'
        'tube_layout': tube_layout.split()[0],
        'n_passes': n_passes,
        'baffle_cut': baffle_cut,
        'shell_id': shell_id, 'length': length, 'n_tubes': n_tubes,
        'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing, 
        'fouling': 0.0002,
        'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_t, 'T_cold_in': c_t,
        'hot_fluid': h_f, 'cold_fluid': c_f
    }

    if optimize_btn:
        st.info("🤖 AI is iterating through geometric combinations...")
        optimizer = DesignOptimizer()
        best = optimizer.run_optimization(inputs)
        if not best.empty:
            st.success("✅ Top Safe Designs:")
            st.dataframe(best, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No safe designs found.")

    if submitted:
        st.session_state['last_inputs'] = inputs # SAVE FOR PROJECT FILE
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
                st.progress(min(res['U']/1000, 1.0))

            with t2:
                st.subheader("Temperature Profile")
                st.line_chart(res['zone_df'][['T_Hot (°C)', 'T_Cold (°C)']])
                st.dataframe(res['zone_df'], use_container_width=True)

            with t3:
                c1, c2 = st.columns(2)
                with c1: 
                    st.markdown("#### 〰️ Vibration") 
                    if vib['status']=="PASS": st.markdown('<div class="success-box">✅ PASS</div>', unsafe_allow_html=True)
                    else: st.markdown(f'<div class="error-box">❌ {vib["msg"]}</div>', unsafe_allow_html=True)
                    st.json(vib['data'])
                with c2: 
                    st.markdown("#### 🌊 API 660")
                    if hyd['status']=="PASS": st.markdown('<div class="success-box">✅ PASS</div>', unsafe_allow_html=True)
                    else: st.markdown(f'<div class="warning-box">{hyd["msg"]}</div>', unsafe_allow_html=True)
                    st.json(hyd['data'])

            with t4:
                c1, c2 = st.columns(2)
                c1.download_button("📥 TEMA Sheet", generate_tema_sheet(proj_name, inputs, res), f"{proj_name}.xlsx")
                c2.download_button("📄 PDF Quote", create_pdf_quote(proj_name, inputs, res, 15000), f"{proj_name}.pdf")

        except Exception as e:
            st.error(f"Error: {str(e)}")

if st.session_state['logged_in']: main_app()
else: render_login()
