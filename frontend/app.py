import streamlit as st
import requests
import graphviz

API = "http://localhost:10000"

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide")

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { align-items: center; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; padding: 10px 20px; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_value=True)

st.title("🛡️ Multi-Agent AI RRL Research System")
st.caption("Autonomous Discovery of Research Gaps & Literature Synthesis")
st.markdown("---")

# --- Initialize Session State ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = ""

# --- Sidebar: Instructions and Examples ---
with st.sidebar:
    st.image("https://img.icons8.com/bubbles/100/research.png", width=80)
    st.header("Project Guide")
    st.info("""
    1. Enter a research topic.
    2. The system fetches papers from ArXiv & OpenAlex.
    3. Multi-agent reasoning identifies trends, conflicts, and gaps.
    4. A relational Knowledge Graph is constructed.
    5. A formal RRL and Research Proposal are generated.
    """)
    
    st.subheader("💡 Example Topics")
    examples = [
        "Hybrid RAG for clinical documents",
        "Explainability in Transformer-based STT",
        "Edge computing for real-time video analytics",
        "Prompt engineering for legal reasoning"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.current_topic = ex
            st.rerun()

# --- Main Input Area ---
col_in1, col_in2 = st.columns([4, 1])
with col_in1:
    topic = st.text_input("Research Topic", value=st.session_state.current_topic, placeholder="e.g., 'Low-resource LLM optimization'")

# Function to submit feedback
def submit_feedback(topic, paper_id, rating):
    try:
        res = requests.post(f"{API}/feedback", params={"topic": topic, "paper_id": paper_id, "rating": rating}, timeout=5)
        if res.status_code == 200:
            st.toast(f"✅ Preference saved for: {paper_id}")
            return True
    except:
        st.error("Failed to submit feedback.")
        return False

# Function to run analysis
def run_analysis():
    if not topic:
        st.warning("Please enter a topic.")
        return
    
    with st.spinner("🚀 Executing Multi-Agent Pipeline... (Retrieving Parallel Sources, Parsing, & Reasoning)"):
        try:
            res = requests.post(f"{API}/analyze", params={"topic": topic}, timeout=150)
            if res.status_code == 200:
                st.session_state.analysis_result = res.json()
                st.session_state.current_topic = topic
                st.success("Pipeline Execution Complete!")
            else:
                st.error(f"Backend Error: {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

with col_in2:
    st.write("") # spacing
    st.write("")
    if st.button("🚀 Run Analysis", use_container_width=True):
        run_analysis()

# --- Display Results from Session State ---
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
                # Different colors for different types
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
        st.caption("Help the system learn: Rate papers by relevance to your topic to bias future retrieval.")
        
        for p in data.get("parsed_papers", []):
            with st.expander(f"📄 {p['title']}"):
                col_p1, col_p2 = st.columns([3, 1])
                with col_p1:
                    st.write(f"**Year:** {p.get('year', 'N/A')} | **Source:** {p.get('metadata', {}).get('source', 'N/A')}")
                    st.write(f"**Authors:** {', '.join(p.get('metadata', {}).get('authors', ['Unknown']))}")
                    st.caption(f"[View PDF/Link]({p.get('metadata', {}).get('pdf_url', '#')})")
                    st.markdown("**Structured Insight:**")
                    st.json(p.get('structured_data', {}))
                with col_p2:
                    rating = st.select_slider("Relevance", options=[1, 2, 3, 4, 5], value=3, key=f"rate_{p['title']}")
                    if st.button("Submit Rating", key=f"btn_{p['title']}"):
                        submit_feedback(topic, p['title'], rating)
else:
    # Empty state
    st.markdown("<br><br><br>", unsafe_allow_value=True)
    st.center_col = st.columns([1, 2, 1])
    with st.center_col[1]:
        st.write("### 🧭 Ready to explore?")
        st.write("Enter a topic above or select an example from the sidebar to begin your research journey.")
