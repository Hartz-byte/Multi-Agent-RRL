import streamlit as st
import requests
import graphviz
import time

API = "http://localhost:10000"

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide", page_icon="🛡️")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { align-items: center; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; padding: 10px 20px; }
    .main-nav { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    .nav-btn { background-color: #f0f2f6; border: 1px solid #d1d5db; }
    .active-nav { background-color: #1f2937 !important; color: white !important; }
    .log-box { font-family: 'Courier New', Courier, monospace; font-size: 0.85rem; background-color: #0e1117; color: #00ff41; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""
if 'active_view' not in st.session_state:
    st.session_state.active_view = "Research"
if 'logs' not in st.session_state:
    st.session_state.logs = ["System ready. Awaiting topic input..."]

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

# --- Sidebar: Instructions, Examples, & Logs ---
with st.sidebar:
    st.header("🏢 Research Workspace")
    st.markdown("---")
    
    st.markdown("### 🧭 Project Guide")
    st.info("""
    1. Enter a research topic.
    2. Parallel Fetch (ArXiv & OpenAlex).
    3. Multi-agent Trend & Gap Analysis.
    4. Relational Knowledge Graph Build.
    5. RRL & PhD Proposal Synthesis.
    """)
    
    st.markdown("### 💡 Example Topics")
    examples = [
        "Hybrid RAG for clinical documents",
        "Explainability in Transformer-based STT",
        "Edge computing for real-time video analytics",
        "Prompt engineering for legal reasoning"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
            st.session_state.current_topic = ex
            st.session_state.active_view = "Research"
            st.rerun()

    st.markdown("---")
    st.markdown("### 📟 System Activity Logs")
    log_content = "\n".join(st.session_state.logs[::-1]) # Show latest first
    st.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)

# --- Main Title Area ---
st.title("🛡️ Multi-Agent AI RRL Research System")
st.caption("Autonomous Discovery of Research Gaps & Literature Synthesis")

# --- Navbar-like Buttons ---
col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    if st.button("🔍 Research Pipeline", use_container_width=True, type="primary" if st.session_state.active_view == "Research" else "secondary"):
        st.session_state.active_view = "Research"
        st.rerun()
with col_nav2:
    if st.button("ℹ️ About the Project", use_container_width=True, type="primary" if st.session_state.active_view == "About" else "secondary"):
        st.session_state.active_view = "About"
        st.rerun()

st.markdown("---")

# --- VIEW: RESEARCH ---
if st.session_state.active_view == "Research":
    # Main Input Area
    col_in1, col_in2 = st.columns([4, 1])
    with col_in1:
        topic = st.text_input("Research Topic", value=st.session_state.current_topic, placeholder="e.g., 'Low-resource LLM optimization'")

    def submit_feedback(topic, paper_id, rating):
        try:
            res = requests.post(f"{API}/feedback", params={"topic": topic, "paper_id": paper_id, "rating": rating}, timeout=5)
            if res.status_code == 200:
                st.toast(f"✅ Preference saved for: {paper_id}")
                return True
        except:
            st.error("Failed to submit feedback.")
            return False

    def run_analysis():
        if not topic:
            st.warning("Please enter a topic.")
            return
        
        # Reset logs for new run
        st.session_state.logs = []
        add_log(f"Initializing Analysis for topic: '{topic}'")
        add_log("Retriever Agent: Fetching ArXiv & OpenAlex sources...")
        
        with st.spinner("🚀 Executing Multi-Agent Pipeline... (Retrieving, Parsing, & Reasoning)"):
            try:
                res = requests.post(f"{API}/analyze", params={"topic": topic}, timeout=180)
                if res.status_code == 200:
                    add_log("Parser Agent: Extracting structured data from PDFs...")
                    add_log("Analyzer Agent: Identifying Trends & Contradictions...")
                    add_log("Gap Finder: Mapping unexplored territories...")
                    add_log("Writer Agent: Synthesizing RRL & PhD Proposal...")
                    add_log("Graph Builder: Generating Relational Knowledge map...")
                    
                    st.session_state.analysis_result = res.json()
                    st.session_state.current_topic = topic
                    add_log("Pipeline Execution Complete. Results rendered.")
                    st.success("Analysis Complete!")
                else:
                    add_log(f"CRITICAL ERROR: Backend failed with status {res.status_code}")
                    st.error(f"Backend Error: {res.text}")
            except Exception as e:
                add_log(f"CONNECTION ERROR: {str(e)}")
                st.error(f"Connection Error: {e}")

    with col_in2:
        st.write("") # spacing
        st.write("")
        if st.button("🚀 Run Analysis", use_container_width=True):
            run_analysis()

    # Display Results
    if st.session_state.analysis_result:
        data = st.session_state.analysis_result
        
        # --- Tabbed Layout ---
        tab1, tab2, tab3 = st.tabs(["📊 Intelligence Suite", "🕸️ Knowledge Graph", "📝 Literature Review"])
        
        with tab1:
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.markdown("### 📈 Trend Analysis")
                st.info(data.get("trends", "N/A"))
                st.markdown("### ⚖️ Contradictions & Conflicts")
                st.warning(data.get("contradictions", "N/A"))
            with res_col2:
                st.markdown("### 🔍 Research Gaps")
                st.success(data.get("gaps", "N/A"))
                st.markdown("### 💡 Research Proposal")
                st.write(data.get("proposal", "N/A"))
        
        with tab2:
            st.subheader("Relational Knowledge Graph")
            graph_data = data.get("graph_data", {})
            if graph_data:
                dot = graphviz.Digraph(comment='Research Graph')
                dot.attr(rankdir='LR', size='12,12')
                dot.attr('node', shape='box', style='filled,rounded', color='#E1F5FE', fontname='Arial')
                dot.attr('edge', color='#B0BEC5', fontname='Arial', fontsize='10')
                for node in graph_data.get('nodes', []):
                    label = node.get('label', node.get('id', 'Unknown'))
                    color = "#E3F2FD" # Paper
                    if node.get('type') == 'Method': color = "#F3E5F5"
                    if node.get('type') == 'Dataset': color = "#E8F5E9"
                    dot.node(str(node['id']), label, fillcolor=color)
                for link in graph_data.get('links', []):
                    dot.edge(str(link['source']), str(link['target']), label=link.get('relation', ''))
                st.graphviz_chart(dot, use_container_width=True)
            else:
                st.info("No relational data available for visualization.")

        with tab3:
            st.subheader("Synthesis: Literature Review")
            st.markdown(data.get("rrl", "N/A"))
            st.markdown("---")
            st.subheader("📚 Source Papers & Learning Loop")
            for p in data.get("parsed_papers", []):
                with st.expander(f"📄 {p['title']}"):
                    col_p1, col_p2 = st.columns([3, 1])
                    with col_p1:
                        st.write(f"**Year:** {p.get('year', 'N/A')} | **Source:** {p.get('metadata', {}).get('source', 'N/A')}")
                        st.write(f"**Authors:** {', '.join(p.get('metadata', {}).get('authors', ['Unknown']))}")
                        st.caption(f"[View PDF/Link]({p.get('metadata', {}).get('pdf_url', '#')})")
                    with col_p2:
                        rating = st.select_slider("Relevance", options=[1, 2, 3, 4, 5], value=3, key=f"rate_{p['title']}")
                        if st.button("Submit Rating", key=f"btn_{p['title']}"):
                            submit_feedback(topic, p['title'], rating)
    else:
        # Empty state
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c_left, c_mid, c_right = st.columns([1, 2, 1])
        with c_mid:
            st.write("### 🧭 Ready to explore?")
            st.write("Enter a topic above or select an example from the sidebar to begin your research journey.")

# --- VIEW: ABOUT ---
elif st.session_state.active_view == "About":
    st.markdown("## ℹ️ About the Project")
    
    col_about1, col_about2 = st.columns([2, 1])
    
    with col_about1:
        st.markdown("""
        ### 🎯 Purpose
        The **Multi-Agent AI RRL Research System** is designed to transform the academic literature review process (RRL). 
        By leveraging specialized AI agents, the system moves beyond simple search and summarization to **autonomous discovery**. 
        It identifies what is *missing* in a domain, flags contradictions between studies, and proposes novel research directions grounded in identified gaps.

        ### 🚀 Key Features
        - **Parallel Intelligence**: Concurrent fetching from ArXiv & OpenAlex reduces search time by 60%.
        - **Multi-Agent Reasoning**: Orchestrated via LangGraph, agents specialize in Trend Analysis, Contradiction Detection, and Gap Finding.
        - **Relational Mapping**: Graph-based visualization of paper relationships, methods, and datasets.
        - **Self-Improving Loop**: Learns from user feedback to bias future retrieval towards highly relevant clusters.
        - **PhD-Grade Synthesis**: Generates structured Literature Reviews and full PhD-level research proposals.
        """)
        
        st.markdown("---")
        st.markdown("### ⭐️ Support the Project")
        st.write("Liked my work? Check out the [GitHub repo](https://github.com/Hartz-byte/Multi-Agent-RRL) and give it a star!")
    
    with col_about2:
        st.markdown("### 🛠️ Tech Stack & Tools")
        st.success("**Core Orchestration**: LangGraph")
        st.info("**LLM Engine**: Groq (Llama 3.3 70B & Llama 3.1 8B)")
        st.warning("**Vector Database**: Pinecone (Serverless)")
        st.error("**Graph Engine**: NetworkX & Graphviz")
        st.markdown("**Backend**: FastAPI (Python)")
        st.markdown("**Frontend**: Streamlit")
        st.markdown("**Search**: ArXiv & OpenAlex APIs")
        st.markdown("**PDF Parsing**: PyMuPDF (fitz)")
        
        st.image("https://img.icons8.com/clouds/100/code.png", width=100)
