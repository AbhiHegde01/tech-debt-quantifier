import streamlit as st
import requests
import graphviz

# Must be the first Streamlit command
st.set_page_config(page_title="Tech Debt Engine", page_icon="🚀", layout="wide")

# --- CUSTOM CSS FOR AESTHETICS ---
st.markdown("""
<style>
    /* Glow effect for main title */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #00A3FF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    /* Subtitle styling */
    .sub-title {
        text-align: center;
        color: #888888;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    /* Make metric numbers massive and bold */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 900 !important;
        color: #00A3FF !important;
    }
    /* Style the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- UI HEADER ---
st.markdown('<div class="main-title">Tech Debt Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Quantify architecture, map blast radiuses, and translate bad code into business metrics.</div>', unsafe_allow_html=True)

# Memory State
if "api_data" not in st.session_state:
    st.session_state.api_data = None

# --- SEARCH BAR ---
col_space1, col_search, col_space2 = st.columns([1, 2, 1])
with col_search:
    repo_url = st.text_input("Enter Public GitHub URL:", "https://github.com/tiangolo/fastapi", label_visibility="collapsed")
    analyze_pressed = st.button("🚀 Analyze Codebase", use_container_width=True, type="primary")

# --- EXECUTION LOGIC ---
if analyze_pressed:
    with st.spinner("Cloning repository, mapping dependencies, and running AI analysis..."):
        try:
            res = requests.post("http://localhost:8000/analyze-repo", json={"github_url": repo_url})
            
            if res.status_code != 200:
                st.error(f"Backend Error: {res.text}")
            else:
                st.session_state.api_data = res.json()
                st.balloons() # The Catchy Flair!
        except Exception as e:
            st.error(f"Failed to connect to the backend server. Error: {e}")

# --- DASHBOARD RENDER ---
if st.session_state.api_data:
    data = st.session_state.api_data

    st.divider()

    # TOP ROW: Executive Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Tech Debt Score", f"{data.get('technical_debt_score', '?')}/10")
    col2.metric("Remediation Time", f"{data.get('remediation_cost_hours', '?')} hrs")
    col3.metric("Priority Level", str(data.get('priority', '?')).upper())

    st.write("") # Spacer

    # MIDDLE ROW: Interactive Tabs
    tab_ai, tab_graph, tab_metrics = st.tabs(["🤖 AI Architect Insights", "🕸️ Blast Radius Graph", "📊 Raw Code Metrics"])

    with tab_ai:
        st.subheader("Architectural Review")
        st.markdown(f"**Primary Offender:** `{data.get('analyzed_file', 'Unknown')}`")
        
        st.info(f"**Business Impact:** {data.get('business_impact', {}).get('expense', 'N/A')}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Improvement Areas:**")
            for item in data.get('improvement_areas', []):
                st.markdown(f"- {item}")
        with col_b:
            st.write("**Efficient Replacements:**")
            for rep in data.get('efficient_replacements', []):
                st.markdown(f"- `{rep}`")

    with tab_graph:
        st.subheader("Dependency Network (Core Architecture)")
        st.caption("Note: Graph is limited to 35 core files to prevent browser memory overload.")
        
        if "blast_radius" in data and data["blast_radius"]:
            graph = graphviz.Digraph()
            graph.attr(rankdir='LR', size='12,8', bgcolor='transparent') 
            
            safe_radius = dict(list(data["blast_radius"].items())[:35])
            
            for file, imports in safe_radius.items():
                graph.node(file, shape='box', style='filled', fillcolor='#1E1E1E', fontcolor='white', color='#00A3FF')
                for imp in imports[:3]:
                    graph.edge(file, imp, color='#444444')
                    
            st.graphviz_chart(graph, use_container_width=True) 
        else:
            st.info("No dependencies found to graph.")

    with tab_metrics:
        st.subheader("Static Analysis Results (Lizard Engine)")
        if "static_metrics" in data:
            st.metric("Peak Cyclomatic Complexity", data["static_metrics"]["cyclomatic_complexity_score"])
            st.caption(f"File analyzed: {data['static_metrics']['worst_file']}")
            st.markdown("*Note: A cyclomatic complexity over 15 is highly prone to bugs. Over 30 is unmaintainable.*")
        else:
            st.info("Static metrics not returned by backend.")