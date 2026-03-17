import streamlit as st
import requests
import graphviz

API = "http://localhost:10000"

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide")

st.title("🛡️ Multi-Agent AI RRL Research System")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_input("Enter research topic", placeholder="e.g., 'Low-resource LLM optimization'")

if st.button("🚀 Analyze Research Domain"):
    with st.spinner("Executing Multi-Agent Pipeline... (Retrieving, Parsing, & Reasoning)"):
        try:
            res = requests.post(f"{API}/analyze", params={"topic": topic}, timeout=60)
            
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
                        # Convert NetworkX links/nodes to Graphviz dot source
                        dot = graphviz.Digraph(comment='Research Graph')
                        dot.attr(rankdir='LR', size='10,10')
                        dot.attr('node', shape='box', style='filled', color='lightblue')
                        
                        # Add Nodes from json-graph data
                        for node in graph_data.get('nodes', []):
                            label = node.get('label', node.get('id', 'Unknown'))
                            dot.node(str(node['id']), label)
                            
                        # Add Edges
                        for link in graph_data.get('links', []):
                            dot.edge(str(link['source']), str(link['target']))
                            
                        st.graphviz_chart(dot)
                    else:
                        st.info("No graph data available for this query.")

                with tab3:
                    st.subheader("📝 Literature Review (RRL)")
                    st.markdown(data.get("rrl", "N/A"))
                    
                    # Display source papers (Vector database metadata)
                    with st.expander("📚 Sources & Metadata (from Pinecone Storage)"):
                        for p in data.get("papers", []):
                            st.write(f"- **{p['title']}** ({p['year']})")
                            st.caption(f"*Source URL: {p['pdf_url']}*")
                            st.caption(f"Authors: {', '.join(p.get('authors', []))}")
            else:
                st.error(f"Error from backend: {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")
