import streamlit as st
import plotly.graph_objects as go
from src.fluid_properties import get_available_fluids
from src.solver import DesignSolver
from src.materials import MaterialDB
from src.geometry_plotter import plot_tube_layout

st.set_page_config(page_title="ExchangerPro V4 | Physics Engine", layout="wide")

st.sidebar.header("⚙️ Engineering Design")
st.sidebar.markdown("**Step 1: Geometry Inputs**")

# Real Geometric Inputs
shell_id = st.sidebar.number_input("Shell Diameter (m)", 0.2, 5.0, 0.6)
length = st.sidebar.number_input("Tube Length (m)", 1.0, 10.0, 3.0)
n_tubes = st.sidebar.number_input("Number of Tubes", 10, 5000, 150)
baffle_spacing = st.sidebar.number_input("Baffle Spacing (m)", 0.1, 2.0, 0.3)
material = st.sidebar.selectbox("Material", MaterialDB.get_names())

st.title("🏭 ExchangerPro V4: Physics Core")
st.info("Now running: Kern Method (Shell) + Gnielinski (Tube) + Iterative Energy Balance")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Hot Stream (Tube Side)")
    h_fluid = st.selectbox("Fluid", get_available_fluids(), key='h')
    h_m = st.number_input("Flow (kg/s)", value=12.0, key='hm')
    h_ti = st.number_input("Inlet Temp (C)", value=90.0, key='ht')

with c2:
    st.subheader("Cold Stream (Shell Side)")
    c_fluid = st.selectbox("Fluid", get_available_fluids(), key='c')
    c_m = st.number_input("Flow (kg/s)", value=15.0, key='cm')
    c_ti = st.number_input("Inlet Temp (C)", value=25.0, key='ct')

if st.button("🚀 Run Simulation", type="primary"):
    solver = DesignSolver()
    inputs = {
        'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_ti, 'T_cold_in': c_ti,
        'hot_fluid': h_fluid, 'cold_fluid': c_fluid,
        'shell_id': shell_id, 'n_tubes': n_tubes, 'length': length,
        'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing,
        'material': material, 'fouling': 0.0002
    }
    
    try:
        res = solver.solve_rating(inputs)
        
        # Results
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Heat Duty", f"{res['Q']:.1f} kW")
        k2.metric("Overall U", f"{res['U']:.1f} W/m2K")
        k3.metric("Hot Out", f"{res['T_hot_out']:.1f} °C")
        k4.metric("Cold Out", f"{res['T_cold_out']:.1f} °C")
        
        t1, t2 = st.tabs(["Physics & Hydraulics", "Geometry"])
        
        with t1:
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown("### Tube Side (Hot)")
                st.write(f"Velocity: **{res['v_tube']:.2f} m/s**")
                st.write(f"Reynolds: **{res['Re_tube']:.0f}**")
                if res['Re_tube'] > 4000: st.success("Flow is Turbulent (Good)")
                else: st.warning("Flow is Laminar (Low Efficiency)")
                
            with c_b:
                st.markdown("### Shell Side (Cold)")
                st.write(f"Velocity: **{res['v_shell']:.2f} m/s**")
                st.write(f"Reynolds: **{res['Re_shell']:.0f}**")
        
        with t2:
            st.image(plot_tube_layout(n_tubes, shell_id), caption="Bundle Cross Section")
            
    except Exception as e:
        st.error(f"Solver Convergence Failed: {str(e)}")
