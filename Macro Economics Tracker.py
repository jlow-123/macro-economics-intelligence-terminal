# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 01:37:26 2026

@author: jolin
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

# terminal configuration & theme
st.set_page_config(page_title="Macro Economics Intelligence Terminal", layout="wide")

# custom CSS
st.markdown("""
    <style>
    .metric-container {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .indicator-label {
        color: #8b949e;
        font-size: 0.9em;
        font-weight: bold;
    }
    /* Style for the regime probabilities */
    .stProgress > div > div > div > div {
        background-color: #4CAF50; /* Green for progress bar */
    }
    .stProgress {
        background-color: #30363d; /* Darker background for progress bar container */
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

if "trend_history" not in st.session_state:
    st.session_state.trend_history = []

# systematic logic & scenario logic
@st.cache_resource
def load_engine():
    class Engine:
        def __init__(self):
            np.random.seed(42)
            X = pd.DataFrame(np.random.normal(2, 1, (1000, 6)), 
                             columns=["US_CPI", "EU_CPI", "Asia_CPI", "Liq", "Semi", "Growth"])
            y = X["Growth"] * 0.5 + X["Semi"] * 0.3 - X["Liq"] * 0.8
            self.model = RandomForestRegressor(n_estimators=50).fit(X, y)
        def predict(self, inputs):
            return self.model.predict(np.array(inputs).reshape(1, -1))[0]
    return Engine()

engine = load_engine()

# feed inputs
with st.sidebar:
    st.title("Systemic Feeds")
    
    # shock stress testing
    st.subheader("Scenario Shocks Stress Testing")
    col_s1, col_s2 = st.columns(2)
    shock_inf = col_s1.button("Inflation Shock")
    shock_liq = col_s2.button("Liquidity Crisis")

    st.divider()
    st.subheader("Global Inflation Feed")
    
    def precision_sync(label, min_v, max_v, default, key):
        val = st.number_input(label, min_v, max_v, default, step=0.1, key=f"n_{key}")
        return st.slider(f"Adjust {label}", min_v, max_v, float(val), key=f"s_{key}")

    # setting defaults based on shocks
    def_us_cpi = 8.5 if shock_inf else 3.1
    def_eu_cpi = 7.0 if shock_inf else 2.8
    def_as_cpi = 4.0 if shock_inf else 1.5
    def_liq_stress = 0.85 if shock_liq else 0.20

    c_us = precision_sync("US CPI (YoY %)", -2.0, 15.0, def_us_cpi, "us")
    c_eu = precision_sync("EU CPI (YoY %)", -2.0, 15.0, def_eu_cpi, "eu")
    c_as = precision_sync("Asia CPI (YoY %)", -2.0, 15.0, def_as_cpi, "as")
    
    st.divider()
    st.subheader("Leading Factors")
    liquidity = precision_sync("Liquidity Stress", 0.0, 1.0, def_liq_stress, "liq")
    semi_cycle = precision_sync("Semi Cycle", 0.0, 1.0, 0.7, "semi")
    growth_leading = precision_sync("Growth Index", -5.0, 10.0, 2.2, "gro")

# data processing
avg_inf = np.mean([c_us, c_eu, c_as])
inputs = [c_us, c_eu, c_as, liquidity, semi_cycle, growth_leading]
gdp_nowcast = engine.predict(inputs)
st.session_state.trend_history.append(gdp_nowcast)

# ensure values stay between 0.0 & 1.0
probs = {
    "Stagflation": np.clip((avg_inf/10) * (1 - growth_leading/10) * max(1, liquidity*2), 0.0, 1.0),
    "Goldilocks": np.clip((1 - liquidity) * (growth_leading/10) * (1 - avg_inf/10), 0.0, 1.0),
    "Tech Boom": np.clip(semi_cycle * (growth_leading/5) * (1-liquidity), 0.0, 1.0),
    "Crisis": np.clip(liquidity * (1 - growth_leading/5), 0.0, 1.0)
}

# ensure probabilities sum to exactly 1.0
total_p = sum(probs.values())
if total_p > 0:
    probs = {k: v/total_p for k, v in probs.items()}
else:
    # fallback if all calcs result in 0
    probs = {k: 1.0/len(probs) for k in probs}

current_regime = max(probs, key=probs.get)

# main dashboard
st.title("Macro Economics Intelligence Terminal")

# outcome
with st.container():
    st.markdown("""
        <div class='metric-container' style='padding-top: 0px; padding-bottom: 0px; margin-top: -10px;'>
            <div style='
                display: flex; 
                align-items: center; 
                justify-content: flex-center; 
                min-height: 45px; 
                margin-top: 5px;
            '>
                <span style='color: #8b949e; font-size: 0.84em; text-align: center; line-height: 1.2;'>
                    <strong>Ghost GDP Nowcast:</strong> A real-time synthetic estimation of economic growth derived from high-frequency leading indicators (Semis, Liquidity, and CPI) before official data releases.
                </span>
            </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: -20px;'>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    
    
    st.markdown("</div>", unsafe_allow_html=True) 
    st.markdown("</div>", unsafe_allow_html=True)
    
    gdp_col = "#28a745" if gdp_nowcast > 1.5 else "#ff4b4b" if gdp_nowcast < 0 else "#FFA500"
    m1.markdown(f"<p class='indicator-label'>GHOST GDP NOWCAST</p><h2 style='color:{gdp_col}'>{gdp_nowcast:.2f}%</h2>", unsafe_allow_html=True)
    
    liq_col = "#ff4b4b" if liquidity > 0.6 else "#28a745" if liquidity < 0.2 else "#FFA500"
    m2.markdown(f"<p class='indicator-label'>SYSTEMIC STRESS</p><h2 style='color:{liq_col}'>{liquidity*100:.1f} pts</h2>", unsafe_allow_html=True)
    
    inf_narr = "Hot" if avg_inf > 4.5 else "Warming" if avg_inf > 2.5 else "Cool"
    inf_col = "#ff4b4b" if avg_inf > 4.5 else "#FFA500" if avg_inf > 2.5 else "#28a745"
    m3.markdown(f"<p class='indicator-label'>INFLATION NARRATIVE</p><h2 style='color:{inf_col}'>{inf_narr}</h2>", unsafe_allow_html=True)
    
    policy = "Restrictive" if avg_inf > 3.5 else "Accommodative" if gdp_nowcast < 1.0 else "Neutral"
    policy_col = "#ff4b4b" if policy == "Restrictive" else "#28a745" if policy == "Accommodative" else "#FFA500"
    m4.markdown(f"<p class='indicator-label'>POLICY STANCE</p><h2 style='color:{policy_col}'>{policy}</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# regime probability engine
st.subheader("Regime Probability Engine")
prob_cols = st.columns(len(probs))
sorted_probs = sorted(probs.items(), key=lambda item: item[1], reverse=True) # Sort for better display
for i, (regime, p) in enumerate(sorted_probs):
    prob_cols[i].markdown(f"**{regime}**")
    prob_cols[i].progress(p)
    prob_cols[i].caption(f"{p*100:.1f}%")

st.divider()

# market impact prediction & contagion map
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("Cross-Asset Market Impact")
    # mapping regime probabilities to market impact
    impact_data = {
        "Asset": ["S&P 500", "Gold (GLD)", "US 10Y Yield", "Bitcoin", "Semis (SOXX)"],
        "Expected Move": ["Neutral", "Bullish", "Bullish", "Bearish", "Strong Bullish"] if current_regime == "Tech Boom" else 
                         ["Strong Bearish", "Bullish", "Bullish", "Strong Bearish", "Bearish"] if current_regime == "Stagflation" else
                         ["Neutral", "Neutral", "Neutral", "Neutral", "Neutral"], 
        "Confidence": [f"{probs[current_regime]*100:.0f}%"] * 5
    }
    st.table(pd.DataFrame(impact_data))
    
    st.subheader("Ghost GDP Historical Nowcast")
    st.line_chart(st.session_state.trend_history[-30:]) 
    if st.button("Reset Historical Trend"):
        st.session_state.trend_history = []
        st.rerun()

with col_right:
    st.subheader("Regional Contagion Map")
    
    coords = {
        "USA": [37.0902, -95.7129],
        "EU": [50.0, 10.0],
        "Asia": [34.0479, 100.6197]
    }

    # base nodes (USA, EU, Asia)
    fig = go.Figure(go.Scattergeo(
        lon=[coords["USA"][1], coords["EU"][1], coords["Asia"][1]],
        lat=[coords["USA"][0], coords["EU"][0], coords["Asia"][0]],
        text=["USA", "EU", "Asia"],
        mode='markers+text',
        marker=dict(
            size=25, 
            color=[c_us, c_eu, c_as], 
            colorscale="Reds", 
            showscale=True, 
            cmin=-2, 
            cmax=15,
            line=dict(width=1, color='white')
        ),
        textfont=dict(color="white", size=11, family="Arial Black"),
        textposition="bottom center"
    ))

    # contagion logic: inflation transmission (US -> EU)
    if c_us > 4.0 and c_eu < c_us * 0.8:
        strength = min(1.0, (c_us - 4.0) / 6.0)
        a_color = f'rgba(255, 60, 60, {strength})'
        a_width = 2 + (strength * 6)
        fig.add_trace(go.Scattergeo(
            lon=[coords["USA"][1], coords["EU"][1]],
            lat=[coords["USA"][0], coords["EU"][0]],
            mode='lines',
            line=dict(width=a_width, color=a_color),
            hoverinfo='text',
            text=f"US to EU Inflation Contagion: {strength*100:.1f}%"
        ))

    # contagion logic: liquidity stress (Asia -> EU -> US)
    if liquidity > 0.6: 
        l_strength = min(1.0, (liquidity - 0.6) / 0.4)
        l_color = f'rgba(255, 165, 0, {l_strength})'
        l_width = 2 + (l_strength * 5)

        # Asia to EU
        fig.add_trace(go.Scattergeo(
            lon=[coords["Asia"][1], coords["EU"][1]],
            lat=[coords["Asia"][0], coords["EU"][0]],
            mode='lines',
            line=dict(width=l_width, color=l_color, dash='dot'),
            hoverinfo='text',
            text=f"Asia to EU Liquidity Stress: {l_strength*100:.1f}%"
        ))
        
        # EU to US (conditional propagation)
        if c_eu > 3.0:
            fig.add_trace(go.Scattergeo(
                lon=[coords["EU"][1], coords["USA"][1]],
                lat=[coords["EU"][0], coords["USA"][0]],
                mode='lines',
                line=dict(width=l_width, color=l_color, dash='dot'),
                hoverinfo='text',
                text=f"EU to US Liquidity Contagion: {l_strength*100:.1f}%"
            ))

    # layout
    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            scope='world',
            projection_type='natural earth',
            showland=True,
            landcolor="#1b1e23",
            showocean=True,
            oceancolor="#0d1117",
            showcountries=True,
            countrycolor="#444d56",
            coastlinecolor="#444d56"
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# historical comparison
st.divider()
st.subheader("Historical Comparison")
benchmarks = {
    "1970s Great Inflation": [12.0, 10.0, 6.0, 0.4, 0.2, -2.0],
    "2008 GFC Crunch": [2.0, 1.5, 1.0, 0.95, 0.1, -5.0],
    "2024 AI Expansion": [3.2, 2.5, 1.8, 0.2, 0.9, 3.5]
}

comp_results = []
for name, data in benchmarks.items():
    sim = max(0, 100 - np.linalg.norm(np.array(inputs) - np.array(data)) * 10)
    comp_results.append({"Historical Event": name, "Similarity Score": f"{sim:.1f}%"})



st.table(pd.DataFrame(comp_results))
