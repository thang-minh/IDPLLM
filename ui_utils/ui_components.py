# ui_utils/ui_components.py
import os
import streamlit as st
import pytesseract

def get_runtime_system_status():
    """
    Kiểm tra trạng thái thời gian thực của các dịch vụ và mô hình trong hệ thống.
    Tuyệt đối không dùng dữ liệu giả lập (mock data).
    """
    # 1. OCR Engine
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    tesseract_online = False
    if tesseract_cmd and os.path.exists(tesseract_cmd):
        tesseract_online = True
    elif os.name == "nt":
        for path in [r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]:
            if os.path.exists(path):
                tesseract_online = True
                break

    # 2. LLM Engine (Groq / OpenRouter)
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    llm_configured = bool(groq_key or openrouter_key)

    # 3. Poppler PDF Engine
    poppler_env = os.getenv("POPPLER_PATH")
    poppler_available = bool(poppler_env and os.path.exists(poppler_env))

    # 4. EfficientNetV2B0 Checkpoint
    model_path = os.path.join("models", "model_AI_documen", "best_document_image_classifier_2classes.keras")
    efficientnet_loaded = os.path.exists(model_path)

    # 5. PhoBERT Model Dir
    phobert_dir = os.path.join("models", "phobert_classifier")
    phobert_available = os.path.exists(phobert_dir)

    return {
        "ocr": tesseract_online,
        "llm": llm_configured,
        "poppler": poppler_available,
        "efficientnet": efficientnet_loaded,
        "phobert": phobert_available,
    }

def render_status_badge(text: str, status_type: str = "neutral") -> str:
    """
    Tạo Soft Badge chuẩn Linear & Stripe SaaS
    status_type: success (#0D9488), warning (#F59E0B), error (#EF4444), info (#3B82F6), indigo (#4F46E5), neutral (#475569)
    """
    badge_classes = {
        "success": "badge-soft-success",
        "warning": "badge-soft-warning",
        "error": "badge-soft-danger",
        "info": "badge-soft-info",
        "indigo": "badge-soft-indigo",
        "neutral": "badge-soft-neutral",
    }
    cls = badge_classes.get(status_type, "badge-soft-neutral")
    return f'<span class="{cls}">{text}</span>'

def render_page_header(title: str, description: str, badges: list = None, breadcrumb: str = None):
    """
    Header chuẩn SaaS đồng bộ trên tất cả các trang
    """
    badges_html = ""
    if badges:
        rendered = [render_status_badge(b.get("text", ""), b.get("type", "neutral")) for b in badges]
        badges_html = f'<div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">{"".join(rendered)}</div>'

    breadcrumb_html = ""
    if breadcrumb:
        breadcrumb_html = f'<div style="font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #4F46E5; margin-bottom: 4px;">{breadcrumb}</div>'

    header_html = f"""
    <div style="margin-bottom: 1.25rem;">
        {breadcrumb_html}
        {badges_html}
        <h2 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.025em; color: #0F172A;">{title}</h2>
        <p style="color: #475569; font-size: 14.5px; margin: 4px 0 0 0; line-height: 1.5;">{description}</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_pipeline_stepper(steps: list, current_step: int):
    """
    Bộ chỉ báo tiến trình 3 bước chuyên nghiệp (Dynamic Stepper)
    steps: [("1. Tải lên tài liệu", 1), ("2. Phân loại & OCR", 2), ("3. Trích xuất JSON", 3)]
    """
    html_parts = []
    for label, step_idx in steps:
        if step_idx < current_step:
            cls = "pipeline-step completed"
            icon = "✓"
        elif step_idx == current_step:
            cls = "pipeline-step active"
            icon = "●"
        else:
            cls = "pipeline-step"
            icon = "○"
        html_parts.append(f'<span class="{cls}">{icon} {label}</span>')

    separator = '<span class="pipeline-separator"> ➔ </span>'
    bar_html = f'<div class="pipeline-step-bar">{separator.join(html_parts)}</div>'
    st.markdown(bar_html, unsafe_allow_html=True)

def render_empty_state(icon: str = "📂", title: str = "Chưa có tài liệu nào được chọn", description: str = "Vui lòng tải lên một tệp tài liệu để hệ thống bắt đầu quy trình xử lý AI."):
    """
    Empty state gọn gàng, thanh lịch, tránh vùng trống quá lớn
    """
    html = f"""
    <div style="background-color: #FFFFFF; border: 1.5px dashed #CBD5E1; border-radius: 12px; padding: 2.25rem 1.5rem; text-align: center; margin: 1rem 0;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <div style="font-weight: 700; color: #0F172A; font-size: 15px;">{title}</div>
        <div style="color: #64748B; font-size: 13.5px; max-width: 440px; margin: 4px auto 0 auto; line-height: 1.5;">{description}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar_system_status():
    """
    Khung trạng thái hệ thống rút gọn ở cuối thanh Sidebar
    """
    status = get_runtime_system_status()
    ocr_badge = '<span class="badge-soft-success">● Online</span>' if status["ocr"] else '<span class="badge-soft-danger">○ Offline</span>'
    llm_badge = '<span class="badge-soft-indigo">● Configured</span>' if status["llm"] else '<span class="badge-soft-danger">○ Missing</span>'
    model_badge = '<span class="badge-soft-success">● Ready</span>' if status["efficientnet"] else '<span class="badge-soft-warning">○ Not Loaded</span>'
    poppler_badge = '<span class="badge-soft-neutral">● Ready</span>' if status["poppler"] else '<span class="badge-soft-neutral">○ Standard</span>'

    with st.expander("⚡ System Status", expanded=False):
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12.5px; padding-top: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #475569; font-weight: 500;">OCR Engine</span>
                {ocr_badge}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #475569; font-weight: 500;">LLM Service</span>
                {llm_badge}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #475569; font-weight: 500;">EfficientNet</span>
                {model_badge}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #475569; font-weight: 500;">Poppler PDF</span>
                {poppler_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)

