import streamlit as pd, pandas as pd, requests, time, streamlit as st

st.set_page_config(page_title="ResQ-TO-MoE Command Center", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<style>@import url('https://googleapis.com'); .stApp { background-color: #060913; color: #cbd5e1; font-family: 'Share Tech Mono', monospace; } .hud-header { border: 1px solid #1e293b; background: linear-gradient(90deg, #0f172a 0%, #020617 100%); padding: 15px; border-radius: 4px; border-left: 4px solid #06b6d4; } .matrix-cell { background: #0b0f19; border: 1px solid #1e293b; padding: 18px; margin-bottom: 12px; } .cell-tag { font-size: 11px; color: #64748b; text-transform: uppercase; } .cell-val { font-size: 24px; color: #f8fafc; font-weight: bold; } .expert-title { font-size: 14px; color: #38bdf8; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #1e293b; } .telemetry-log { font-size: 12px; color: #94a3b8; line-height: 1.5; }</style>", unsafe_allow_html=True)

def profile_difficulty(text):
    text_l = text.lower()
    weights = {"earthquake": 3.0, "rupture": 2.5, "trapped": 2.5, "toxic": 2.0, "ganga": 2.0}
    score = 1.0
    for word, wt in weights.items():
        if word in text_l: score += wt
    return min(int(score), 10)

st.markdown('<div class="hud-header"><div style="color:#06b6d4; font-size:22px; font-weight:bold; letter-spacing:2px;">ResQ-TO-MoE // Tactical Operations Command Center</div><div style="font-size:11px; color:#64748b;">MULTI-SERVICE CONTAINER INFRASTRUCTURE ARCHITECTURE</div></div>', unsafe_allow_html=True)
col_l, col_r = st.columns()

with col_l:
    st.markdown('<div class="matrix-cell"><div class="cell-tag">Telemetry Ingress Log Feed</div></div>', unsafe_allow_html=True)
    input_text = st.text_area("Context", "CRITICAL EMERGENCY FEED: A massive 7.8 magnitude earthquake has hit an industrial sector bordering the upper Ganga river basin. Main bridge routes 4 and 9 have completely collapsed, blocking all vehicle ingress. Concurrently, a secondary chemical fertilizer facility has ruptured, leaking toxic methyl isocyanate gas into the atmosphere and liquid residue into the water supply. Thermal imaging confirms over 150 workers are trapped in subsurface structural basements with rising water levels, experiencing immediate respiratory failure. Airborne toxicity vectors are moving eastward toward high-density residential grids.", height=165, label_visibility="collapsed")
    execute_pipeline = st.button("⚡ INITIATE DYNAMIC MULTI-SERVICE ROUTING MATRIX")

with col_r:
    st.markdown('<div class="matrix-cell"><div class="cell-tag">Test-Time Compute Search Allocation Function Curve</div></div>', unsafe_allow_html=True)
    st.line_chart(pd.DataFrame({"Complexity Vector (c_t)": list(range(1, 11)), "Reasoning Loop Search Budget (L_i)": [x * 2 for x in range(1, 11)]}), y="Reasoning Loop Search Budget (L_i)", x="Complexity Vector (c_t)", height=155)

if execute_pipeline:
    c_t = profile_difficulty(input_text)
    L_i = c_t * 2
    workers = ["hazmat", "logistics", "medical"] if c_t >= 6 else ["logistics"]
    
    st.markdown('<div class="matrix-cell"><div class="cell-tag">Structural Vector Matrix Allocation Analysis</div></div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    g1.markdown(f'<div class="matrix-cell"><div class="cell-tag">Complexity Vector (c_t)</div><div class="cell-val" style="color:#ef4444;">{c_t}.00</div></div>', unsafe_allow_html=True)
    g2.markdown(f'<div class="matrix-cell"><div class="cell-tag">Allocated Loops (L_i)</div><div class="cell-val" style="color:#38bdf8;">{L_i}</div></div>', unsafe_allow_html=True)
    g3.markdown(f'<div class="matrix-cell"><div class="cell-tag">Active Containers</div><div class="cell-val" style="color:#06b6d4;">0{len(workers)}</div></div>', unsafe_allow_html=True)

    # SECURE INTER-CONTAINER RPC CALL TO NODE.JS BACKEND
    # Zerops handles private host resolution automatically inside the cluster mesh
    backend_rpc_url = "http://moe-backend:3000/api/compute-moe"
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY", "")
    
    try:
        response = requests.post(backend_rpc_url, json={"report": input_text, "loops": L_i, "workers": workers, "api_key": openrouter_key}, timeout=15)
        cluster_data = response.json()
        
        st.markdown('<div class="matrix-cell"><div class="cell-tag">Asynchronous Heterogeneous Parallel Execution Pipeline Layer</div></div>', unsafe_allow_html=True)
        cols = st.columns(len(workers))
        for idx, w in enumerate(workers):
            with cols[idx]:
                st.markdown(f'<div class="expert-title">🛡️ Service Node // {w.upper()}</div>', unsafe_allow_html=True)
                st.markdown(f"<div class='telemetry-log'>{cluster_data['mesh_traces'][w]}</div>", unsafe_allow_html=True)
                
        st.markdown(f'<div style="border:1px solid #10b981; background:rgba(16,185,129,0.03); padding:20px; border-left:5px solid #10b981; margin-top:20px;"><div style="color:#10b981; font-size:14px; font-weight:bold; text-transform:uppercase;">Information Aggregation Matrix Output (y_t)</div><div style="font-size:14px; color:#e2e8f0; line-height:1.6; margin-top:8px;">[OPTIMAL_FRONTIER_SOLUTION_CONVERGENCE]: DATA TELEMETRY PROCESSED FROM DUAL-RUNTIME ZEROPS RECTOR CELL. MASTER PROTOCOL DEPLOYED FOR GANGA BASIN SECTOR SEVERITY LEVEL {c_t}.</div></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Private Network Pipeline Disconnected. Error: {e}")
