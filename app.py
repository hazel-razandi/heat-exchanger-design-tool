import streamlit as st
from src.core.solver import SegmentalSolver
from src.core.properties import get_available_fluids
from src.data.materials import MaterialDB
from src.mechanical.vibration import VibrationCheck
from src.mechanical.api_660 import API660Validator
from src.platform.auth import render_login
from src.platform.project_db import save_project, load_project, get_project_list

# --- APP CONFIG ---
st.set_page_config(page_title="ExchangerAI Enterprise", layout="wide", page_icon="🏭")
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = None

# --- MAIN APP LOGIC ---
def main_app():
    # Sidebar Navigation
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        menu = st.radio("Menu", ["📂 Projects", "🛠️ New Design", "🚪 Logout"])
        st.markdown("---")
        st.caption("ExchangerAI v6.0 Enterprise")

    if menu == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()

    elif menu == "📂 Projects":
        st.title("📂 Project Hub")
        projects = get_project_list()
        if not projects:
            st.info("No projects found. Go to 'New Design' to start.")
        
        for p in projects:
            c1, c2 = st.columns([4,1])
            c1.subheader(f"📄 {p}")
            if c2.button("Load", key=p):
                st.session_state['loaded_project'] = load_project(p)
                st.success(f"Loaded {p}. Switch to 'New Design' to view.")

    elif menu == "🛠️ New Design":
        render_designer()

def render_designer():
    st.title("🛠️ Thermal & Mechanical Designer")
    
    # Project Toolbar
    c_proj, c_save = st.columns([3,1])
    proj_name = c_proj.text_input("Project Name", value="Design_001")
    
    # Load defaults if project loaded
    defaults = st.session_state.get('loaded_project', {}).get('inputs', {})
    
    # --- INPUTS ---
    with st.expander("1. Geometry Configuration", expanded=True):
        c1, c2, c3 = st.columns(3)
        shell_id = c1.number_input("Shell Diameter (m)", 0.2, 5.0, defaults.get('shell_id', 0.6))
        length = c2.number_input("Tube Length (m)", 1.0, 10.0, defaults.get('length', 3.0))
        n_tubes = c3.number_input("Tube Count", 10, 5000, defaults.get('n_tubes', 150))
        
        c4, c5 = st.columns(2)
        baffle_spacing = c4.number_input("Baffle Spacing (m)", 0.1, 2.0, defaults.get('baffle_spacing', 0.3))
        material = c5.selectbox("Material", MaterialDB.get_names())

    with st.expander("2. Process Conditions", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Hot Side")
            h_f = st.selectbox("Fluid", get_available_fluids(), key='h')
            h_m = st.number_input("Flow (kg/s)", 0.1, 500.0, defaults.get('m_hot', 12.0))
            h_ti = st.number_input("Inlet Temp (C)", 0.0, 500.0, defaults.get('T_hot_in', 90.0))
        with c2:
            st.markdown("#### Cold Side")
            c_f = st.selectbox("Fluid", get_available_fluids(), key='c', index=1)
            c_m = st.number_input("Flow (kg/s)", 0.1, 500.0, defaults.get('m_cold', 15.0))
            c_ti = st.number_input("Inlet Temp (C)", 0.0, 500.0, defaults.get('T_cold_in', 25.0))

    if st.button("🚀 Run Simulation", type="primary"):
        inputs = {
            'shell_id': shell_id, 'length': length, 'n_tubes': n_tubes,
            'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing, 'baffle_cut': 25,
            'n_passes': 2, 'fouling': 0.0002,
            'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_ti, 'T_cold_in': c_ti,
            'hot_fluid': h_f, 'cold_fluid': c_f
        }
        
        # SAVE FUNCTION
        if c_save.button("💾 Save Project"):
            save_project(proj_name, {'inputs': inputs, 'status': 'draft'})
            st.toast("Project Saved!")

        # RUN ENGINES
        solver = SegmentalSolver()
        try:
            res = solver.run(inputs)
            vib = VibrationCheck(inputs, res).run_check()
            hyd = API660Validator(inputs, res).check_rho_v2()
            
            # --- RESULTS ---
            st.divider()
            k1, k2, k3 = st.columns(3)
            k1.metric("Heat Duty", f"{res['Q']/1000:.1f} kW")
            k2.metric("Overall U", f"{res['U']:.1f} W/m²K")
            k3.metric("Area", f"{res['Area']:.1f} m²")
            
            # WARNINGS
            st.subheader("🛡️ Safety Shield")
            if vib['status'] != "PASS":
                st.error(f"VIBRATION: {vib['msg']}")
            else:
                st.success("✅ Vibration Check Passed")
                
            if hyd['status'] != "PASS":
                for w in hyd['items']: st.warning(w)
            else:
                st.success("✅ Hydraulic Check Passed")
                
        except Exception as e:
            st.error(f"Solver Error: {str(e)}")

# --- ROUTER ---
if st.session_state['logged_in']:
    main_app()
else:
    render_login()
