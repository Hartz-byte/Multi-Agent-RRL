import streamlit as st
import requests

API = "http://localhost:10000"

st.set_page_config(page_title="Multi-Agent Research AI", layout="wide")

st.title("🛡️ Multi-Agent AI RRL Research System")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    topic = st.text_input("Enter research topic (e.g., 'Low-resource LLM optimization')")

if st.button("🚀 Analyze Research Domain"):
    with st.spinner("Executing Multi-Agent Pipeline... (Retrieving, Parsing, & Reasoning)"):
        res = requests.post(f"{API}/analyze", params={"topic": topic})
        
        if res.status_code == 200:
            data = res.json()
            
            # --- Results ---
            st.success("Pipeline Execution Complete")
            
            # Use columns for layout
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
            
            st.markdown("---")
            st.subheader("📝 Literature Review (RRL)")
            st.write(data.get("rrl", "N/A"))
            
            # Display source papers
            with st.expander("📝 Source Papers (Metadata)"):
                for p in data.get("papers", []):
                    st.write(f"- **{p['title']}** ({p['year']})")
                    st.caption(p['summary'][:200] + "...")
        else:
            st.error(f"Error from backend: {res.text}")
