import streamlit as st
import plotly.graph_objects as go

def set_streamlit_style():
    # Apply dark/navy background and Garamond font where possible
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Garamond');
        html, body, .stApp { background-color: #011627; color: #ffffff; font-family: 'Garamond', serif; }
        .widget-label { color: #ffffff }
        .stButton>button { background-color:#2EC4B6; color:#011627 }
        </style>
        """, unsafe_allow_html=True)

def format_irf_fig(irfs, horizon):
    t = list(range(horizon))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=irfs["Output"], mode="lines", name="Output"))
    fig.add_trace(go.Scatter(x=t, y=irfs["Consumption"], mode="lines", name="Consumption"))
    fig.add_trace(go.Scatter(x=t, y=irfs["Investment"], mode="lines", name="Investment"))
    fig.add_trace(go.Scatter(x=t, y=irfs["GovDebt"], mode="lines", name="GovDebt"))
    fig.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#0b2136",
                      font_color="#ffffff", legend=dict(bgcolor="#011627"),
                      title="Impulse Response Functions")
    return fig
