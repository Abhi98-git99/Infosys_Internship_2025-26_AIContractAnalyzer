import streamlit as st
import tempfile
from _3_unstruct_struct_parsing import read_doc_pro
from _4_clause_extraction import extract_clause as extract_clauses
from _5_keyword_classifier import classify_clause
from _6_langgraph import app, db_clause
from _7_embedding_pinecone import upsert_db, query_db

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Contract Analyzer | Executive Suite",
    page_icon="CA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Professional Office CSS 🏛️
# -------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;700&family=JetBrains+Mono&display=swap');

        /* Main Body: Light Gray / White Professional */
        .stApp {
            background-color: #F8FAFC;
            font-family: 'Public Sans', sans-serif;
        }

        /* Top Navigation Bar */
        .nav-header {
            background: #FFFFFF;
            padding: 1.5rem 3rem;
            border-bottom: 2px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        /* Professional Clause Cards */
        .clause-container {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        }

        /* Large Risk Indicators */
        .risk-label {
            padding: 8px 20px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .high { background: #FEE2E2; color: #991B1B; border: 1px solid #F87171; }
        .medium { background: #FEF3C7; color: #92400E; border: 1px solid #FBBF24; }
        .low { background: #D1FAE5; color: #065F46; border: 1px solid #34D399; }

        /* Agent Branding */
        .agent-header {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: #64748B;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #1E293B;
            color: black;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Business Logic
# -------------------------------------------------
def process_document(file):
    db_clause.clear()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        path = tmp.name

    elements = read_doc_pro(path)
    clauses = extract_clauses(elements)
    
    if not clauses:
        st.error("Document parsing failed. No clauses found.")
        return

    progress_container = st.empty()
    bar = st.progress(0)
    
    for i, clause in enumerate(clauses):
        progress_container.markdown(f"**Agent Review in Progress:** *Clause {i+1} of {len(clauses)}*")
        for ctype in classify_clause(clause):
            app.invoke({"clause": clause, "clause_type": ctype})
        bar.progress((i + 1) / len(clauses))
    
    upsert_db()
    progress_container.success(f"Audit Complete. {len(db_clause)} data points indexed.")

# -------------------------------------------------
# Header Section
# -------------------------------------------------
st.markdown("""
    <div class="nav-header">
        <div style="display:flex; align-items:center; gap: 15px;">
            <div style="background:#2563EB; width:45px; height:45px; border-radius:8px; display:grid; place-items:center; color:white; font-weight:bold; font-size:24px;">L</div>
            <h1 style="margin:0; font-size:1.8rem; font-weight:700; color:#1E293B; letter-spacing:-1px;">Contract<span style="color:#2563EB">Analyzer</span></h1>
        </div>
        <div style="color:#64748B; font-weight:500;">Corporate Legal Intelligence v4.0</div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠 COMMAND CENTER")
    mode = st.radio("SELECT OPERATION", ["📥 DOCUMENT INGESTION", "🔍 SEMANTIC AUDIT"])
    
    st.markdown("---")
    st.markdown("### 📊 ACTIVE AGENTS")
    st.caption("✅ Compliance Guardian")
    st.caption("✅ Legal Risk Analyst")
    st.caption("✅ Finance & Penalties")
    st.caption("✅ Ops Workflow Review")
    
    st.markdown("---")
    if st.button("CLEAR SYSTEM MEMORY", type="secondary", use_container_width=True):
        db_clause.clear()
        st.rerun()

# -------------------------------------------------
# Main Interface
# -------------------------------------------------
if mode == "📥 DOCUMENT INGESTION":
    st.markdown("## 📄 Document Ingestion & Extraction")
    st.markdown("Upload corporate contracts for multi-agent risk synthesis.")
    
    with st.container():
        uploaded_file = st.file_uploader("Drop PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")
        if st.button("EXECUTE CORPORATE AUDIT", type="primary", use_container_width=True):
            if uploaded_file:
                process_document(uploaded_file)
            else:
                st.warning("Action Required: Please upload a valid legal document.")

else:
    st.markdown("## 🔍 Semantic Audit")
    query = st.text_input("QUERY CLAUSE DATABASE", placeholder="e.g., 'What are the indemnification limits for IP infringement?'")
    
    if query:
        results = query_db(query)
        if results["matches"]:
            for m in results["matches"]:
                md = m["metadata"]
                risk_lvl = md.get('risk', 'Low')
                
                st.markdown(f"""
                <div class="clause-container">
                    <div class="agent-header">
                        SYSTEM AGENT: {md['agent'].upper()} | NODE ID: {m['id'][:8]}
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                        <div style="flex:1; padding-right:20px;">
                            <span style="color:#94A3B8; font-size:0.8rem; font-weight:700; text-transform:uppercase;">Extracted Language</span>
                            <p style="font-size:1.15rem; color:#1E293B; line-height:1.6; margin-top:5px;">"{md['clause']}"</p>
                        </div>
                        <div class="risk-label {risk_lvl.lower()}">{risk_lvl} RISK</div>
                    </div>
                    <div style="background:#F1F5F9; padding:20px; border-radius:8px;">
                        <span style="color:#2563EB; font-weight:700; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Agent Analysis & Mitigation</span>
                        <p style="color:#334155; margin-top:8px; line-height:1.5;">{md['analysis']}</p>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:15px; border-top: 1px solid #CBD5E1; pt:10px;">
                            <div><small><b>SEVERITY:</b> {md['severity']}</small></div>
                            <div><small><b>OBLIGATION:</b> {md['obligations']}</small></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No relevant clauses found matching that query.")