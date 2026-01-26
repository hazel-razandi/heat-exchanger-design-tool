import streamlit as st
from src.core.solver import SegmentalSolver
from src.core.properties import get_available_fluids
from src.data.materials import MaterialDB
from src.mechanical.vibration import VibrationCheck
from src.mechanical.api_660 import API660Validator
from src.platform.auth import render_login
from src.platform.project_db import save_project, load_project, get_project_list
# NEW IMPORTS
from src.business.tema_exporter import generate_tema_sheet
from src.business.quote_generator import create_pdf_quote

st.set_page_config(page_title="ExchangerAI Enterprise", layout="wide", page_icon="🏭")
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user' not in st.session_state: st.session_state['user'] = None

def main_app():
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        menu = st.radio("Menu", ["📂 Projects", "🛠️ New Design", "🚪 Logout"])
        st.markdown("---")
    
    if menu == "🚪 Logout":
        st.session_state['logged_in'] = False
        st.rerun()
    elif menu == "📂 Projects":
        render_projects()
    elif menu == "🛠️ New Design":
        render_designer()

def render_projects():
    st.title("📂 Project Hub")
    projects = get_project_list()
    if not projects: st.info("No projects found.")
    for p in projects:
        c1, c2 = st.columns([4,1])
        c1.subheader(f"📄 {p}")
        if c2.button("Load", key=p):
            st.session_state['loaded_project'] = load_project(p)
            st.success(f"Loaded {p}")

def render_designer():
    st.title("🛠️ Thermal & Mechanical Designer")
    
    c_proj, c_save = st.columns([3,1])
    proj_name = c_proj.text_input("Project Name", value="Design_001")
    defaults = st.session_state.get('loaded_project', {}).get('inputs', {})
    
    with st.expander("Geometry", expanded=True):
        c1, c2, c3 = st.columns(3)
        shell_id = c1.number_input("Shell Dia (m)", 0.2, 5.0, defaults.get('shell_id', 0.6))
        length = c2.number_input("Length (m)", 1.0, 10.0, defaults.get('length', 3.0))
        n_tubes = c3.number_input("Tubes", 10, 5000, defaults.get('n_tubes', 150))
        baffle_spacing = st.number_input("Baffle Space (m)", 0.1, 2.0, defaults.get('baffle_spacing', 0.3))

    with st.expander("Process", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            h_f = st.selectbox("Hot Fluid", get_available_fluids())
            h_m = st.number_input("Hot Flow", 0.1, 500.0, 12.0)
            h_t = st.number_input("Hot In", 0.0, 500.0, 90.0)
        with c2:
            c_f = st.selectbox("Cold Fluid", get_available_fluids(), index=1)
            c_m = st.number_input("Cold Flow", 0.1, 500.0, 15.0)
            c_t = st.number_input("Cold In", 0.0, 500.0, 25.0)

    if st.button("🚀 Run Analysis", type="primary"):
        inputs = {
            'shell_id': shell_id, 'length': length, 'n_tubes': n_tubes,
            'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing, 'baffle_cut': 25,
            'n_passes': 2, 'fouling': 0.0002,
            'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_t, 'T_cold_in': c_t,
            'hot_fluid': h_f, 'cold_fluid': c_f
        }
        
        solver = SegmentalSolver()
        try:
            res = solver.run(inputs)
            vib = VibrationCheck(inputs, res).run_check()
            hyd = API660Validator(inputs, res).check_rho_v2()
            
            # TABS FOR OUTPUT
            t1, t2, t3 = st.tabs(["📊 Results", "🛡️ Safety", "📥 Downloads"])
            
            with t1:
                k1, k2, k3 = st.columns(3)
                k1.metric("Duty", f"{res['Q']/1000:.1f} kW")
                k2.metric("U-Value", f"{res['U']:.1f}")
                k3.metric("Area", f"{res['Area']:.1f} m²")
                
            with t2:
                if vib['status'] == "PASS": st.success(vib['msg'])
                else: st.error(vib['msg'])
                
                if hyd['status'] == "PASS": st.success(hyd['msg'])
                else: 
                    for w in hyd['items']: st.warning(w)

            with t3:
                st.subheader("Commercial Deliverables")
                
                # Excel Generation
                xls_data = generate_tema_sheet(proj_name, inputs, res)
                st.download_button("📥 TEMA Datasheet (.xlsx)", xls_data, f"{proj_name}.xlsx")
                
                # PDF Generation
                pdf_data = create_pdf_quote(proj_name, inputs, res, 15000) # 15k dummy cost
                st.download_button("📄 Sales Quote (.pdf)", pdf_data, f"{proj_name}_Quote.pdf")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

if st.session_state['logged_in']: main_app()
else: render_login()
