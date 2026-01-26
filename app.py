import streamlit as st
from src.core.solver import SegmentalSolver
from src.core.properties import get_available_fluids
from src.data.materials import MaterialDB

st.set_page_config(page_title="ExchangerAI Enterprise", layout="wide", page_icon="🏭")

st.sidebar.header("⚙️ Design Parameters")

# Inputs
shell_id = st.sidebar.number_input("Shell Diameter (m)", 0.2, 5.0, 0.6)
length = st.sidebar.number_input("Tube Length (m)", 1.0, 10.0, 3.0)
n_tubes = st.sidebar.number_input("Number of Tubes", 10, 5000, 150)
baffle_spacing = st.sidebar.number_input("Baffle Spacing (m)", 0.1, 2.0, 0.3)
material = st.sidebar.selectbox("Material", MaterialDB.get_names())

st.title("🏭 ExchangerAI Enterprise v6.0")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Hot Side (Tube)")
    h_fluid = st.selectbox("Fluid", get_available_fluids(), key='h')
    h_m = st.number_input("Flow (kg/s)", 0.1, 500.0, 12.0, key='hm')
    h_ti = st.number_input("Inlet Temp (C)", 0.0, 500.0, 90.0, key='ht')

with c2:
    st.subheader("Cold Side (Shell)")
    c_fluid = st.selectbox("Fluid", get_available_fluids(), key='c', index=1)
    c_m = st.number_input("Flow (kg/s)", 0.1, 500.0, 15.0, key='cm')
    c_ti = st.number_input("Inlet Temp (C)", 0.0, 500.0, 25.0, key='ct')

if st.button("🚀 Run Analysis", type="primary"):
    inputs = {
        'shell_id': shell_id, 'length': length, 'n_tubes': n_tubes,
        'tube_od': 0.019, 'pitch_ratio': 1.25, 'baffle_spacing': baffle_spacing, 'baffle_cut': 25,
        'n_passes': 2, 'fouling': 0.0002,
        'm_hot': h_m, 'm_cold': c_m, 'T_hot_in': h_ti, 'T_cold_in': c_ti,
        'hot_fluid': h_fluid, 'cold_fluid': c_fluid
    }
    
    solver = SegmentalSolver()
    try:
        res = solver.run(inputs)
        
        st.divider()
        k1, k2, k3 = st.columns(3)
        k1.metric("Heat Duty", f"{res['Q']/1000:.1f} kW")
        k2.metric("Overall U", f"{res['U']:.1f} W/m²K")
        k3.metric("Area Required", f"{res['Area']:.1f} m²")
        
        st.success("✅ Analysis Complete - Physics Engine Validated")
    except Exception as e:
        st.error(f"Solver Error: {str(e)}")
