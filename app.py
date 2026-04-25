import streamlit as st
from dsgemodel import DSGEEngine
from utils import format_irf_fig, set_streamlit_style

st.set_page_config(page_title="AI-Assisted Fiscal Policy Dashboard", layout="wide")
set_streamlit_style()

st.title("AI-Assisted Fiscal Policy Dashboard — ECO 317 (Spring 2026)")

# Global sidebar (structural sliders)
st.sidebar.header("Global structural parameters")
params = {
    "h": st.sidebar.slider("Habit formation (h)", 0.0, 0.9, 0.5, 0.01),
    "psi": st.sidebar.slider("Capital utilization cost (psi)", 0.0, 10.0, 2.0, 0.1),
    "theta_p": st.sidebar.slider("Price stickiness (theta_p)", 0.0, 0.99, 0.75, 0.01),
    "theta_w": st.sidebar.slider("Wage stickiness (theta_w)", 0.0, 0.99, 0.75, 0.01),
    "phi_b": st.sidebar.slider("Debt-feedback aggressiveness (phi_b)", 0.0, 5.0, 1.0, 0.05),
    "ron0": st.sidebar.number_input("Steady interest rate (annual %)", 0.0, 20.0, 2.0, 0.1),
    "share_rot": st.sidebar.slider("Rule-of-Thumb share", 0.0, 0.5, 0.1, 0.01),
}

# Engine with caching
@st.cache_data(ttl=600, show_spinner=False)
def make_engine(p):
    eng = DSGEEngine(**p)
    eng.build_linear_model()
    return eng

engine = make_engine(params)

tabs = st.tabs(["Model Fit (Unconditional)", "Fiscal Exercises (Conditional)"])

with tabs[0]:
    st.header("Phase II — Model Fit (Unconditional Dynamics)")
    st.write("Simulate 1,000 periods of random shocks and compute moments.")
    periods = st.number_input("Simulation periods", min_value=500, max_value=2000, value=1000, step=100)
    if st.button("Run unconditional sim"):
        sim = engine.simulate_unconditional(periods=periods)
        moments = engine.compute_moments(sim)
        st.subheader("Key simulated moments")
        st.table(moments)
        st.subheader("AI-style interpretation")
        st.markdown(engine.generate_moment_interpretation(moments))

with tabs[1]:
    st.header("Phase III — Fiscal Exercises (Conditional Policy)")
    st.write("Select fiscal shock and financing rule, simulate 40 quarters (10 years).")
    shock_type = st.selectbox("Fiscal shock", ["Govt_consumption", "Govt_investment", "Labor_tax_cut", "Capital_tax_cut"])
    shock_size = st.number_input("Shock size (percent of steady-state GDP)", 0.0, 20.0, 2.0, 0.1)
    financing = st.selectbox("Financing rule", ["Lump-Sum", "Consumption_Tax", "Labor_Tax", "Capital_Tax", "Spending_Cut"])
    horizon = st.slider("IRF horizon (quarters)", 4, 160, 40, 4)
    if st.button("Run fiscal experiment"):
        irfs, debt_path = engine.run_fiscal_experiment(shock_type, shock_size, financing, horizon=horizon)
        fig = format_irf_fig(irfs, horizon)
        st.plotly_chart(fig, use_container_width=True)
        # multipliers
        impact, cumulative = engine.compute_multipliers(irfs, shock_size)
        st.metric("Impact multiplier (output per gov. shock)", f"{impact:.3f}")
        st.metric("Cumulative multiplier (discounted 40q)", f"{cumulative:.3f}")
        st.subheader("Automated policy briefing")
        st.markdown(engine.generate_policy_briefing(shock_type, financing, impact, cumulative, debt_path))
