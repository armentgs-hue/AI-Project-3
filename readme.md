AI-Assisted Fiscal Policy Dashboard — ECO 317

Run locally on Windows (PowerShell):
1. cd C:\path\to\project-3
2. python -m venv venv
3. .\venv\Scripts\Activate.ps1
4. pip install -r requirements.txt
5. streamlit run app.py

Deploy to Streamlit Community Cloud:
- Push this repo to GitHub (root contains app.py and requirements.txt).
- Go to https://share.streamlit.io → New app → choose repo, branch main, file app.py → Deploy.
