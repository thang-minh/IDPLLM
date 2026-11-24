# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import nltk
import pytesseract
from datetime import datetime

# =========================================================
# 1. PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# =========================================================
st.set_page_config(
    page_title="SmartDoc AI – Enterprise Document Processing",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "# SmartDoc AI Platform\nModern Enterprise Document Processing SaaS."
    }
)

# =========================================================
# 2. ENVIRONMENT & SYSTEM INTEGRATION
# =========================================================
load_dotenv()

TESSERACT_PATH_ENV = os.getenv("TESSERACT_CMD")
POPPLER_PATH_ENV_CONFIG = os.getenv("POPPLER_PATH")

OPENROUTER_API_KEY_ENV = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY_ENV = os.getenv("GROQ_API_KEY")
API_KEY_CONFIG = GROQ_API_KEY_ENV if GROQ_API_KEY_ENV else OPENROUTER_API_KEY_ENV

if TESSERACT_PATH_ENV and os.path.exists(TESSERACT_PATH_ENV):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH_ENV
elif os.name == "nt":
    for path in [r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# Ensure NLTK resources
def ensure_nltk_resource(resource_path, download_name):
    try:
        nltk.data.find(resource_path)
    except LookupError:
        try:
            nltk.download(download_name, quiet=True)
        except Exception:
            pass

ensure_nltk_resource("tokenizers/punkt", "punkt")
ensure_nltk_resource("corpora/wordnet", "wordnet")
ensure_nltk_resource("corpora/omw-1.4", "omw-1.4")

# =========================================================
# 3. IMPORT UI MODULES & COMPONENTS
# =========================================================
from ui_modules.main_smartdoc_ui import show_main_smartdoc_ui
from ui_modules.form_extractor_ui import show_form_extractor_ui
from ui_modules.version_manager_ui import show_version_manager_ui
from ui_modules.multi_doc_qna_ui import show_multi_doc_qna_ui
from ui_modules.knowledge_graph_ui import show_knowledge_graph_ui
from ui_modules.pdf_redaction_ui import show_pdf_redaction_ui
from ui_modules.table_extractor_ui import show_table_extractor_ui
from ui_modules.compare_module_ui import show_compare_module_ui
from ui_modules.converter_ui import show_converter_ui
from ui_modules.sentiment_analyzer_ui import show_sentiment_analyzer_ui
from ui_modules.translator_ui import show_translator_ui
from ui_modules.pdf_merge_ui import show_pdf_merge_ui
from ui_modules.pdf_split_ui import show_pdf_split_ui
from ui_modules.pdf_watermark_ui import show_pdf_watermark_ui
from ui_modules.pdf_unlock_ui import show_pdf_unlock_ui
from ui_modules.pdf_protect_ui import show_pdf_protect_ui
from ui_modules.pdf_editor_ui import show_pdf_editor_ui
from ui_modules.pdf_signer_ui import show_pdf_signer_ui

from ui_utils.dark_mode import manage_dark_mode
from ui_utils.ui_components import (
    get_runtime_system_status,
    render_page_header,
    render_sidebar_system_status,
)

# Apply Global Design System & SaaS Theme CSS at root
manage_dark_mode()

# =========================================================
# 4. NAVIGATION REGISTRY (ORGANIZED BY SPECIFICATION)
# =========================================================
NAVIGATION_GROUPS = {
    "AI DOCUMENT": {
        "AI Document Processing": {
            "icon": "🧠",
            "desc": "PhoBERT fine-tuned classifier, PDF text extraction & deep LLM analysis.",
            "route": lambda: show_main_smartdoc_ui(API_KEY_CONFIG, POPPLER_PATH_ENV_CONFIG)
        },
        "Form Extraction": {
            "icon": "🎯",
            "desc": "EfficientNetV2B0 classification, OCR & structured JSON extraction.",
            "route": lambda: show_form_extractor_ui(API_KEY_CONFIG)
        },
        "Document Storage": {
            "icon": "🗂️",
            "desc": "Track document version history, restore states and view audits.",
            "route": lambda: show_version_manager_ui(API_KEY_CONFIG)
        },
    },
    "AI KNOWLEDGE": {
        "Document Q&A": {
            "icon": "💬",
            "desc": "Multi-document semantic search and RAG synthesis with FAISS.",
            "route": lambda: show_multi_doc_qna_ui(API_KEY_CONFIG, POPPLER_PATH_ENV_CONFIG)
        },
        "Knowledge Graph": {
            "icon": "🕸️",
            "desc": "Visual graph of inter-document entity relationships.",
            "route": lambda: show_knowledge_graph_ui(API_KEY_CONFIG, POPPLER_PATH_ENV_CONFIG)
        },
    },
    "AI SECURITY": {
        "AI Redaction": {
            "icon": "🛡️",
            "desc": "Detect and sanitize sensitive PII data directly in PDF streams.",
            "route": lambda: show_pdf_redaction_ui()
        },
    },
    "DOCUMENT TOOLS": {
        "Table Extractor": {
            "icon": "📋",
            "desc": "Extract tabular data from PDFs into clean Excel/CSV formats.",
            "route": lambda: show_table_extractor_ui()
        },
        "Document Comparison": {
            "icon": "⚖️",
            "desc": "Visual optical comparison and character diff across versions.",
            "route": lambda: show_compare_module_ui()
        },
        "Document Converter": {
            "icon": "🔄",
            "desc": "Offline conversion between Images, PDF and Microsoft Word.",
            "route": lambda: show_converter_ui()
        },
        "Sentiment Analysis": {
            "icon": "📈",
            "desc": "Analyze sentiment polarity, keywords and response recommendations.",
            "route": lambda: show_sentiment_analyzer_ui(API_KEY_CONFIG)
        },
        "Document Translator": {
            "icon": "🌐",
            "desc": "Context-aware translation for cross-border documents.",
            "route": lambda: show_translator_ui(API_KEY_CONFIG)
        },
        "PDF Editor": {
            "icon": "✏️",
            "desc": "Reorder, delete, rotate and optimize PDF pages.",
            "route": lambda: show_pdf_editor_ui()
        },
        "PDF Signer": {
            "icon": "✍️",
            "desc": "Digitally sign or place stamp images onto PDF pages.",
            "route": lambda: show_pdf_signer_ui()
        },
        "PDF Merge": {
            "icon": "🧩",
            "desc": "Combine multiple PDF documents into a single unified file.",
            "route": lambda: show_pdf_merge_ui()
        },
        "PDF Split": {
            "icon": "✂️",
            "desc": "Split PDF files into individual pages or custom ranges.",
            "route": lambda: show_pdf_split_ui()
        },
        "PDF Watermark": {
            "icon": "💧",
            "desc": "Stamp text or image watermarks onto PDF pages.",
            "route": lambda: show_pdf_watermark_ui()
        },
        "PDF Protect": {
            "icon": "🔒",
            "desc": "Encrypt and password-protect confidential PDF files.",
            "route": lambda: show_pdf_protect_ui()
        },
        "PDF Unlock": {
            "icon": "🔓",
            "desc": "Remove password restrictions from authorized PDFs.",
            "route": lambda: show_pdf_unlock_ui()
        },
    },
    "SYSTEM": {
        "System Status": {
            "icon": "⚡",
            "desc": "Central operations overview, system runtime health and fast actions.",
            "route": lambda: show_home_dashboard()
        }
    }
}

if "current_nav_feature" not in st.session_state:
    st.session_state.current_nav_feature = "System Status"

def navigate_to(feature_name: str):
    st.session_state.current_nav_feature = feature_name
    for group_name, features in NAVIGATION_GROUPS.items():
        if feature_name in features:
            st.session_state.selected_nav_group = group_name
            break
    st.rerun()

# =========================================================
# 5. HOME DASHBOARD (ENTERPRISE AI SAAS DASHBOARD)
# =========================================================
def show_home_dashboard():
    sys_status = get_runtime_system_status()

    badges = [
        {"text": "● System Operational", "type": "success"},
        {"text": "Production v1.0", "type": "neutral"},
    ]
    render_page_header(
        title="SmartDoc AI Platform",
        description="Comprehensive enterprise AI platform for automated document intelligence, classification, structured data extraction, and semantic search.",
        breadcrumb="SYSTEM / DASHBOARD OVERVIEW",
        badges=badges
    )

    # Hero Card (Stripe & Linear SaaS Style)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
                border: 1px solid rgba(99, 102, 241, 0.4);
                border-radius: 14px;
                padding: 24px 30px;
                margin-bottom: 24px;
                box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.25);">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 9999px; margin-bottom: 14px;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
            <span style="font-size: 11.5px; font-weight: 700; color: #E0E7FF; letter-spacing: 0.06em; text-transform: uppercase;">SmartDoc AI Platform v2.0</span>
        </div>
        <h1 style="color: #FFFFFF !important; font-size: 26px; font-weight: 800; margin: 0 0 10px 0; letter-spacing: -0.025em; line-height: 1.25;">
            Nền tảng Xử lý Tài liệu Thông minh AI
        </h1>
        <p style="color: #C7D2FE !important; font-size: 14px; line-height: 1.6; margin: 0; max-width: 820px;">
            Hệ sinh thái xử lý tài liệu thông minh kết hợp mô hình AI thị giác máy tính cục bộ (EfficientNetV2), mô hình ngôn ngữ tiếng Việt (PhoBERT), cùng công nghệ OCR tiên tiến và tìm kiếm ngữ nghĩa vector (FAISS RAG). Tự động hóa bóc tách hóa đơn, hợp đồng và hồ sơ với độ chính xác cao.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # System Status Cards
    st.markdown("### ⚡ System Status")
    st.caption("Real-time runtime health metrics across all underlying engines.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.15rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 4px;">Image Classifier</div>
            <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 8px;">EfficientNetV2B0</div>
            {'<span class="badge-soft-success">● Model Ready</span>' if sys_status["efficientnet"] else '<span class="badge-soft-warning">○ Not Loaded</span>'}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.15rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 4px;">OCR Service</div>
            <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 8px;">Tesseract OCR</div>
            {'<span class="badge-soft-success">● OCR Online</span>' if sys_status["ocr"] else '<span class="badge-soft-danger">○ OCR Offline</span>'}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.15rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 4px;">LLM Integration</div>
            <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 8px;">Groq / OpenRouter</div>
            {'<span class="badge-soft-indigo">● Configured</span>' if sys_status["llm"] else '<span class="badge-soft-danger">○ Key Missing</span>'}
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1rem 1.15rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);">
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 4px;">PDF Engine</div>
            <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 8px;">PyMuPDF / Poppler</div>
            {'<span class="badge-soft-neutral">● Poppler Available</span>' if sys_status["poppler"] else '<span class="badge-soft-neutral">● Native Engine</span>'}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3 Fast Actions Cards
    st.markdown("### 🚀 Fast Actions")
    st.caption("Direct one-click access to core AI document pipelines.")

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 26px;">🎯</span>
                <span class="badge-soft-indigo">Core Feature</span>
            </div>
            <h4 style="margin: 0 0 6px 0; font-weight: 700; color: #0F172A;">Form Extraction</h4>
            <p style="font-size: 13.5px; color: #475569; margin-bottom: 16px; min-height: 54px; line-height: 1.5;">
                AI classification (EfficientNetV2B0), optical character recognition and structured JSON key-value extraction.
            </p>
            """, unsafe_allow_html=True)
            if st.button("Open Form Extraction →", key="dash_btn_form", type="primary", use_container_width=True):
                navigate_to("Form Extraction")

    with c2:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 26px;">🧠</span>
                <span class="badge-soft-success">PhoBERT + LLM</span>
            </div>
            <h4 style="margin: 0 0 6px 0; font-weight: 700; color: #0F172A;">AI Document Processing</h4>
            <p style="font-size: 13.5px; color: #475569; margin-bottom: 16px; min-height: 54px; line-height: 1.5;">
                Classify documents locally with fine-tuned Vietnamese PhoBERT transformer, analyze terms and chat with PDF.
            </p>
            """, unsafe_allow_html=True)
            if st.button("Open Document AI →", key="dash_btn_doc", type="primary", use_container_width=True):
                navigate_to("AI Document Processing")

    with c3:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 26px;">💬</span>
                <span class="badge-soft-warning">RAG + FAISS</span>
            </div>
            <h4 style="margin: 0 0 6px 0; font-weight: 700; color: #0F172A;">Document Q&A</h4>
            <p style="font-size: 13.5px; color: #475569; margin-bottom: 16px; min-height: 54px; line-height: 1.5;">
                Vector index multiple PDF knowledge bases with FAISS and perform context-grounded conversational search.
            </p>
            """, unsafe_allow_html=True)
            if st.button("Open Document Q&A →", key="dash_btn_rag", type="primary", use_container_width=True):
                navigate_to("Document Q&A")

# =========================================================
# 6. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    # Branding Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
        <div style="background: #4F46E5; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 18px;">
            S
        </div>
        <div>
            <div style="font-weight: 800; font-size: 16px; color: #0F172A; letter-spacing: -0.02em; line-height: 1.2;">SmartDoc AI</div>
            <div style="font-size: 11px; color: #64748B; font-weight: 500;">Intelligent Document Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Determine Group
    current_feat = st.session_state.current_nav_feature

    group_names = list(NAVIGATION_GROUPS.keys())
    default_grp_idx = 0
    for idx, grp in enumerate(group_names):
        if current_feat in NAVIGATION_GROUPS[grp]:
            default_grp_idx = idx
            break

    selected_group = st.selectbox(
        "Navigation Group",
        group_names,
        index=default_grp_idx,
        key="selected_nav_group"
    )

    feature_options = list(NAVIGATION_GROUPS[selected_group].keys())

    def format_nav_item(name):
        meta = NAVIGATION_GROUPS[selected_group].get(name, {})
        return f"{meta.get('icon', '📄')}  {name}"

    current_idx = 0
    if current_feat in feature_options:
        current_idx = feature_options.index(current_feat)

    selected_feature = st.radio(
        "Feature",
        feature_options,
        index=current_idx,
        format_func=format_nav_item,
        label_visibility="collapsed",
        key="feature_nav_radio"
    )

    if selected_feature != st.session_state.current_nav_feature:
        st.session_state.current_nav_feature = selected_feature
        st.rerun()

    # Feature Context Tooltip Card
    active_meta = NAVIGATION_GROUPS[selected_group][selected_feature]
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 12px; margin-top: 12px;">
        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #4F46E5; margin-bottom: 3px;">
            {selected_group}
        </div>
        <div style="font-size: 12.5px; color: #475569; line-height: 1.45;">
            {active_meta.get('desc', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Compact Collapsible System Status Section
    render_sidebar_system_status()

    st.caption(f"<p style='font-size: 11px; color: #94A3B8; text-align: center; margin-top: 14px;'>SmartDoc AI SaaS © {datetime.now().year}</p>", unsafe_allow_html=True)

# =========================================================
# 7. ROUTER EXECUTION
# =========================================================
active_feature = st.session_state.current_nav_feature
route_found = False

for grp, feats in NAVIGATION_GROUPS.items():
    if active_feature in feats:
        feats[active_feature]["route"]()
        route_found = True
        break

if not route_found:
    st.error(f"Route not configured for: {active_feature}")
