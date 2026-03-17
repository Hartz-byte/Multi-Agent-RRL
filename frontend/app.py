import streamlit as st
import requests
import graphviz
import time
import os

# Use environment variable for API URL in production, default to localhost for development
API = os.getenv("BACKEND_URL", "http://localhost:10000")

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide", page_icon="🛡️")

# Custom CSS for Premium Look and Horizontal Radio
st.markdown("""
<style>
    /* Radio button styling to look like a navbar */
    div[data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 20px;
        background: transparent;
        padding: 5px 0;
    }
    div[role="radiogroup"] label {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-weight: 400 !important;
        color: #ffffff !important;
    }
    div[role="radiogroup"] label[data-baseweb="radio"] {
        padding-right: 20px !important;
    }
    
    /* Title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] { align-items: center; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; padding: 10px 20px; }
    .log-box { font-family: 'Courier New', Courier, monospace; font-size: 0.85rem; background-color: #0e1117; color: #00ff41; padding: 10px; border-radius: 5px; height: 300px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""
if 'logs' not in st.session_state:
    st.session_state.logs = ["System ready. Awaiting topic input..."]

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")

def check_connection():
    try:
        res = requests.get(f"{API}/", timeout=10)
        if res.status_code == 200:
            st.toast("✅ Backend is Online!")
            add_log("Connection Check: Backend is Online.")
            return True
        else:
            st.toast(f"⚠️ Backend returned status {res.status_code}", icon="⚠️")
            add_log(f"Connection Check: Unexpected status {res.status_code}")
            return False
    except Exception as e:
        st.toast("❌ Backend is Offline or Waking Up...", icon="❌")
        add_log(f"Connection Check: Offline ({str(e)})")
        return False

# --- Sidebar: Instructions, Examples, & Logs ---
with st.sidebar:
    # Render Note
    st.info(f"💡 **Note:** The backend gets inactive (Render Free Tier), click [here]({API}) to wake it up.")
    
    # Action Buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔌 Check Connection", use_container_width=True):
            check_connection()
    with col_btn2:
        if st.button("🗑️ Clear Result & Logs", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.logs = ["Logs cleared. System ready."]
            st.rerun()

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
            st.rerun()

    st.markdown("---")
    st.markdown("### 📟 System Activity Logs")
    log_content = "\n".join(st.session_state.logs[::-1]) # Show latest first
    st.markdown(f'<div class="log-box">{log_content}</div>', unsafe_allow_html=True)

# --- Header Area (Matching Screenshot) ---
st.markdown('<div class="main-title">Multi-Agent Research AI 🛡️</div>', unsafe_allow_html=True)

# Navbar using st.radio with custom horizontal styling
active_view = st.radio(
    label="Hidden",
    options=["🔍 Research Pipeline", "ℹ️ About the project"],
    horizontal=True,
    label_visibility="collapsed"
)

# --- VIEW: RESEARCH ---
if active_view == "🔍 Research Pipeline":
    st.header(active_view)
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
                res = requests.post(f"{API}/analyze", params={"topic": topic}, timeout=300)
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
elif active_view == "ℹ️ About the project":
    st.markdown("# About the Project")
    st.markdown("""
    **Multi-Agent Research AI** is a state-of-the-art Autonomous Agentic Retrieval-Augmented Generation (RAG) platform. It serves as a personal AI Research Assistant, transforming the way scholars and researchers interact with academic literature.

    By orchestrating a swarm of specialized agents, the system moves beyond simple summarization to perform **Autonomous Discovery**—identifying what is *missing* in a scientific domain and proposing high-impact research directions.
    """)

    st.info("⚡ **Cloud Performance Optimization:** Since this application is currently running on the Render Free Tier (limited CPU/RAM), the system is configured to analyze the top **4 most relevant papers** per topic to ensure processing completes within timeout limits. On dedicated instances, this capacity can be scaled up to 50+ papers.")

    st.markdown("## ✨ Key Features")
    st.markdown("""
    - **Multi-Source Autonomous Discovery**: 
        - Parallel ingestion from **ArXiv** and **OpenAlex** (covering millions of scientific works).
        - Bias-correction: Automatically prioritizes research clusters based on your historical feedback.
    - **Agentic Orchestration (LangGraph)**:
        - Uses a directed cyclic graph to coordinate specialized agents: **Retriever, Parser, Analyzer, Gap Finder, and Writer**.
        - Internal **Self-Reflection** loop ensures research outputs are grounded in evidence.
    - **Structural Intelligence**:
        - **Deep PDF Scraping**: Extracts methodologies, experimental setups, and datasets directly from journal PDFs using Llama 3.3.
        - **Trend & Contradiction Detection**: Identifies how techniques evolve over time and where global studies disagree.
    - **Relational Mapping**: Graph-based visualization of connection points between papers, methods, and datasets.
    - **Self-Improving RAG**: A persistent feedback loop stored in Pinecone that learns your technical preferences over time.
    """)

    st.markdown("## 🛠️ Tech Stack & Tools")
    st.markdown("""
    - **Orchestration & Workflow**: LangGraph, LangChain, Asyncio Parallel Processing.
    - **Generative AI (Groq API)**:
        - **Llama 3.3 70B**: The "Brain"—handles complex reasoning, PhD-grade synthesis, and structured JSON parsing.
        - **Llama 3.1 8B**: The "Router"—used for fast relevance grading and metadata classification.
    - **Knowledge & Memory**:
        - **Pinecone Serverless**: High-performance vector database for persistent long-term research memory.
        - **Hugging Face Inference API**: Offloads embedding generation (all-MiniLM-L6-v2), saving 100% of local CPU/Memory for agentic reasoning.
    - **Visual & Interface**:
        - **Streamlit**: Modern, premium dashboard with real-time logging.
        - **Graphviz & NetworkX**: High-resolution relational knowledge graph rendering.
    - **Backend Architecture**: FastAPI (Asynchronous Python) on Render.
    """)

    st.markdown("---")
    st.markdown("### ⭐️ Support the Project")
    st.write("If this system assisted your research, check out the [GitHub repo](https://github.com/Hartz-byte/Multi-Agent-RRL) and give it a star!")
