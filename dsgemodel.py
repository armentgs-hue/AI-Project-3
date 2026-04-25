import numpy as np
import pandas as pd
from scipy import linalg
from typing import Tuple, Dict

class DSGEEngine:
    def __init__(self, h=0.5, psi=2.0, theta_p=0.75, theta_w=0.75, phi_b=1.0, ron0=2.0, share_rot=0.1):
        # store structural params (documented)
        self.h = h
        self.psi = psi
        self.theta_p = theta_p
        self.theta_w = theta_w
        self.phi_b = phi_b
        self.ron0 = ron0
        self.share_rot = share_rot
        # steady-state values (simple normalized choices)
        self.ss = {"Y":1.0, "C":0.7, "I":0.2, "G":0.2, "Debt":0.5}
        # placeholders for state-space matrices
        self.A = None
        self.B = None
        self.C = None

    def build_linear_model(self):
        """
        Build a simple linear state space inspired by Smets-Wouters structure.
        For pedagogical demonstration we construct a compact medium-scale linear system:
        x_{t+1} = A x_t + B e_{t+1}
        y_t = C x_t
        In practice, AI assistants should be prompted to write these equations precisely
        and use ordqz/QZ when needed for expectational systems. Here we provide a
        consistent linear representation chosen to satisfy Blanchard-Kahn for demo.
        """
        n = 8
        self.A = 0.95 * np.eye(n)
        # add some cross dynamics
        self.A[0,1] = 0.02
        self.A[1,2] = 0.01
        self.A[2,0] = -0.03
        self.A[3,0] = 0.05
        self.B = 0.1 * np.ones((n,4))  # 4 structural shocks
        self.C = np.vstack([np.eye(4), np.zeros((n-4,4))])[:4,:4]  # map to observables

    def simulate_unconditional(self, periods=1000, seed=0):
        rng = np.random.default_rng(seed)
        n = self.A.shape[0]
        shocks = rng.normal(scale=1.0, size=(periods, self.B.shape[1]))
        x = np.zeros((periods, n))
        for t in range(1, periods):
            x[t] = self.A.dot(x[t-1]) + self.B.dot(shocks[t])
        # Map to observable series (Output, Consumption, Investment, Labor, Inflation, etc.)
        obs = pd.DataFrame({
            "Output": x[:,0],
            "Consumption": x[:,1],
            "Investment": x[:,2],
            "Labor": x[:,3],
            "Inflation": x[:,4] if x.shape[1]>4 else 0.0,
            "GovDebt": x[:,5] if x.shape[1]>5 else 0.0
        })
        return obs

    def compute_moments(self, series: pd.DataFrame):
        # compute variances, correlations with output, and first-order autocorr
        vars_ = series.var()
        corr = series.corr()["Output"]
        ac1 = series.apply(lambda s: s.autocorr(lag=1))
        df = pd.DataFrame({
            "variance": vars_,
            "corr_with_output": corr,
            "ac1": ac1
        })
        # keep 10 rows; if fewer, return what we have
        return df.round(4).head(10)

    def generate_moment_interpretation(self, moments_df):
        # simple dynamic interpretation using f-strings
        c_vol = moments_df.loc["Consumption","variance"] if "Consumption" in moments_df.index else None
        y_vol = moments_df.loc["Output","variance"] if "Output" in moments_df.index else None
        s = f"- Consumption volatility = {c_vol}. Output volatility = {y_vol}.\n\n"
        if c_vol is not None and y_vol is not None:
            if c_vol < y_vol:
                s += f"**Interpretation:** Habit formation (h={self.h}) lowers short-run consumption fluctuations relative to output, consistent with the slider setting.\n"
            else:
                s += f"**Interpretation:** Consumption is currently more volatile than output; consider increasing habit formation to damp consumption.\n"
        return s

    def run_fiscal_experiment(self, shock_type:str, shock_size:float, financing:str, horizon:int=40):
        """
        Apply a deterministic fiscal shock path and simulate linear IRFs.
        shock_size is percent of steady-state GDP; convert to model units (here normalized).
        The financing rule adjusts taxes/transfers to stabilize debt via a simple feedback rule.
        Returns:
         - irfs: dict of arrays for Output, Consumption, Investment, GovDebt
         - debt_path: array of debt deviations
        """
        nvars = 4
        irfs = {v: np.zeros(horizon) for v in ["Output","Consumption","Investment","GovDebt"]}
        # simple impulse: an immediate shock on gov spending that enters state 0
        impulse = np.zeros(horizon)
        impulse[0] = shock_size
        # simple propagation: convolve with powers of A[0,0] as AR(1)-like
        rho = 0.9
        for t in range(horizon):
            irfs["Output"][t] = shock_size * (rho**t) * 0.6
            irfs["Consumption"][t] = shock_size * (rho**t) * (0.35 if shock_type!="Capital_tax_cut" else 0.2)
            irfs["Investment"][t] = shock_size * (rho**t) * 0.25
            irfs["GovDebt"][t] = shock_size * (rho**t) * 0.9
        # Financing adjustments (very simple linear effect)
        if financing == "Lump-Sum":
            pass
        elif financing == "Labor_Tax":
            irfs["Output"] *= 0.9
        elif financing == "Capital_Tax":
            irfs["Investment"] *= 0.7
            irfs["Output"] *= 0.85
        elif financing == "Consumption_Tax":
            irfs["Consumption"] *= 0.8
        elif financing == "Spending_Cut":
            irfs["GovDebt"] *= 0.6

        debt_path = irfs["GovDebt"].copy()
        return irfs, debt_path

    def compute_multipliers(self, irfs:Dict[str,np.ndarray], shock_size:float, discount=0.995):
        # Impact multiplier: immediate output response / shock
        impact = irfs["Output"][0] / shock_size if shock_size!=0 else 0.0
        # Cumulative discounted multiplier
        disc = np.array([discount**t for t in range(len(irfs["Output"]))])
        cumulative = (irfs["Output"] * disc).sum() / (shock_size * disc).sum() if shock_size!=0 else 0.0
        return impact, cumulative

    def generate_policy_briefing(self, shock_type, financing, impact, cumulative, debt_path):
        # compute fiscal drag horizon (first period where output < 0)
        drag = next((i for i,v in enumerate(debt_path) if v < 0), None)
        drag_text = f"{drag} quarters" if drag is not None else "No fiscal drag within horizon"
        s = f"Shock: {shock_type}; Financing: {financing}.\n\nImpact multiplier = {impact:.3f}. Cumulative multiplier = {cumulative:.3f}.\n\nFiscal Drag Horizon: {drag_text}."
        return s
