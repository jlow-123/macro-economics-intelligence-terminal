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
    .card-title {
        font-size: 1.4rem !important;
        font-weight: 1000 !important;
        color: #8b949e;
        margin-bottom: 8px;
    }

    .card-value {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        line-height: 1.1;
        margin-bottom: 15px;
    }

    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        min-height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }

    .driver-score {
        font-size: 0.85rem;
        font-weight: 400;
        color: #58a6ff;
        border-top: 1px solid #30363d;
        padding-top: 10px;
        width: 100%;
    }

    .stAlert {
        margin-top: 30px !important;
    }
    </style>
""", unsafe_allow_html=True)

if "trend_history" not in st.session_state:
    st.session_state.trend_history = []

# institutional macro memory
if "macro_memory" not in st.session_state:
    st.session_state.macro_memory = []

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

# tells user which information is signal/noise

feature_names = [
    "US CPI",
    "EU CPI",
    "Asia CPI",
    "Liquidity",
    "Semi Cycle",
    "Growth Index"
]

# extract feature importance from random forest
importances = engine.model.feature_importances_

signal_results = []

for name, imp in zip(feature_names, importances):

    if imp > 0.40:
        label = "Core Macro Driver"
        color = "#ff4b4b"
    elif imp > 0.20:
        label = "Secondary Signal"
        color = "#FFA500"
    elif imp > 0.08:
        label = "Weak Signal"
        color = "#8b949e"
    else:
        label = "Noise"
        color = "#444d56"

    signal_results.append({
        "Indicator": name,
        "Signal Strength": imp,
        "Classification": label,
        "Color": color
    })

signal_df = pd.DataFrame(signal_results)

st.session_state.trend_history.append(gdp_nowcast)

# store macro state (institutional memory)
current_state = {
    "timestamp": datetime.now(),
    "inputs": inputs,
    "gdp": gdp_nowcast
}
st.session_state.macro_memory.append(current_state)

# ensure values stay between 0.0 & 1.0
base_probs = {
    "Stagflation": (avg_inf / 5) * (1 - (growth_leading + 5) / 15),
    "Goldilocks": (1 - liquidity) * ((growth_leading + 5) / 15) * (1 - (avg_inf / 10)),
    "Tech Boom": semi_cycle * ((growth_leading + 5) / 15) * (1 - liquidity),
    "Crisis": liquidity * (1 - (growth_leading + 5) / 15)
}

exp_p = {k: np.exp(v * 2) for k, v in base_probs.items()}
sum_exp = sum(exp_p.values())
probs = {k: v / sum_exp for k, v in exp_p.items()}

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
                justify-content: flex-start;  /* CHANGED FROM flex-center */
                min-height: 45px; 
                margin-top: 5px;
            '>
                <span style='color: #8b949e; font-size: 0.84em; text-align: left; line-height: 1.2;'>
                    <strong>Ghost GDP Nowcast:</strong> A real-time synthetic estimation of economic growth derived from high-frequency leading indicators (Semis, Liquidity, and CPI) before official data releases.
                </span>
            </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: -20px;'>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    
    
    st.markdown("</div>", unsafe_allow_html=True) 
    st.markdown("</div>", unsafe_allow_html=True)
    
    # gdp narrative
    gdp_col = "#28a745" if gdp_nowcast > 1.5 else "#ff4b4b" if gdp_nowcast < 0 else "#FFA500"
    m1.markdown(f"""
            <p class='indicator-label'>Ghost GDP Nowcast</p>
            <h2 style='color:{gdp_col}'>{gdp_nowcast:.2f}%</h2>
            <span style='color:#8b949e; font-size:0.8em'>Growth Velocity</span>
        """, unsafe_allow_html=True)    
        
    # liquidity narrative
    liq_narr = "Tightening" if liquidity > 0.6 else "Neutral" if liquidity > 0.3 else "Loose"
    liq_narr_col = "#ff4b4b" if liquidity > 0.6 else "#FFA500" if liquidity > 0.3 else "#28a745"
    liq_col = "#ff4b4b" if liquidity > 0.6 else "#28a745" if liquidity < 0.2 else "#FFA500"
    m2.markdown(
        f"<p class='indicator-label'>Liquidity Narrative</p>"
        f"<h2 style='color:{liq_narr_col}'>{liq_narr}</h2>"
        f"<span style='color:#8b949e; font-size:0.8em'>{liquidity*100:.1f} stress pts</span>",
    unsafe_allow_html=True)
    
    # inflation narrative
    inf_narr = "Hot" if avg_inf > 4.5 else "Warming" if avg_inf > 2.5 else "Cool"
    inf_col = "#ff4b4b" if avg_inf > 4.5 else "#FFA500" if avg_inf > 2.5 else "#28a745"
    
    m3.markdown(f"""
            <p class='indicator-label'>Inflation Narrative</p>
            <h2 style='color:{inf_col}'>{inf_narr}</h2>
            <span style='color:#8b949e; font-size:0.8em'>{avg_inf:.1f}% basket avg</span>
        """, unsafe_allow_html=True)    
    
    # policy narrative
    policy = "Restrictive" if avg_inf > 3.5 else "Accommodative" if gdp_nowcast < 1.0 else "Neutral"
    policy_col = "#ff4b4b" if policy == "Restrictive" else "#28a745" if policy == "Accommodative" else "#FFA500"
    m4.markdown(f"""
            <p class='indicator-label'>Policy Stance</p>
            <h2 style='color:{policy_col}'>{policy}</h2>
            <span style='color:#8b949e; font-size:0.8em'>Systemic Bias</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# signal v noise structuring
st.subheader("Macro Signal vs Noise Intelligence")

# extract importance directly from model
importances = engine.model.feature_importances_
feature_names = ["US CPI", "EU CPI", "Asia CPI", "Liquidity", "Semi Cycle", "Growth Index"]

sig_cols = st.columns(6)

for i, (name, imp) in enumerate(zip(feature_names, importances)):
    # classification logic
    if imp > 0.40:   label, color = "Core Macro<br>Driver", "#ff4b4b"
    elif imp > 0.15: label, color = "Secondary<br>Signal", "#FFA500"
    else:            label, color = "Noise", "#444d56"

    with sig_cols[i]:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='card-label'>{name}</div>
                <div class='card-value' style='color:{color};'>{label}</div>
                <div class='card-strength'>Driver Score: {imp:.3f}</div>
            </div>
        """, unsafe_allow_html=True)

top_signal = signal_df.sort_values("Signal Strength", ascending=False).iloc[0]

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

st.info(
    f"Primary Macro Driver Detected: **{top_signal['Indicator']}** "
    f"(Signal Strength {top_signal['Signal Strength']:.3f})"
)

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
    # market impact & strat
    st.subheader("Cross-Asset Market Impact & Strategy")
    
    # define asset behaviour per regime
    # weights: 1.0 (strong bullish), 0.5 (bullish), 0 (neutral), -0.5 (bearish), -1.0 (strong bearish)
    regime_dna = {
        "Stagflation": {"S&P 500": -1.0, "Gold (GLD)": 0.8, "US 10Y Yield": 0.7, "Bitcoin": -0.8, "Semis": -0.6},
        "Goldilocks":  {"S&P 500": 1.0,  "Gold (GLD)": 0.2, "US 10Y Yield": 0.0, "Bitcoin": 0.6,  "Semis": 0.8},
        "Tech Boom":   {"S&P 500": 0.7,  "Gold (GLD)": -0.2, "US 10Y Yield": 0.4, "Bitcoin": 0.5,  "Semis": 1.0},
        "Crisis":      {"S&P 500": -1.0, "Gold (GLD)": 0.5, "US 10Y Yield": 0.9, "Bitcoin": -1.0, "Semis": -1.0}
    }
    
    # actionable insight
    tactical_map = {
        "S&P 500": "Overweight Equities" if probs["Goldilocks"] > 0.4 else "Hedge Beta",
        "Gold (GLD)": "Long Inflation Hedge" if probs["Stagflation"] > 0.3 else "Neutral",
        "US 10Y Yield": "Short Duration" if avg_inf > 4.0 else "Long Duration",
        "Bitcoin": "Risk-On Allocation" if probs["Tech Boom"] > 0.4 else "Avoid / Short",
        "Semis": "Core Tech Holding" if semi_cycle > 0.6 else "Underweight"
    }
    
    impact_results = []
    for asset in ["S&P 500", "Gold (GLD)", "US 10Y Yield", "Bitcoin", "Semis"]:
        # calculate probability-weighted score
        weighted_score = sum(probs[r] * regime_dna[r][asset] for r in probs)
        
        # map score to text
        if weighted_score > 0.6: move = "Strong Bullish"
        elif weighted_score > 0.2: move = "Bullish"
        elif weighted_score < -0.6: move = "Strong Bearish"
        elif weighted_score < -0.2: move = "Bearish"
        else: move = "Neutral"
        
        impact_results.append({
            "Asset": asset,
            "Expected Move": move,
            "Sentiment Score": f"{weighted_score:.4f}", 
            "Tactical Stance": tactical_map[asset]
        })

    df_impact = pd.DataFrame(impact_results)

    styled_impact = df_impact.style.set_properties(**{
        'text-align': 'left',
        'white-space': 'pre'
    })

    st.table(styled_impact)
    
    # strategic callout box
    st.info(f"**Primary Portfolio Directive:** Based on a **{probs[current_regime]*100:.1f}%** probability of **{current_regime}**, Suggestion - " + 
            ("Capital Preservation & Liquidity" if current_regime in ["Crisis", "Stagflation"] else "Growth Aggression & Semi Exposure"))
    
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

    fig = go.Figure()

    # base nodes
    fig.add_trace(go.Scattergeo(
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


    # a. US -> EU inflation transmission
    if c_us > 4.0 and c_eu < c_us * 0.8:
        strength = min(1.0, (c_us - 4.0) / 6.0)
        fig.add_trace(go.Scattergeo(
            lon=[coords["USA"][1], coords["EU"][1]],
            lat=[coords["USA"][0], coords["EU"][0]],
            mode='lines',
            line=dict(width=2 + (strength * 6), color=f'rgba(255, 60, 60, {strength})'),
            text=f"US → EU Inflation Export: {strength*100:.1f}%"
        ))
    
    # b. global liquidity stress transmission
    if liquidity > 0.6:
        l_strength = min(1.0, (liquidity - 0.6) / 0.4)
        l_color = f'rgba(255, 165, 0, {l_strength})'
    
        # Asia -> EU
        fig.add_trace(go.Scattergeo(
            lon=[coords["Asia"][1], coords["EU"][1]],
            lat=[coords["Asia"][0], coords["EU"][0]],
            mode='lines',
            line=dict(width=2 + (l_strength * 5), color=l_color, dash='dot'),
            text=f"Asia → EU Liquidity Stress: {l_strength*100:.1f}%"
        ))
    
        # EU -> US
        if c_eu > 3.0:
            fig.add_trace(go.Scattergeo(
                lon=[coords["EU"][1], coords["USA"][1]],
                lat=[coords["EU"][0], coords["USA"][0]],
                mode='lines',
                line=dict(width=2 + (l_strength * 5), color=l_color, dash='dot'),
                text=f"EU → US Liquidity Stress: {l_strength*100:.1f}%"
            ))
    
    # c. US <-> Asia supply chain / tech stress
    if c_as > 5.0 or semi_cycle < 0.3:
        t_strength = min(1.0, (c_as / 10.0))
        fig.add_trace(go.Scattergeo(
            lon=[coords["USA"][1], coords["Asia"][1]],
            lat=[coords["USA"][0], coords["Asia"][0]],
            mode='lines',
            line=dict(width=2 + (t_strength * 4), color='rgba(255, 140, 0, 0.7)', dash='dash'),
            text=f"US ↔ Asia Supply Chain Stress: {t_strength*100:.1f}%"
        ))
    
    # d. EU -> US industrial / energy spillover
    if c_eu > 5.0 and c_eu > c_us:
        e_strength = min(1.0, (c_eu - 5.0) / 5.0)
        fig.add_trace(go.Scattergeo(
            lon=[coords["EU"][1], coords["USA"][1]],
            lat=[coords["EU"][0], coords["USA"][0]],
            mode='lines',
            line=dict(width=1.5 + (e_strength * 3), color='rgba(120, 180, 255, 0.7)', dash='dot'),
            text=f"EU → US Industrial Spillover: {e_strength*100:.1f}%"
        ))
    
    # e. EU -> Asia demand shock
    if liquidity > 0.5 and c_eu > 4.0:
        d_strength = min(1.0, liquidity)
        fig.add_trace(go.Scattergeo(
            lon=[coords["EU"][1], coords["Asia"][1]],
            lat=[coords["EU"][0], coords["Asia"][0]],
            mode='lines',
            line=dict(width=1.5 + (d_strength * 3), color='rgba(255, 255, 255, 0.6)', dash='dash'),
            text=f"EU → Asia Demand Shock: {d_strength*100:.1f}%"
        ))
    
    # f. flight to safety (capital flows to US)
    if liquidity > 0.7 or current_regime == "Crisis":
        f_strength = min(1.0, liquidity)
    
        fig.add_trace(go.Scattergeo(
            lon=[coords["EU"][1], coords["USA"][1]],
            lat=[coords["EU"][0], coords["USA"][0]],
            mode='lines',
            line=dict(width=2 + (f_strength * 4), color='rgba(0, 255, 150, 0.7)'),
            text=f"Flight to Safety → US Assets: {f_strength*100:.1f}%"
        ))
    
        fig.add_trace(go.Scattergeo(
            lon=[coords["Asia"][1], coords["USA"][1]],
            lat=[coords["Asia"][0], coords["USA"][0]],
            mode='lines',
            line=dict(width=2 + (f_strength * 4), color='rgba(0, 255, 150, 0.7)'),
            text=f"Flight to Safety → US Assets: {f_strength*100:.1f}%"
        ))

    # layout
    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=10, b=0),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            projection_type='natural earth',
            showland=True, landcolor="#1b1e23",
            showocean=True, oceancolor="#0d1117",
            showcountries=True, countrycolor="#444d56"
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div style='background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-top: 10px;'>

<p class='indicator-label' style='margin-bottom: 10px;'>CONTAGION INTELLIGENCE BRIEF</p>

<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85em; color: #8b949e;'>

<div>
<span style='color:#ff4b4b;'>●</span>
<b>Solid Red:</b> (Inflation Export) High inflation in 1 economy transmitting cost pressures globally through trade and commodities.
</div>

<div>
<span style='color:#FFA500;'>┄</span>
<b>Orange Dotted:</b> (Liquidity Stress) Tight financial conditions spreading through global credit and funding markets.
</div>

<div>
<span style='color:#FFA500;'>- -</span>
<b>Orange Dashed:</b> (Supply Chain Stress) Technology or manufacturing disruptions between major production hubs.
</div>

<div>
<span style='color:#78b4ff;'>┄</span>
<b>Blue Dotted:</b> (Industrial Spillover) Industrial or energy shocks transmitting across regions.
</div>

<div>
<span style='color:#ffffff;'>- -</span>
<b>White Dashed:</b> (Demand Shock) Economic slowdown in one region reducing global trade demand.
</div>

<div>
<span style='color:#00ff96;'>▬</span>
<b>Green Solid:</b> (Flight to Safety) Capital flows toward perceived safe assets during systemic stress.
</div>

</div>

<p style='font-size: 0.75em; color: #444d56; margin-top: 10px; font-style: italic;'>
Contagion pathways activate dynamically when macro stress thresholds are breached (e.g., CPI spikes, liquidity tightening, or supply shocks).
</p>

</div>
""", unsafe_allow_html=True)

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
    similarity = max(0, 100 - np.linalg.norm(np.array(inputs) - np.array(data)) * 10)

    # institutional memory trend
    if len(st.session_state.macro_memory) > 5:
        past_inputs = st.session_state.macro_memory[-5]["inputs"]
        past_similarity = max(0, 100 - np.linalg.norm(np.array(past_inputs) - np.array(data)) * 10)

        if similarity > past_similarity + 5:
            trend = "Increasing Similarity"
        elif similarity < past_similarity - 5:
            trend = "Diverging"
        else:
            trend = "Stable"
    else:
        trend = "Insufficient Data"

    comp_results.append({
        "Historical Event": name,
        "Similarity Score": f"{similarity:.1f}%",
        "Trend": trend
    })

st.table(pd.DataFrame(comp_results))

st.divider()
st.subheader("Export Data")

if st.session_state.macro_memory:
    # convert memory list to df
    export_df = pd.DataFrame([
        {
            "Timestamp": m["timestamp"],
            "US_CPI": m["inputs"][0],
            "EU_CPI": m["inputs"][1],
            "Asia_CPI": m["inputs"][2],
            "Liquidity_Stress": m["inputs"][3],
            "Semi_Cycle": m["inputs"][4],
            "Growth_Index": m["inputs"][5],
            "GDP_Nowcast": m["gdp"]
        } for m in st.session_state.macro_memory
    ])

    # download button
    csv = export_df.to_csv(index=False).encode('utf-8')
    
    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name=f"macro_intelligence_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    with col_dl2:
        st.caption("Export includes all captured snapshots for this session.")
else:

    st.info("No snapshots captured yet. Use the sidebar button to record data.")