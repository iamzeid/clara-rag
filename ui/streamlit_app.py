import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import streamlit-shadcn-ui for modern UI components
try:
    import streamlit_shadcn_ui as ui
    SHADCN_AVAILABLE = True
except ImportError:
    SHADCN_AVAILABLE = False
    ui = None

from src.generation.chain import FinConRAGPipeline
from src.ingestion.run_ingestion import run_ingestion_pipeline

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CLARA — Compliance & Ledger Analysis Retrieval Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── UI Helper Functions (streamlit-shadcn-ui with graceful fallbacks) ─────────
def render_shadcn_card(title: str, content: str = "", description: str = "", key: Optional[str] = None):
    """Renders a card using streamlit-shadcn-ui when available, falling back to clean styled HTML."""
    if SHADCN_AVAILABLE and hasattr(ui, "card"):
        try:
            return ui.card(title=title, content=content, description=description, key=key)
        except Exception:
            pass

    st.markdown(
        f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin: 8px 0; background-color: #f8fafc; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 2px;">{title}</div>
            {f'<div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">{description}</div>' if description else ''}
            {f'<div style="font-size: 13.5px; color: #334155; line-height: 1.55;">{content}</div>' if content else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_entity_badges(entities: List[Dict[str, str]], key_prefix: str = "entity"):
    """Renders recognized financial entities as badges using streamlit-shadcn-ui or styled pill tags."""
    if not entities:
        st.markdown("*No specific financial entities recognized in this query.*")
        return

    if SHADCN_AVAILABLE and hasattr(ui, "badges"):
        try:
            badge_list = [
                {"text": f"{e['text']} ({e.get('label', 'ENT')})", "badgeContent": ""}
                for e in entities
            ]
            ui.badges(badge_list=badge_list, key=f"{key_prefix}_badges")
            return
        except Exception:
            pass

    # Styled pill badges fallback
    badges_html = " ".join([
        f'<span style="display:inline-block; background-color:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; border-radius:9999px; padding:3px 10px; margin:3px 4px; font-size:12px; font-weight:500;">🏷️ {e["text"]} <span style="color:#60a5fa; font-size:11px;">[{e.get("label", "ENTITY")}]</span></span>'
        for e in entities
    ])
    st.markdown(f'<div style="margin: 4px 0 8px 0;">{badges_html}</div>', unsafe_allow_html=True)

def render_metric_card(title: str, content: str, description: str = "", key: Optional[str] = None):
    """Renders a metric card using streamlit-shadcn-ui or native st.metric."""
    if SHADCN_AVAILABLE and hasattr(ui, "metric_card"):
        try:
            return ui.metric_card(title=title, content=content, description=description, key=key)
        except Exception:
            pass
    st.metric(label=title, value=content, help=description if description else None)

# ── Pipeline Singleton ────────────────────────────────────────────────────────
@st.cache_resource
def get_pipeline():
    return FinConRAGPipeline()

pipeline = get_pipeline()

# ── 2026 Financial Standards Sample Queries ──────────────────────────────────
SAMPLE_QUERIES = [
    "What is the mandatory timeline for Form 8-K disclosure under SEC Item 1.05 for material cybersecurity incidents?",
    "What are the differences between Scope 1, Scope 2, and Scope 3 emissions under IFRS S2 in 2026?",
    "What are the eligibility criteria and turnover thresholds for EU CSRD Wave 2 compliance in 2026?",
    "What is the Basel III Endgame capital output floor percentage for risk-weighted assets?",
    "What confidence level is required for Expected Shortfall under the FRTB market risk framework?"
]

# ── Session State Initialization ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ── Sidebar: AI Persona Identity, Configuration & Controls ───────────────────
with st.sidebar:
    # Visible AI Persona Identity Badge

    st.markdown("### ⚙️ Pipeline Settings")
    top_k = st.slider("Top-K Rerank Results", min_value=1, max_value=8, value=3, step=1,
                      help="Number of top child chunks retrieved and reranked before parent expansion.")

    st.markdown("---")
    st.markdown("### 🔄 Knowledge Ingestion")
    if st.button("Run Document Ingestion", use_container_width=True, help="Parses standards corpus & rebuilds hybrid indexes"):
        with st.spinner("CLARA is indexing regulatory documents & constructing hybrid indexes..."):
            try:
                run_ingestion_pipeline()
                pipeline.refresh_parent_store()
                st.success("✅ Knowledge base successfully synced & indexed!")
            except Exception as e:
                st.error(f"❌ Ingestion failed: {e}")

    st.markdown("---")
    st.markdown("### 💬 Chat Management")
    if st.button("🗑️ Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("---")


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 0 16px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); display: flex; align-items: center; justify-content: center; font-size: 26px; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.06);">
                ⚖️
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 22px; font-weight: 700; color: #0f172a; letter-spacing: -0.3px;">CLARA</span>
                    <span style="background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 9999px; border: 1px solid #cbd5e1;">AI Regulatory Persona</span>
                    <span style="background-color: #dcfce7; color: #166534; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 9999px; border: 1px solid #bbf7d0;">● Live Retrieval</span>
                </div>
                <div style="font-size: 13px; color: #64748b; margin-top: 2px;">
                    <strong>C</strong>ompliance & <strong>L</strong>edger <strong>A</strong>nalysis <strong>R</strong>etrieval <strong>A</strong>ssistant • Enterprise Financial Controlling Co-Pilot
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ── Helper to Render Collapsible RAG Input Details ───────────────────────────
def render_input_inspection(rag_input_data: Dict[str, Any], msg_idx: int):
    """Renders the hidden input processing details (entities, expansion, parameters) inside an expander."""
    with st.expander("🔍 Pre-Retrieval Input Processing & Query Analysis (Click to View)", expanded=False):
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("##### 🏷️ Recognized Financial Entities (spaCy NER)")
            entities = rag_input_data.get("entities", [])
            render_entity_badges(entities, key_prefix=f"user_{msg_idx}")

        with col2:
            st.markdown("##### ⚙️ Retrieval Parameters")
            st.markdown(f"- **Top-K Rerank Results:** `{rag_input_data.get('top_k', 3)}`")
            st.markdown(f"- **Retrieval Mode:** `Hierarchical Child-to-Parent Hybrid`")

        st.markdown("##### 🔄 Pre-Retrieval Query Expansion")
        orig_query = rag_input_data.get("original_query", "")
        expanded_query = rag_input_data.get("expanded_query", "")

        if expanded_query and expanded_query != orig_query:
            st.markdown(
                f"""
                <div style="background-color: #f1f5f9; border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 4px; font-size: 13.5px; margin: 8px;">
                    <strong>Original:</strong> {orig_query}<br>
                    <strong>Expanded with Domain Lexicon:</strong> <span style="color: #1d4ed8; font-weight: 500;">{expanded_query}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown("*No additional domain expansion terms needed; exact query terms matched financial vocabulary.*")

# ── Helper to Render Collapsible RAG Output Details ──────────────────────────
def render_output_inspection(rag_output_data: Dict[str, Any], msg_idx: int):
    """Renders the hidden output details (sources, child chunks, scores, parent context) inside an expander."""
    with st.expander("📊 Inspect RAG Retrieval & Context Details (Click to Expand)", expanded=False):
        inspect_tabs = st.tabs([
            "📚 Source Attributions",
            "🎯 Retrieved Chunks & Reranker Scores",
            "📖 Full Parent Context Sent to LLM"
        ])

        # Tab 1: Sources & Citations
        with inspect_tabs[0]:
            sources = rag_output_data.get("sources", [])
            if sources:
                st.markdown("##### 📚 Official Regulatory & Controlling Sources Grounding this Answer:")
                for s_idx, src in enumerate(sources, start=1):
                    render_shadcn_card(
                        title=f"Source [{s_idx}]: {src}",
                        description="Verified Regulatory Standard / Financial Corpus Document",
                        content="This document was retrieved via hierarchical indexing and passed citation validation.",
                        key=f"card_src_{msg_idx}_{s_idx}"
                    )
            else:
                st.info("No specific external source documents were required for this synthesis.")

        # Tab 2: Retrieved Child Chunks & Scores
        with inspect_tabs[1]:
            chunks = rag_output_data.get("retrieved_child_chunks", [])
            if chunks:
                st.markdown(f"##### 🎯 Top-{len(chunks)} Child Chunks After Cross-Encoder Reranking:")
                for idx, chunk in enumerate(chunks, start=1):
                    rerank_score = chunk.get("rerank_score", 0.0)
                    rrf_score = chunk.get("rrf_score", 0.0)
                    chunk_id = chunk.get("id", f"chunk_{idx}")
                    parent_id = chunk.get("parent_id", "N/A")
                    meta_src = chunk.get("metadata", {}).get("source", "N/A")

                    header_badge = f"Rank #{idx} | Cross-Encoder Rerank Score: {rerank_score:.4f} | RRF Score: {rrf_score:.4f}"
                    desc = f"Parent ID: {parent_id} • Source: {meta_src}"
                    clean_text = chunk.get("text", "").strip()

                    render_shadcn_card(
                        title=f"Chunk {chunk_id} ({header_badge})",
                        description=desc,
                        content=f"{clean_text}",
                        key=f"card_chunk_{msg_idx}_{idx}"
                    )
            else:
                st.info("No child chunks were retrieved for this query.")

        # Tab 3: Full Parent Context Sent to LLM
        with inspect_tabs[2]:
            parent_context = rag_output_data.get("context_used", "")
            if parent_context:
                st.markdown("##### 📖 Complete Hierarchical Parent Context Injected into LLM Prompt:")
                st.code(parent_context, language="markdown")
            else:
                st.info("No parent context was injected.")

# ── Render Chat History ───────────────────────────────────────────────────────
if len(st.session_state.messages) == 0:
    # Empty state landing display showing CLARA's AI persona introduction
    st.markdown(
        """
        <div style="background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            <div style="display: flex; align-items: flex-start; gap: 16px;">
                <div style="width: 52px; height: 52px; border-radius: 12px; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                    ⚖️
                </div>
                <div>
                    <h3 style="margin: 0 0 6px 0; font-size: 19px; color: #0f172a;">Hello, I am CLARA</h3>
                    <p style="margin: 0 0 10px 0; font-size: 14px; color: #475569; line-height: 1.55;">
                        I am your <strong>Autonomous Regulatory & Compliance AI Persona</strong>. I analyze statutory reporting frameworks, 
                        SEC disclosures, IFRS ESG metrics, and banking capital mandates to provide rigorous, citation-backed intelligence for financial controllers and auditors.
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                        <span style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 9999px; padding: 2px 10px; font-size: 12px; color: #334155; font-weight: 500;">🎯 Audit-Defensible</span>
                        <span style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 9999px; padding: 2px 10px; font-size: 12px; color: #334155; font-weight: 500;">⚖️ SEC Item 1.05 & 8-K</span>
                        <span style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 9999px; padding: 2px 10px; font-size: 12px; color: #334155; font-weight: 500;">🌿 IFRS S2 Climate Disclosures</span>
                        <span style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 9999px; padding: 2px 10px; font-size: 12px; color: #334155; font-weight: 500;">🏦 Basel III Endgame & FRTB</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### 💡 Quick Inquiry Starters")
    st.caption("Select a standard regulatory inquiry to begin your consultation with CLARA:")
    col_a, col_b = st.columns(2)
    for i, sq in enumerate(SAMPLE_QUERIES):
        target_col = col_a if i % 2 == 0 else col_b
        with target_col:
            if st.button(f"📌 {sq}", key=f"quick_sq_{i}", use_container_width=True):
                st.session_state.pending_prompt = sq
                st.rerun()

else:
    # Render all conversation turns
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
                if msg.get("rag_input_data"):
                    render_input_inspection(msg["rag_input_data"], idx)

        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="⚖️"):
                # Persona Header Badge on Assistant Bubble
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="font-weight: 600; font-size: 13px; color: #0f172a;">CLARA</span>
                        <span style="font-size: 10.5px; background-color: #f1f5f9; color: #475569; padding: 1px 6px; border-radius: 4px; border: 1px solid #e2e8f0;">AI Compliance Co-Pilot</span>
                        <span style="font-size: 10.5px; color: #16a34a;">● Grounded Analysis</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(msg["content"])
                if msg.get("rag_output_data"):
                    render_output_inspection(msg["rag_output_data"], idx)

# ── Chat Input Processing ─────────────────────────────────────────────────────
active_prompt = st.session_state.pending_prompt
st.session_state.pending_prompt = None

chat_prompt = st.chat_input("Ask CLARA a compliance, accounting, or regulatory question...")

prompt_to_process = active_prompt if active_prompt else chat_prompt

if prompt_to_process:
    cleaned_prompt = prompt_to_process.strip()
    if cleaned_prompt:
        with st.chat_message("user", avatar="👤"):
            st.markdown(cleaned_prompt)

        with st.chat_message("assistant", avatar="⚖️"):
            with st.spinner("CLARA is retrieving statutory standards & evaluating ledger evidence..."):
                try:
                    result = pipeline.run(query=cleaned_prompt, top_k_rerank=top_k)
                    answer_text = result.get("answer", "No answer generated.")
                    st.markdown(answer_text)

                    rag_input_data = {
                        "original_query": cleaned_prompt,
                        "expanded_query": result.get("expanded_query", cleaned_prompt),
                        "entities": result.get("entities", []),
                        "top_k": top_k
                    }

                    rag_output_data = {
                        "sources": result.get("sources", []),
                        "retrieved_child_chunks": result.get("retrieved_child_chunks", []),
                        "retrieved_parent_chunks": result.get("retrieved_parent_chunks", []),
                        "context_used": result.get("context_used", ""),
                        "query": cleaned_prompt
                    }

                    st.session_state.messages.append({
                        "role": "user",
                        "content": cleaned_prompt,
                        "rag_input_data": rag_input_data
                    })

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_text,
                        "rag_output_data": rag_output_data
                    })

                    st.rerun()

                except Exception as ex:
                    error_msg = f"⚠️ An error occurred while executing the RAG pipeline: {str(ex)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "user",
                        "content": cleaned_prompt,
                        "rag_input_data": {"original_query": cleaned_prompt, "top_k": top_k}
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "rag_output_data": {}
                    })
                    st.rerun()