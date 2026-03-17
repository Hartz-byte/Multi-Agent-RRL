import streamlit as st
import requests
import graphviz
import asyncio

API = "http://localhost:10000"

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide")

st.title("🛡️ Multi-Agent AI RRL Research System")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_input("Enter research topic", placeholder="e.g., 'Low-resource LLM optimization'")

# Function to submit feedback
def submit_feedback(topic, paper_id, rating):
    try:
        res = requests.post(f"{API}/feedback", params={"topic": topic, "paper_id": paper_id, "rating": rating}, timeout=5)
        if res.status_code == 200:
            st.toast(f"Feedback saved for {paper_id}!")
    except:
        st.error("Failed to submit feedback.")

if st.button("🚀 Analyze Research Domain"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Executing Multi-Agent Pipeline... (Retrieving Parallel Sources, Parsing, & Reasoning)"):
            try:
                res = requests.post(f"{API}/analyze", params={"topic": topic}, timeout=120)
                
                if res.status_code == 200:
                    data = res.json()
                    
                    st.success("Pipeline Execution Complete")
                    
                    # --- Tabbed Layout for Results ---
                    tab1, tab2, tab3 = st.tabs(["📊 Core Synthesis", "🕸️ Knowledge Graph", "📝 Literature Review"])
                    
                    with tab1:
                        res_col1, res_col2 = st.columns(2)
                        
                        with res_col1:
                            st.subheader("📊 Trend Analysis")
                            st.write(data.get("trends", "N/A"))
                            
                            st.subheader("⚠️ Contradictions & Conflicts")
                            st.write(data.get("contradictions", "N/A"))
                            
                        with res_col2:
                            st.subheader("🔍 Identified Research Gaps")
                            st.write(data.get("gaps", "N/A"))
                            
                            st.subheader("💡 Suggested Research Proposal")
                            st.write(data.get("proposal", "N/A"))
                    
                    with tab2:
                        st.subheader("🕸️ Relational Knowledge Graph")
                        graph_data = data.get("graph_data", {})
                        
                        if graph_data:
                            dot = graphviz.Digraph(comment='Research Graph')
                            dot.attr(rankdir='LR', size='10,10')
                            dot.attr('node', shape='box', style='filled', color='lightblue')
                            
                            for node in graph_data.get('nodes', []):
                                label = node.get('label', node.get('id', 'Unknown'))
                                dot.node(str(node['id']), label)
                                
                            for link in graph_data.get('links', []):
                                dot.edge(str(link['source']), str(link['target']))
                                
                            st.graphviz_chart(dot)
                        else:
                            st.info("No graph data available for this query.")

                    with tab3:
                        st.subheader("📝 Literature Review (RRL)")
                        st.markdown(data.get("rrl", "N/A"))
                        
                        # Display source papers (Vector database metadata)
                        with st.expander("📚 Sources & Metadata (from Parallel Multi-Sources)"):
                            for p in data.get("parsed_papers", []):
                                col_p1, col_p2 = st.columns([4, 1])
                                with col_p1:
                                    st.write(f"**{p['title']}** ({p.get('year', 0)})")
                                    st.caption(f"*Source: {p.get('metadata', {}).get('source', 'Unknown')} | PDF: {p.get('metadata', {}).get('pdf_url', 'N/A')}*")
                                with col_p2:
                                    # Feedback loop: Rating buttons for specific paper preference
                                    rating = st.selectbox("Rate", [1, 2, 3, 4, 5], key=f"rate_{p['title']}")
                                    if st.button("Submit", key=f"btn_{p['title']}"):
                                        submit_feedback(topic, p['title'], rating)
                                st.markdown("---")
                else:
                    st.error(f"Error from backend: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
