import streamlit as st
from utils import load_pdf_text, preprocess_text, run_demo_pipeline

st.set_page_config(page_title="AI Project 1", layout="wide")

st.title("AI Project 1 — Assignment Viewer & Demo")

# Load and show assignment
st.sidebar.header("Assignment")
pdf_bytes = open("assignment_instructions.pdf", "rb").read()
if st.sidebar.button("Show assignment text"):
    text = load_pdf_text("assignment_instructions.pdf")
    st.sidebar.text_area("Assignment text", text, height=400)

# Inputs
st.header("Demo pipeline (quick, safe default)")
uploaded = st.file_uploader("Upload CSV (optional) — first column used as text", type=["csv"])
example_text = st.text_area("Or paste example text for quick demo", value="Enter sample text here")

if st.button("Run demo"):
    if uploaded:
        df_out = run_demo_pipeline(uploaded)
        st.success("Processed CSV — first 10 rows shown")
        st.dataframe(df_out.head(10))
    else:
        out = preprocess_text(example_text)
        st.write("Processed output:")
        st.json(out)
