import streamlit as st
from dotenv import load_dotenv
import os

from services.pipeline import FactCheckPipeline
from config import STREAMLIT_TITLE, STREAMLIT_DESCRIPTION
from utils.logger import logger

load_dotenv()


st.set_page_config(
    page_title=STREAMLIT_TITLE,
    page_icon="🔍",
    layout="wide"
)

st.title(STREAMLIT_TITLE)
st.markdown(STREAMLIT_DESCRIPTION)

@st.cache_resource
def get_pipeline():
    try:
        if not os.getenv("ANTHROPIC_API_KEY"):
            st.error("⚠️ ANTHROPIC_API_KEY not found in environment variables. Please set it in .env file.")
            st.stop()
        
        logger.info("Initializing fact-checking pipeline")
        pipeline = FactCheckPipeline()
        logger.info("Pipeline initialized successfully")
        return pipeline
    except Exception as e:
        st.error(f"Error initializing pipeline: {str(e)}")
        logger.error(f"Pipeline initialization error: {str(e)}")
        st.stop()


def display_verdict(verdict: str, confidence: float = None):
    if "true" in verdict.lower():
        st.success(f"✅ **Verdict: {verdict}**")
    elif "false" in verdict.lower():
        st.error(f"❌ **Verdict: {verdict}**")
    else:
        st.warning(f"🤷♂️ **Verdict: {verdict}**")
    
    if confidence is not None:
        st.metric("Confidence Score", f"{confidence:.0%}")


with st.sidebar:
    st.header("⚙️ Settings")
    
    extraction_method = st.selectbox(
        "Claim Extraction Method",
        ["spacy", "llm"],
        help="spaCy: Fast, rule-based | LLM: More accurate, uses API calls"
    )
    
    show_evidence = st.checkbox("Show Evidence", value=True)
    show_metadata = st.checkbox("Show Source Metadata", value=False)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This fact-checker uses:
    - **spaCy** for claim extraction
    - **BGE embeddings** for semantic search
    - **ChromaDB** for vector storage
    - **Claude Haiku 4.5** for verification
    """)


tab1, tab2, tab3 = st.tabs(["📝 Single Claim", "📄 Text Analysis", "💾 Database Info"])

with tab1:
    st.header("Verify a Single Claim")
    
    claim_input = st.text_area(
        "Enter claim to verify:",
        height=100,
        placeholder="e.g., The Indian government announced free electricity to all farmers starting July 2025"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        verify_button = st.button("🔍 Verify Claim", type="primary", use_container_width=True)
    
    if verify_button:
        if not claim_input.strip():
            st.warning("⚠️ Please enter a claim to verify")
        else:
            try:
                pipeline = get_pipeline()
                
                with st.spinner("🔄 Verifying claim..."):
                    result = pipeline.verify_claim(claim_input)
                
                st.markdown("---")
                st.subheader("📊 Verification Result")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    display_verdict(result.get("verdict", "Unverifiable"), result.get("confidence"))
                
                st.markdown("### 🧠 Reasoning")
                reasoning = result.get("reasoning", "No reasoning available")
                st.info(reasoning)
                
                if show_evidence and result.get("evidence"):
                    st.markdown("### 📚 Evidence")
                    evidence_list = result.get("evidence", [])
                    if isinstance(evidence_list, list) and evidence_list:
                        for i, ev in enumerate(evidence_list, 1):
                            with st.expander(f"Evidence {i}", expanded=True):
                                st.markdown(ev)
                    elif evidence_list:
                        st.text(evidence_list)
                    else:
                        st.info("No evidence found")
            
            except Exception as e:
                st.error(f"❌ Error during verification: {str(e)}")
                logger.error(f"Verification error: {str(e)}")


with tab2:
    st.header("Verify Claims from Text")
    
    text_input = st.text_area(
        "Enter text to analyze:",
        height=200,
        placeholder="Paste your text here. Claims will be automatically extracted and verified."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
    
    if analyze_button:
        if not text_input.strip():
            st.warning("⚠️ Please enter text to analyze")
        else:
            try:
                pipeline = get_pipeline()
                
                with st.spinner("🔄 Extracting claims and verifying..."):
                    results = pipeline.verify_text(text_input, extract_claims=True, method=extraction_method)
                
                if not results:
                    st.warning("⚠️ No verifiable claims found in the text")
                else:
                    st.success(f"✅ Found and verified {len(results)} claim(s)")
                    
                    true_count = sum(1 for r in results if "true" in r['verdict'].lower())
                    false_count = sum(1 for r in results if "false" in r['verdict'].lower())
                    unverifiable_count = len(results) - true_count - false_count
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("✅ True", true_count)
                    col2.metric("❌ False", false_count)
                    col3.metric("🤷♂️ Unverifiable", unverifiable_count)
                    
                    st.markdown("---")
                    
                    for i, result in enumerate(results, 1):
                        claim_text = result.get('claim', '')[:100]
                        with st.expander(f"**Claim {i}**: {claim_text}...", expanded=True):
                            st.markdown("**📝 Full Claim:**")
                            st.info(result.get("claim", ""))
                            
                            display_verdict(result.get("verdict", "Unverifiable"), result.get("confidence"))
                            
                            st.markdown("**🧠 Reasoning:**")
                            reasoning = result.get("reasoning", "No reasoning available")
                            st.markdown(reasoning)
                            
                            if show_evidence and result.get("evidence"):
                                st.markdown("**📚 Evidence:**")
                                evidence_list = result.get("evidence", [])
                                if isinstance(evidence_list, list):
                                    for j, ev in enumerate(evidence_list, 1):
                                        st.markdown(f"{j}. {ev}")
                                else:
                                    st.text(evidence_list)
            
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")


with tab3:
    st.header("💾 Database Information")
    
    try:
        pipeline = get_pipeline()
        count = pipeline.store_manager.count()
        
        col1, col2 = st.columns(2)
        col1.metric("📊 Total Facts", count)
        col2.metric("🔧 Vector Database", "ChromaDB")
        
        if count > 0:
            st.success(f"✅ Database is populated with {count} verified facts")
            
            if st.button("👁️ View Sample Facts"):
                with st.spinner("Loading facts..."):
                    facts = pipeline.store_manager.get_all_facts()[:10]
                    
                    for i, fact in enumerate(facts, 1):
                        with st.expander(f"Fact {i}: {fact.get('fact', '')[:80]}..."):
                            st.markdown("**📝 Fact:**")
                            st.info(fact.get('fact', ''))
                            
                            if show_metadata:
                                st.markdown("**📊 Metadata:**")
                                st.json(fact.get('metadata', {}))
        else:
            st.warning("⚠️ Database is empty. Please run the ingestion script.")
            st.markdown("""
            ### Setup Instructions:
            1. Create `data/verified_facts.csv` with your facts
            2. Run: `python scripts/ingest_data.py`
            3. Refresh this page
            """)
    
    except Exception as e:
        st.error(f"❌ Error accessing database: {str(e)}")
        logger.error(f"Database access error: {str(e)}")


st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("🔍 **LLM Fact Checker** | Built with Streamlit")
with col2:
    st.markdown("⚡ Powered by Claude AI")
with col3:
    st.markdown("📦 ChromaDB + BGE")