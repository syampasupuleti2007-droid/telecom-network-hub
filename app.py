import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
from datetime import datetime

# Import Python Analytics Engine
try:
    from python_analytics.dbms_algebra import link_complaints_to_infrastructure
    from python_analytics.churn_predictor import ChurnPredictor
except ImportError:
    # Fallback dummy functions if local modules aren't found
    def link_complaints_to_infrastructure(sub, cmp):
        return pd.DataFrame()
    class ChurnPredictor:
        def predict_churn_prob(self, c, o, u):
            return 0.45

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Telecom Network & Analytics Engine",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- OPERATIONS CONSOLE THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f4f7fb;
        --surface: #ffffff;
        --surface-strong: #eef5ff;
        --line: #dfe8f3;
        --text: #14233b;
        --text-muted: #5f6f89;
        --primary: #0f6fff;
        --primary-deep: #0a4fc7;
        --secondary: #14b8a6;
        --warning: #f59e0b;
        --danger: #ef4444;
        --success: #10b981;
        --sidebar: #0b1220;
        --sidebar-soft: rgba(255,255,255,0.08);
        --shadow: 0 14px 34px rgba(9, 25, 48, 0.08);
    }

    header[data-testid="stHeader"] {
        background: rgba(244, 247, 251, 0.8) !important;
        backdrop-filter: blur(12px);
    }

    .main .block-container {
        max-width: 1500px;
        padding: 2rem 2.25rem 3rem !important;
    }

    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, #eff5fb 100%) !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1220 0%, #111b2c 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
        box-shadow: 14px 0 28px rgba(7, 15, 27, 0.12);
    }

    [data-testid="stSidebar"] * {
        color: #eaf2ff !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #b7d7ff !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.035em !important;
        font-weight: 800 !important;
    }

    h1 {
        font-size: clamp(2.4rem, 3vw, 3.2rem) !important;
        line-height: 1.1 !important;
        margin-bottom: 0.35rem !important;
    }

    h2, h3 { font-weight: 700 !important; }

    p, span, .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--text-muted) !important;
    }

    .stMarkdown p { line-height: 1.6; }
    hr { border-color: var(--line) !important; }

    label, label p, label span {
        color: var(--text) !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    input {
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid #c7d4e6 !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] *,
    div[data-baseweb="input"] * {
        color: var(--text) !important;
    }

    ul[data-baseweb="menu"] {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 10px !important;
    }

    ul[data-baseweb="menu"] li {
        color: var(--text) !important;
    }

    div[data-testid="stForm"],
    .stBorderContainer,
    div[data-testid="stMetric"] {
        border-radius: 18px !important;
        border: 1px solid var(--line) !important;
        background: rgba(255,255,255,0.9) !important;
        box-shadow: var(--shadow);
        padding: 1.1rem !important;
    }

    div[data-testid="stMetric"] {
        min-height: 120px;
        border-top: 3px solid var(--primary) !important;
    }

    div[data-testid="stMetric"]:nth-child(3n) {
        border-top-color: var(--secondary) !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em !important;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background: transparent !important;
        border-radius: 10px 10px 0 0 !important;
        border: 0 !important;
        padding: 0 14px !important;
    }

    .stTabs [data-baseweb="tab"] p {
        color: var(--text-muted) !important;
        font-weight: 700 !important;
    }

    .stTabs [aria-selected="true"] {
        background: #e7f0ff !important;
        box-shadow: inset 0 -3px 0 var(--primary);
    }

    .stTabs [aria-selected="true"] p {
        color: var(--primary-deep) !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 22px rgba(20, 35, 59, 0.04);
    }

    code {
        color: var(--primary-deep) !important;
        background: #edf5ff !important;
        border: 1px solid #cfe1ff !important;
        border-radius: 6px !important;
    }

    .stButton > button,
    .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"] {
        min-height: 42px;
        border-radius: 10px;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: #ffffff !important;
        border: none !important;
        transition: transform 160ms ease, box-shadow 160ms ease;
        box-shadow: 0 10px 18px rgba(15, 111, 255, 0.2);
    }

    .stButton > button * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    .stButton > button:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 20px rgba(15, 111, 255, 0.24);
    }

    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #dfeeff 0%, #c8ebff 100%) !important;
        color: var(--text) !important;
        border: none !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%) !important;
        box-shadow: 0 10px 18px rgba(245, 158, 11, 0.2);
    }

    [data-testid="stSlider"] [data-baseweb="slider"] {
        padding: 0.7rem 0 0.9rem;
    }

    [data-testid="stSlider"] [role="slider"] {
        width: 20px !important;
        height: 20px !important;
        background: #ffffff !important;
        border: 3px solid var(--primary) !important;
        box-shadow: 0 4px 12px rgba(15, 111, 255, 0.18) !important;
    }

    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background: #dfeaf8 !important;
        height: 7px !important;
        border-radius: 99px !important;
    }

    [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        height: 7px !important;
        border-radius: 99px !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] {
        border-color: var(--line) !important;
        border-radius: 12px !important;
    }

    .success-animation {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.9rem 1rem;
        margin: 0.6rem 0 1rem;
        border-radius: 14px;
        border: 1px solid #b7f0d4;
        background: linear-gradient(135deg, #ecfdf5 0%, #f2fff9 100%);
        box-shadow: 0 12px 24px rgba(16, 185, 129, 0.12);
        animation: successSlideIn 0.4s ease-out;
    }

    .success-badge {
        display: grid;
        place-items: center;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        box-shadow: 0 0 0 8px rgba(52, 211, 153, 0.14);
        animation: successPulse 0.8s ease-out;
    }

    .success-animation-title {
        color: #065f46 !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }

    .success-animation-subtitle {
        color: #047857 !important;
        font-size: 0.82rem !important;
        margin-top: 2px !important;
    }

    @keyframes successPulse {
        0% { transform: scale(0.6); opacity: 0; }
        65% { transform: scale(1.12); opacity: 1; }
        100% { transform: scale(1); }
    }

    @keyframes successSlideIn {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 900px) {
        .main .block-container { padding: 1.2rem 1rem 2rem !important; }
        h1 { font-size: 2rem !important; }
    }
    </style>
""", unsafe_allow_html=True)


def render_success_animation(title, subtitle="Request processed successfully"):
    st.markdown(
        f"""
        <div class="success-animation">
            <div class="success-badge">✓</div>
            <div>
                <div class="success-animation-title">{title}</div>
                <div class="success-animation-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- INITIALIZE SESSION STATE ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "main_dashboard"

if "show_submit_success" not in st.session_state:
    st.session_state.show_submit_success = False

if "complaint_history" not in st.session_state:
    st.session_state.complaint_history = pd.DataFrame({
        "complaint_id": ["CMP01", "CMP02", "CMP03", "CMP04"],
        "subscriber_id": ["SUB001", "SUB002", "SUB004", "SUB005"],
        "tower_id_complaint": ["Tower_A", "Tower_B", "Tower_A", "Tower_B"],
        "outage_hours": [14.5, 2.0, 18.0, 1.0],
        "usage_drop_pct": [50, 10, 65, 5],
        "complaint_date": ["2026-03-01", "2026-03-02", "2026-03-02", "2026-03-03"],
        "name": ["Student_01", "Student_02", "Student_04", "Student_05"],
        "plan_type": ["Premium_Unlimited", "Basic_Data", "Premium_Unlimited", "Basic_Data"],
        "tower_id_subscriber": ["Tower_A", "Tower_B", "Tower_A", "Tower_B"],
        "monthly_bill": [49, 29, 49, 29]
    })

# --- BACKEND INITIALIZATION ---
@st.cache_resource
def load_churn_predictor():
    return ChurnPredictor()

@st.cache_resource
def build_telecom_network():
    G = nx.DiGraph()
    towers = [f"Tower_{i:02d}" for i in range(1, 21)]
    substations = ["Substation_01", "Substation_02", "Substation_03", "Substation_04"]
    central_hub = "Central_Hub"
    
    G.add_nodes_from(towers + substations + [central_hub])

    for i in range(1, 6):
        status = "FAULT_DISRUPT" if i == 2 else "OK"
        G.add_edge(f"Tower_{i:02d}", "Substation_01", status=status, link_id=f"L10{i}")

    for i in range(6, 11):
        status = "DEGRADED" if i == 8 else "OK"
        G.add_edge(f"Tower_{i:02d}", "Substation_02", status=status, link_id=f"L1{i:02d}")

    for i in range(11, 16):
        G.add_edge(f"Tower_{i:02d}", "Substation_03", status="OK", link_id=f"L1{i:02d}")

    for i in range(16, 21):
        status = "FAULT_DISRUPT" if i == 19 else "OK"
        G.add_edge(f"Tower_{i:02d}", "Substation_04", status=status, link_id=f"L1{i:02d}")

    G.add_edge("Substation_01", central_hub, status="FAULT_DISRUPT", link_id="L_SUB_01")
    G.add_edge("Substation_02", central_hub, status="OK", link_id="L_SUB_02")
    G.add_edge("Substation_03", central_hub, status="OK", link_id="L_SUB_03")
    G.add_edge("Substation_04", central_hub, status="DEGRADED", link_id="L_SUB_04")

    return G

def trace_fault_path(graph, start_tower, target_hub="Central_Hub"):
    if not nx.has_path(graph, start_tower, target_hub):
        return None, ["No physical path connected to Central Hub."]
    
    path = nx.shortest_path(graph, start_tower, target_hub)
    faults = []
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        edge_data = graph.get_edge_data(u, v)
        if edge_data["status"] != "OK":
            faults.append(f"Link {edge_data['link_id']} ({u} ➔ {v}): Status '{edge_data['status']}'")
            
    return path, faults

def render_network_graph(graph, highlight_path=None):
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#161B22")
    ax.set_facecolor("#161B22")

    pos = nx.spring_layout(graph, seed=42)

    towers = [n for n in graph.nodes if n.startswith("Tower_")]
    substations = [n for n in graph.nodes if n.startswith("Substation_")]
    central_hub = ["Central_Hub"]

    nx.draw_networkx_nodes(graph, pos, nodelist=towers, node_color="#38BDF8", node_size=350, label="Cell Towers (20)", ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=substations, node_color="#F59E0B", node_size=700, label="Substations (4)", ax=ax)
    nx.draw_networkx_nodes(graph, pos, nodelist=central_hub, node_color="#10B981", node_size=1200, label="Central Hub", ax=ax)

    edge_colors = []
    for u, v, d in graph.edges(data=True):
        if d.get("status") == "FAULT_DISRUPT":
            edge_colors.append("#F87171")
        elif d.get("status") == "DEGRADED":
            edge_colors.append("#FBBF24")
        else:
            edge_colors.append("#6B7280")

    nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=2.0, alpha=0.8, ax=ax)

    if highlight_path:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color="#22D3EE", width=4.0, ax=ax)
        nx.draw_networkx_nodes(graph, pos, nodelist=highlight_path, node_color="#22D3EE", node_size=550, ax=ax)

    nx.draw_networkx_labels(
        graph, pos, 
        font_color="#FFFFFF", 
        font_size=8, 
        font_weight="bold", 
        font_family="sans-serif", 
        ax=ax
    )

    ax.legend(facecolor="#0D1117", edgecolor="#30363D", labelcolor="white", loc="upper left")
    plt.axis("off")
    plt.tight_layout()
    return fig

# Initialize System Objects
network_graph = build_telecom_network()
churn_engine = load_churn_predictor()
tower_list = [node for node in network_graph.nodes if node.startswith("Tower_")]
subscriber_list = [f"SUB{i:03d}" for i in range(1, 151)]

# ==========================================
# PAGE ROUTING SYSTEM
# ==========================================

if st.session_state.current_page == "lodge_complaint_page":
    st.title("🚨 Emergency Complaint Registration Portal")
    st.caption("Submit customer service incident ticket to execute path tracing and machine learning churn prediction.")
    st.divider()

    with st.container(border=True):
        st.markdown("### 📝 Incident Entry Form")
        
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            input_sub = st.selectbox("Select Subscriber ID:", subscriber_list)
            input_tower = st.selectbox("Connected Cell Tower Node:", tower_list)
            input_outage = st.number_input("Experienced Outage Hours:", min_value=0.5, max_value=72.0, value=12.0, step=0.5)

        with col2:
            input_drop = st.slider("Estimated Data Usage Drop Rate (%):", 0, 100, 50)
            st.markdown("**Automated Backend Triggers:**")
            st.write("• **DBMS:** Appends record to relational algebra table.")
            st.write("• **ADSA Graph:** Traces link faults from target tower to Central Hub.")
            st.write("• **ML Engine:** Computes immediate churn probability score.")

        st.divider()
        col_sub, col_cancel = st.columns([1, 1])

        with col_sub:
            if st.button("Submit Complaint & Process", type="primary", use_container_width=True):
                new_id = f"CMP{len(st.session_state.complaint_history) + 1:02d}"
                new_entry = {
                    "complaint_id": new_id,
                    "subscriber_id": input_sub,
                    "tower_id_complaint": input_tower,
                    "outage_hours": input_outage,
                    "usage_drop_pct": input_drop,
                    "complaint_date": datetime.now().strftime("%Y-%m-%d"),
                    "name": "User_Entry",
                    "plan_type": "Standard",
                    "tower_id_subscriber": input_tower,
                    "monthly_bill": 39
                }
                st.session_state.complaint_history = pd.concat(
                    [pd.DataFrame([new_entry]), st.session_state.complaint_history],
                    ignore_index=True
                )

                prob = churn_engine.predict_churn_prob(1, input_outage, input_drop)
                st.session_state.show_submit_success = True
                st.session_state.submit_success_message = (
                    f"Complaint {new_id} successfully registered! Subscriber {input_sub} churn risk recalculated at {round(prob * 100, 2)}%"
                )
                render_success_animation(
                    f"Complaint {new_id} successfully registered!",
                    f"Subscriber {input_sub} churn risk recalculated at {round(prob * 100, 2)}%"
                )
                st.info(f"📊 Recalculated Subscriber `{input_sub}` Churn Risk: **{round(prob * 100, 2)}%**")
                
                time.sleep(1.6)
                st.session_state.current_page = "main_dashboard"
                st.rerun()

        with col_cancel:
            if st.button("Cancel & Return to Dashboard", use_container_width=True):
                st.session_state.current_page = "main_dashboard"
                st.rerun()

else:
    # --- HIGH-CONTRAST SIDEBAR CONTROL PANEL ---
    with st.sidebar:
        st.markdown("## 📡 **Control Center**")
        st.caption("Network Operations & Analytics")
        st.divider()

        st.markdown("### 🎛️ Diagnostic Testing")
        selected_tower = st.selectbox("Select Target Tower Node:", tower_list, index=0)
        sim_complaints = st.slider("Simulate Complaints:", 0, 10, 4)
        sim_outage = st.slider("Outage Hours:", 0.0, 48.0, 14.5)
        sim_usage_drop = st.slider("Usage Drop (%):", 0, 100, 50)
        
        st.divider()
        st.caption("📍 JNTUK R23 - B.Tech AI & DS (2025 Batch)")

    if st.session_state.get("show_submit_success", False):
        render_success_animation(
            "Submission complete",
            st.session_state.get("submit_success_message", "Complaint processed successfully.")
        )
        st.session_state.show_submit_success = False

    # --- TOP HEADER BANNER ---
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;margin-bottom:18px;'>"
        "<span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:#10b981;box-shadow:0 0 0 6px rgba(16,185,129,0.12);'></span>"
        "<span style='font-size:0.78rem;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#0f6fff;'>Operations Command Center</span>"
        "<span style='color:#73839a;font-size:0.8rem;'>Updated just now</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.title("Telecom Network Intelligence Platform")
    st.caption("Enterprise monitoring, path tracing, and churn risk intelligence for modern telecom operations.")
    st.divider()

    # --- TOP NAVIGATION TABS ---
    tab_overview, tab_topology, tab_analytics, tab_architecture, tab_dbms = st.tabs([
        "📊 Executive Dashboard",
        "🗺️ Network Topology & Fault Tracer",
        "📈 Predictive Churn Engine",
        "💻 Enterprise Stack Architecture",
        "🗄️ DBMS Relational Operations"
    ])

    # --- TAB 1: EXECUTIVE DASHBOARD ---
    with tab_overview:
        header_col, action_col = st.columns([3, 1])
        with header_col:
            st.subheader("🌐 Global Network Overview & Operational Hub")
        with action_col:
            if st.button("🚨 Lodge Complaint Now", use_container_width=True):
                st.session_state.current_page = "lodge_complaint_page"
                st.rerun()

        st.markdown("---")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Cell Towers", "20 Nodes", delta="100% Operational")
        m2.metric("Subscribers", "150 Members", delta="Batch Cohort")
        m3.metric("Filed Tickets", f"{len(st.session_state.complaint_history)} Total", delta="+1 Logged")
        m4.metric("Network Links", f"{len(network_graph.edges)} Edges", delta="3 Disrupted", delta_color="inverse")
        m5.metric("Network Health", "88.4%", delta="-3.2% Downtime", delta_color="inverse")

        st.markdown("---")

        col_map, col_log = st.columns([1.6, 1], gap="large")

        with col_map:
            st.markdown("### 📡 Live Topology Health Map")
            fig = render_network_graph(network_graph)
            st.pyplot(fig, use_container_width=True)

        with col_log:
            st.markdown("### 📋 Complaint Audit Register")
            st.dataframe(st.session_state.complaint_history, use_container_width=True, hide_index=True)

    # --- TAB 2: NETWORK TOPOLOGY & FAULT TRACER ---
    with tab_topology:
        st.subheader("🗺️ Graph Traversal & Fault Isolation (ADSA Unit 2)")

        col_map, col_controls = st.columns([2, 1], gap="large")
        path, faults = trace_fault_path(network_graph, selected_tower, "Central_Hub")

        with col_controls:
            st.markdown("### 🔍 Path Isolation Results")
            with st.container(border=True):
                st.write(f"**Origin Tower Node:** `{selected_tower}`")
                st.write(f"**Target Central Hub:** `Central_Hub`")
                st.divider()

                if path:
                    st.success("✅ Path Identified")
                    st.write("**Traversal Graph Path:**")
                    st.code(" ➔ ".join(path))

                if faults:
                    st.error("🚨 Active Link Disruptions:")
                    for fault in faults:
                        st.write(f"• {fault}")
                else:
                    st.success("🟢 All connected links operating normally.")

        with col_map:
            st.markdown("### 🌐 Dynamic Network Fault Path Map")
            fig_path = render_network_graph(network_graph, highlight_path=path)
            st.pyplot(fig_path, use_container_width=True)

    # --- TAB 3: PREDICTIVE CHURN ENGINE ---
    with tab_analytics:
        st.subheader("📈 Machine Learning Churn Engine (Python)")

        col_input, col_output = st.columns([1, 1], gap="large")

        with col_input:
            with st.container(border=True):
                st.markdown("### 🧮 Subscriber Churn Score Calculation")
                st.write(f"• **Filed Complaints:** `{sim_complaints}`")
                st.write(f"• **Downtime Hours:** `{sim_outage} Hours`")
                st.write(f"• **Usage Drop Rate:** `{sim_usage_drop}%`")

                prob = churn_engine.predict_churn_prob(sim_complaints, sim_outage, sim_usage_drop)
                churn_pct = round(prob * 100, 2)

                st.divider()
                st.metric("Output Churn Probability Score (`churn_prob`)", f"{churn_pct}%")

                if churn_pct >= 65.0:
                    st.error("🔴 **HIGH RISK:** Triggering automated Java retention manager workflow.")
                elif churn_pct >= 30.0:
                    st.warning("🟡 **MODERATE RISK:** Queued for service notification.")
                else:
                    st.success("🟢 **LOW RISK:** Customer relationship stable.")

        with col_output:
            st.markdown("### 📊 Cohort Risk Tier Breakdown (150 Members)")
            cohort_counts = pd.DataFrame({
                "Risk Tier": ["Low Risk (<30%)", "Moderate Risk (30-65%)", "High Risk (>65%)"],
                "Subscribers": [95, 35, 20]
            }).set_index("Risk Tier")
            st.bar_chart(cohort_counts, color="#38BDF8")

    # --- TAB 4: ARCHITECTURE ---
    with tab_architecture:
        st.subheader("💻 Enterprise Architecture & Subject Mapping")

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            with st.container(border=True):
                st.markdown("### ☕ Java Logic Core (`java_backend/`)")
                st.divider()
                st.write("• **`SubscriberApp.java`**: Object models for 150 subscriber base.")
                st.write("• **`FaultPathTracer.java`**: Implements shortest path graph traversal.")
                st.write("• **`RetentionManager.java`**: Handles high-churn priority queues.")

        with col2:
            with st.container(border=True):
                st.markdown("### 🐍 Python Analytics Engine (`python_analytics/`)")
                st.divider()
                st.write("• **`dbms_algebra.py`**: Executes relational join logic on tables.")
                st.write("• **`churn_predictor.py`**: Scikit-Learn Logistic Regression pipeline.")
                st.write("• **`app.py`**: Interactive Streamlit web interface.")

    # --- TAB 5: DBMS OPERATIONS ---
    with tab_dbms:
        st.subheader("🗄️ Relational Algebra Engine (DBMS Unit 2)")
        st.caption("Interactive Execution of Fundamental Relational Operators: Selection (σ), Projection (π), and Natural Join (⋈)")

        dbms_tab1, dbms_tab2, dbms_tab3 = st.tabs([
            "📊 Interactive Operator Simulator (σ, π)", 
            "🔗 Multi-Table Natural Join (⋈)", 
            "📘 Formal Relational Notations"
        ])

        # SUB-TAB 1: INTERACTIVE SELECTION & PROJECTION ENGINE
        with dbms_tab1:
            st.markdown("### 1. Dynamic Query Processing Engine")
            
            col_op1, col_op2 = st.columns(2, gap="medium")
            
            with col_op1:
                with st.container(border=True):
                    st.markdown(r"#### **Selection Operator ($\sigma$)**")
                    min_outage_filter = st.slider(
                        r"Filter Outage Duration Threshold ($\sigma_{\text{Outage} \ge x}$):", 
                        min_value=0.0, 
                        max_value=48.0, 
                        value=1.0, 
                        step=0.5
                    )
                    
                    filtered_df = st.session_state.complaint_history[
                        st.session_state.complaint_history["outage_hours"] >= min_outage_filter
                    ]
                    st.code(f"σ_(outage_hours >= {min_outage_filter})(Complaint_Logs)", language="sql")

            with col_op2:
                with st.container(border=True):
                    st.markdown(r"#### **Projection Operator ($\pi$)**")
                    available_cols = list(st.session_state.complaint_history.columns)
                    selected_cols = st.multiselect(
                        r"Select Output Attributes ($\pi_{A_1, A_2, ...}$):", 
                        available_cols, 
                        default=["complaint_id", "subscriber_id", "tower_id_complaint", "outage_hours", "usage_drop_pct"]
                    )
                    
                    cols_str = ", ".join(selected_cols) if selected_cols else "ø"
                    st.code(f"π_({cols_str})(Filtered_Relation)", language="sql")

            st.divider()
            st.markdown("#### **Query Result Output**")
            
            if selected_cols:
                result_df = filtered_df[selected_cols]
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                
                m1, m2 = st.columns(2)
                m1.metric("Input Cardinality (|R|)", f"{len(st.session_state.complaint_history)} Tuples")
                m2.metric("Output Cardinality (|Result|)", f"{len(result_df)} Tuples")
            else:
                st.warning(r"⚠️ Please select at least one attribute to execute the Projection ($\pi$) operation.")

        # SUB-TAB 2: NATURAL JOIN OPERATIONS
        with dbms_tab2:
            st.markdown("### 2. Infrastructure Natural Join Execution")
            
            st.markdown(
                """
                <div style="background-color: #161B22; padding: 15px; border-radius: 8px; border: 1px solid #30363D; text-align: center; font-size: 1.2rem; font-weight: bold; color: #58A6FF; margin-bottom: 20px;">
                    Complaints &nbsp; ⋈<sub>Subscriber_ID</sub> &nbsp; Subscribers &nbsp; ⋈<sub>Tower_ID</sub> &nbsp; Infrastructure_Towers
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            sub_file = "data/subscribers.csv"
            cmp_file = "data/complaint_logs.csv"

            if os.path.exists(sub_file) and os.path.exists(cmp_file):
                joined_data = link_complaints_to_infrastructure(sub_file, cmp_file)
                st.dataframe(joined_data, use_container_width=True, hide_index=True)
            else:
                st.dataframe(st.session_state.complaint_history, use_container_width=True, hide_index=True)

        # SUB-TAB 3: MATHEMATICAL NOTATIONS & THEORY
        with dbms_tab3:
            st.markdown("### 3. JNTUK DBMS Unit 2 Formal Notations")
            
            c1, c2 = st.columns(2, gap="large")
            
            with c1:
                with st.container(border=True):
                    st.markdown("#### **Unary Relational Operators**")
                    st.write(r"**1. Selection ($\sigma$):** Retrieves tuple subsets satisfying predicate $P$.")
                    st.latex(r"\sigma_{P}(R) = \{ t \in R \mid P(t) \text{ is True} \}")
                    
                    st.write(r"**2. Projection ($\pi$):** Selects specified attribute columns $A_1, A_2, \dots, A_k$.")
                    st.latex(r"\pi_{A_1, A_2, \dots, A_k}(R)")

            with c2:
                with st.container(border=True):
                    st.markdown("#### **Binary Relational Operators**")
                    st.write("**1. Natural Join ($\bowtie$):** Combines tuples with matching common attributes.")
                    st.latex(r"R \bowtie S = \pi_{\text{Attrs}(R) \cup \text{Attrs}(S)}(\sigma_{R.A = S.A}(R \times S))")
                    
                    st.write("**2. Full Relational Query Pipeline:**")
                    st.latex(r"\pi_{\text{Sub\_ID}, \text{Tower\_ID}}(\sigma_{\text{Outage} > 10.0}(\text{Complaints} \bowtie \text{Subscribers}))")