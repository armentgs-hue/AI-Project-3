import io
import pandas as pd
from typing import Dict
from pdfminer.high_level import extract_text

def load_pdf_text(path: str) -> str:
    return extract_text(path)

def preprocess_text(text: str) -> Dict:
    # Minimal deterministic preprocessing: lowercase, length, token count
    t = text.strip()
    tokens = t.split()
    return {"text": t, "length": len(t), "token_count": len(tokens), "preview": t[:500]}

def run_demo_pipeline(csv_file) -> pd.DataFrame:
    # csv_file may be an UploadedFile or path
    if hasattr(csv_file, "read"):
        df = pd.read_csv(csv_file)
    else:
        df = pd.read_csv(csv_file)
    first_col = df.columns[0]
    df["processed_preview"] = df[first_col].astype(str).map(lambda s: s.strip()[:300])
    df["token_count"] = df[first_col].astype(str).map(lambda s: len(s.split()))
    return df
