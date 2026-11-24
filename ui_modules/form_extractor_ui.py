# ui_modules/form_extractor_ui.py
import asyncio
import json
import os
import pandas as pd
import streamlit as st
from PIL import Image

from logic.common_processing import extract_text_from_image_pil
from logic.form_extractor_logic import parse_text_with_groq_form
from logic.local_model_logic import predict_image_type, clear_local_model_cache
from ui_utils.fun_meme import display_random_meme
from ui_utils.ui_components import (
    get_runtime_system_status,
    render_page_header,
    render_pipeline_stepper,
    render_empty_state,
)

# =========================================================
# HELPER FUNCTIONS & STATE
# =========================================================

def init_form_extractor_state():
    defaults = {
        "fe_ocr_text": "",
        "fe_ai_result": None,
        "fe_local_pred": None,
        "fe_last_filename": None,
        "fe_manual_label": None,
        "fe_preprocess_ocr": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_form_extractor_state(filename=None):
    st.session_state.fe_ocr_text = ""
    st.session_state.fe_ai_result = None
    st.session_state.fe_local_pred = None
    st.session_state.fe_manual_label = None
    st.session_state.fe_last_filename = filename

def build_ai_context_prompt(ocr_text, local_pred, manual_label):
    local_label = "Không xác định"
    local_conf = 0.0

    if local_pred and "error" not in local_pred:
        local_label = local_pred.get("display_label", "Không xác định")
        local_conf = local_pred.get("confidence", 0.0)

    final_label = manual_label.replace("_", " ") if manual_label else local_label

    prompt = f"""
THÔNG TIN PHÂN LOẠI ẢNH CỤC BỘ:
- Mô hình: EfficientNetV2B0 fine-tuned
- Phân loại dự đoán: {local_label}
- Độ tin cậy: {local_conf:.2f}%
- Nhãn xác nhận: {final_label}

NỘI DUNG VĂN BẢN TỪ OCR:
{ocr_text}

YÊU CẦU:
Hãy trích xuất thông tin quan trọng từ tài liệu trên và trả về định dạng JSON thuần túy (không markdown bọc ngoài).
Nếu là Hóa đơn:
- loai_giay_to: "Hóa đơn"
- ten_ben_ban
- ten_ben_mua
- ma_so_thue
- so_hoa_don
- ngay_lap
- tong_tien
- thue_gtgt
- danh_sach_hang_hoa (danh sách các đối tượng gồm ten_hang, so_luong, don_gia, thanh_tien)

Nếu là Sơ yếu lý lịch:
- loai_giay_to: "Sơ yếu lý lịch"
- ho_ten
- ngay_sinh
- que_quan
- dia_chi_thuong_tru
- so_cccd_cmnd
- trinh_do_hoc_van
- kinh_nghiem_chinh

Nếu là tài liệu khác:
- loai_giay_to
- cac_truong_thong_tin_chinh
"""
    return prompt

# =========================================================
# MAIN DOCUMENT EXTRACTION UI (HIGHEST PRIORITY)
# =========================================================

def show_form_extractor_ui(api_key):
    init_form_extractor_state()
    sys_status = get_runtime_system_status()

    # A. Page Header (Mục 6.A)
    badges = [
        {"text": "● EfficientNetV2B0 Ready" if sys_status["efficientnet"] else "○ Model Missing", "type": "success" if sys_status["efficientnet"] else "warning"},
        {"text": "● OCR Online" if sys_status["ocr"] else "○ OCR Offline", "type": "success" if sys_status["ocr"] else "error"},
        {"text": "● LLM Configured" if sys_status["llm"] else "○ LLM Missing", "type": "indigo" if sys_status["llm"] else "error"},
    ]
    render_page_header(
        title="Document Extraction",
        description="Extract structured information from forms and documents using AI-powered classification, OCR and LLM.",
        breadcrumb="AI DOCUMENT / FORM EXTRACTION",
        badges=badges
    )

    # B. Processing Pipeline Stepper (Mục 6.B)
    current_step = 1
    if st.session_state.fe_local_pred is not None:
        current_step = 2
    if st.session_state.fe_ai_result is not None:
        current_step = 3

    steps = [
        ("Step 1: Upload Document", 1),
        ("Step 2: Classification & OCR", 2),
        ("Step 3: Structured JSON Extraction", 3)
    ]
    render_pipeline_stepper(steps, current_step)

    # D. Model Configuration (Mục 6.D)
    with st.expander("⚙️ EfficientNetV2B0 Model Configuration", expanded=False):
        c_cfg1, c_cfg2 = st.columns([3, 1])
        with c_cfg1:
            st.markdown("**Architecture:** `EfficientNetV2B0 Fine-tuned (Local Inference)`")
            st.markdown("**Checkpoint:** `models/model_AI_documen/best_document_image_classifier_2classes.keras`")
            st.markdown("**Classes:** `Hóa đơn (Invoice)`, `Sơ yếu lý lịch (Resume)`")
        with c_cfg2:
            if st.button("Reload Model Cache", key="fe_btn_reload_cache", use_container_width=True):
                clear_local_model_cache()
                st.session_state.fe_local_pred = None
                st.success("Cache cleared successfully.")
                st.rerun()

    # C. Upload Section (Mục 6.C)
    uploaded_image_file = st.file_uploader(
        "Kéo thả hoặc duyệt ảnh tài liệu:",
        type=["jpg", "jpeg", "png"],
        key="fe_image_uploader",
        help="Hỗ trợ các định dạng hình ảnh: JPG, PNG, JPEG. Kích thước khuyến nghị dưới 20MB."
    )

    # E. Empty State (Mục 6.E)
    if not uploaded_image_file:
        render_empty_state(
            icon="📄",
            title="No documents selected",
            description="Hãy tải lên một tệp ảnh tài liệu (Hóa đơn, Sơ yếu lý lịch, CCCD) để hệ thống tự động nhận diện và trích xuất cấu trúc dữ liệu."
        )
        return

    # Quản lý đổi file
    if uploaded_image_file.name != st.session_state.fe_last_filename:
        reset_form_extractor_state(uploaded_image_file.name)

    try:
        image = Image.open(uploaded_image_file)
        preview_image = image.convert("RGB")
    except Exception as e:
        st.error(f"Lỗi không thể mở file ảnh: {e}")
        return

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # =========================================================
    # G. EXTRACTION RESULTS & WORKBENCH (Mục 6.G: TWO-COLUMN LAYOUT)
    # =========================================================
    col_preview, col_workbench = st.columns([1, 1.25], gap="large")

    # LEFT COLUMN: Document Preview & Info (Mục 6.G - Left column)
    with col_preview:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">🖼️ Document Preview</span>
                <span class="badge-soft-neutral">{uploaded_image_file.name}</span>
            </div>
            """, unsafe_allow_html=True)

            st.image(preview_image, use_container_width=True)

            # Metadata info bar
            file_kb = len(uploaded_image_file.getvalue()) / 1024
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding-top: 8px; border-top: 1px solid #E2E8F0; font-size: 12px; color: #64748B;">
                <span>Resolution: <b>{image.size[0]} × {image.size[1]} px</b></span>
                <span>Mode: <b>{image.mode}</b></span>
                <span>Size: <b>{file_kb:.1f} KB</b></span>
            </div>
            """, unsafe_allow_html=True)

    # RIGHT COLUMN: Extracted info, JSON, actions (Mục 6.G - Right column)
    with col_workbench:
        # STEP 1: CLASSIFICATION
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">1. Classification (EfficientNetV2B0)</span>
                <span class="badge-soft-indigo">Step 2.1</span>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.fe_local_pred is None:
                st.caption("Khởi chạy mô hình mạng nơ-ron tích chập để nhận dạng loại tài liệu.")
                if st.button("🚀 Run Classification", key="fe_btn_classify", type="primary", use_container_width=True):
                    with st.status("Analyzing image features with EfficientNetV2B0...", expanded=True) as status:
                        st.session_state.fe_local_pred = predict_image_type(image)
                        status.update(label="✓ Classification completed!", state="complete", expanded=False)
                    st.rerun()
            else:
                pred = st.session_state.fe_local_pred
                if "error" in pred:
                    st.error(f"Classification Error: {pred['error']}")
                else:
                    conf = pred.get("confidence", 0.0)
                    disp_label = pred.get("display_label", pred.get("label", "Unknown"))
                    raw_label = pred.get("label", "")

                    c_m1, c_m2 = st.columns([1.6, 1])
                    with c_m1:
                        st.markdown(f"""
                        <div style="margin-top: 2px;">
                            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700; letter-spacing: 0.05em;">Predicted Category</div>
                            <div style="font-size: 20px; font-weight: 800; color: #4F46E5;">{disp_label}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with c_m2:
                        st.metric("Confidence", f"{conf:.1f}%")

                    st.progress(min(conf / 100.0, 1.0), text=f"Model Confidence: {conf:.1f}%")

                    details = pred.get("details", {})
                    st.session_state.fe_manual_label = st.selectbox(
                        "Confirm or adjust document label:",
                        options=list(details.keys()) if details else [raw_label],
                        index=list(details.keys()).index(raw_label) if (details and raw_label in details) else 0,
                        format_func=lambda x: x.replace("_", " ").title(),
                        key="fe_manual_label_select"
                    )

        # STEP 2: OCR & LLM PIPELINE
        if st.session_state.fe_local_pred is not None:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 14px; color: #0F172A;">2. OCR & Structured LLM Extraction</span>
                    <span class="badge-soft-success">Step 2.2 & 3</span>
                </div>
                """, unsafe_allow_html=True)

                st.session_state.fe_preprocess_ocr = st.checkbox(
                    "Enable Image Preprocessing (Adaptive Contrast & Denoise)",
                    value=st.session_state.fe_preprocess_ocr
                )

                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    run_ocr = st.button("Run OCR Only", key="fe_btn_ocr", use_container_width=True)
                with c_b2:
                    run_pipeline = st.button("Extract JSON (Full Pipeline) →", key="fe_btn_full", type="primary", use_container_width=True)

                if run_ocr or run_pipeline:
                    with st.status("Processing OCR with Tesseract Engine...", expanded=False) as ocr_status:
                        try:
                            st.session_state.fe_ocr_text = extract_text_from_image_pil(
                                image,
                                lang="vie",
                                preprocess=st.session_state.fe_preprocess_ocr
                            )
                            ocr_status.update(label="✓ Optical Character Recognition completed!", state="complete")
                        except Exception as e:
                            st.error(f"OCR Exception: {e}")

                if run_pipeline:
                    if not api_key:
                        st.error("LLM API Key missing in environment (.env).")
                    elif not st.session_state.fe_ocr_text.strip():
                        st.warning("OCR returned empty text. Cannot extract structured data.")
                    else:
                        with st.status("LLM is synthesizing structured JSON...", expanded=True) as llm_status:
                            try:
                                final_label = st.session_state.get("fe_manual_label_select")
                                prompt_text = build_ai_context_prompt(
                                    ocr_text=st.session_state.fe_ocr_text,
                                    local_pred=st.session_state.fe_local_pred,
                                    manual_label=final_label
                                )
                                parsed_res = asyncio.run(
                                    parse_text_with_groq_form(api_key, prompt_text)
                                )
                                st.session_state.fe_ai_result = parsed_res
                                llm_status.update(label="✓ Structured data extraction completed!", state="complete", expanded=False)
                            except Exception as e:
                                st.error(f"LLM Extraction Error: {e}")
                        st.rerun()

        # STEP 3: STRUCTURED OUTPUT & ACTIONS (Mục 6.G)
        if st.session_state.fe_ai_result or st.session_state.fe_ocr_text:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 14px; color: #0F172A;">3. Extraction Output</span>
                    <span class="badge-soft-indigo">Structured Data</span>
                </div>
                """, unsafe_allow_html=True)

                tab_table, tab_json, tab_ocr = st.tabs(["📊 Structured Fields", "🧾 JSON Output", "📝 Raw OCR Text"])

                with tab_table:
                    res = st.session_state.fe_ai_result
                    if res and isinstance(res, dict):
                        flat_rows = []
                        for k, v in res.items():
                            if not isinstance(v, (dict, list)):
                                label_k = str(k).replace("_", " ").title()
                                flat_rows.append({"Field Name": label_k, "Value": str(v)})

                        if flat_rows:
                            st.dataframe(pd.DataFrame(flat_rows), use_container_width=True, hide_index=True)

                        for list_key in ["danh_sach_hang_hoa", "items", "san_pham"]:
                            if list_key in res and isinstance(res[list_key], list):
                                st.markdown(f"**Items Breakdown ({list_key}):**")
                                st.dataframe(pd.DataFrame(res[list_key]), use_container_width=True)
                    else:
                        st.info("Nhấn 'Extract JSON (Full Pipeline)' để trích xuất các trường dữ liệu có cấu trúc.")

                with tab_json:
                    if res:
                        st.json(res)
                        json_str = json.dumps(res, ensure_ascii=False, indent=2)

                        # Copy JSON and Download JSON Actions (Mục 6.G)
                        col_copy, col_dl = st.columns(2)
                        with col_copy:
                            st.text_area("JSON Payload (Ready to copy):", value=json_str, height=120, key="fe_copy_json_area")
                        with col_dl:
                            st.download_button(
                                label="📥 Download JSON",
                                data=json_str,
                                file_name=f"extract_{uploaded_image_file.name.rsplit('.', 1)[0]}.json",
                                mime="application/json",
                                type="primary",
                                use_container_width=True
                            )

                with tab_ocr:
                    st.text_area(
                        "Raw OCR Transcription:",
                        value=st.session_state.fe_ocr_text,
                        height=240,
                        help="Dữ liệu thô thu được từ động cơ Tesseract OCR."
                    )

    if st.session_state.fe_ai_result:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        display_random_meme()
