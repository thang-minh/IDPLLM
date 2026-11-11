# ui_modules/main_smartdoc_ui.py
import streamlit as st
import tempfile
import os
import asyncio

from logic.common_processing import (
    convert_pdf_to_txt,
    convert_pdf_to_images,
    extract_text_from_list_of_images,
    generate_groq_response
)
from logic.document_classifier_logic import classify_document_phobert
from ui_utils.fun_meme import display_random_meme

# =========================================================
# HELPER FUNCTIONS & PIPELINE TRACKER
# =========================================================

def render_pipeline_tracker(current_step: int):
    steps = [
        ("1. Nguồn PDF / Text", 1),
        ("2. PhoBERT Phân loại", 2),
        ("3. Phân tích Sâu LLM", 3)
    ]
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

def build_llm_document_analysis_prompt(text: str, phobert_result: dict):
    label = "Không xác định"
    confidence = 0.0

    if phobert_result and "error" not in phobert_result:
        label = phobert_result.get("display_label", "Không xác định")
        confidence = phobert_result.get("confidence", 0.0) * 100

    text_for_llm = text[:12000]

    prompt = f"""
Bạn là chuyên gia phân tích tài liệu số cao cấp.

Thông tin từ mô hình phân loại cục bộ:
- Mô hình: PhoBERT fine-tuned
- Phân loại dự đoán: {label}
- Độ tin cậy: {confidence:.2f}%

Nhiệm vụ:
Hãy phân tích nội dung tài liệu bên dưới và cấu trúc câu trả lời theo đúng định dạng Markdown sắc sảo sau:

### 1. Nhận định & So khớp
- Đánh giá loại tài liệu và mức độ tương thích với dự đoán của mô hình PhoBERT.

### 2. Tóm tắt Nội dung Cốt lõi
Tóm tắt ngắn gọn trong 4-6 gạch đầu dòng rõ ràng, tập trung vào các ý chính.

### 3. Các Thực thể & Dữ liệu Quan trọng
Trích xuất theo dạng bảng hoặc danh sách có cấu trúc:
- Nếu là Hóa đơn: Tên bên bán, bên mua, MST, số hóa đơn, ngày phát hành, tổng thanh toán, thuế GTGT.
- Nếu là Hợp đồng: Đại diện các bên, chức danh, ngày hiệu lực, giá trị hợp đồng/lương, các điều khoản trọng yếu.
- Nếu là Biên bản/Thông báo: Địa điểm, người tham dự, nội dung thảo luận, các quyết nghị/hành động tiếp theo.

### 4. Đánh giá Chất lượng Văn bản & OCR
Đánh giá độ toàn vẹn của văn bản, cảnh báo nếu có lỗi chính tả hoặc thiếu sót trang.

### 5. Khuyến nghị Xử lý Tiếp theo
3-4 hành động thiết thực cho người quản trị.

NỘI DUNG TÀI LIỆU:
{text_for_llm}
"""
    return prompt

# =========================================================
# MAIN SMARTDOC UI (PDF & PHOBERT PIPELINE)
# =========================================================

def show_main_smartdoc_ui(api_key, poppler_path_env):
    # SaaS Header
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="saas-badge saas-badge-indigo">NLP Document Intelligence</span>
                <span class="saas-badge saas-badge-success">PhoBERT Fine-tuned</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em;">Trí tuệ Tài liệu & Phân loại PhoBERT</h2>
            <p style="color: #64748B; font-size: 14px; margin: 4px 0 0 0;">
                Quy trình 3 bước: Nguồn PDF/Văn bản ➔ Trích xuất văn bản & Phân loại PhoBERT local ➔ LLM phân tích sâu & Đối thoại.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # State defaults
    defaults = {
        "msd_input_mode": "Upload PDF",
        "msd_full_text": "",
        "msd_preview_images": [],
        "msd_phobert_result": None,
        "msd_ai_results": None,
        "msd_last_filename": None,
        "msd_local_done": False,
        "msd_llm_done": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Tính step hiện tại cho Tracker
    current_step = 1
    if st.session_state.msd_local_done:
        current_step = 2
    if st.session_state.msd_llm_done:
        current_step = 3

    render_pipeline_tracker(current_step)

    # =========================================================
    # SPLIT VIEW 2 CỘT NGANG HÀNG
    # CỘT TRÁI: CHỌN NGUỒN, PREVIEW PDF, TEXT NGUYÊN BẢN
    # CỘT PHẢI: KẾT QUẢ PHOBERT LOCAL & PHÂN TÍCH SÂU LLM
    # =========================================================
    col_source, col_insights = st.columns([1, 1.25], gap="large")

    with col_source:
        # 1. Chọn nguồn dữ liệu
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px;">1. Chọn nguồn tài liệu</span>
                <span class="saas-badge saas-badge-indigo">Input</span>
            </div>
            """, unsafe_allow_html=True)

            input_mode = st.radio(
                "Định dạng đầu vào:",
                ["Upload PDF", "Nhập văn bản trực tiếp"],
                horizontal=True,
                key="msd_input_mode_radio"
            )

            if input_mode != st.session_state.msd_input_mode:
                for key, val in defaults.items():
                    st.session_state[key] = val
                st.session_state.msd_input_mode = input_mode
                st.rerun()

            uploaded_file = None
            manual_text = ""

            if input_mode == "Upload PDF":
                uploaded_file = st.file_uploader(
                    "Tải lên tập tin PDF:",
                    type="pdf",
                    key="msd_pdf_uploader",
                    help="Hỗ trợ các tài liệu PDF văn bản và PDF scan."
                )
            else:
                manual_text = st.text_area(
                    "Dán nội dung tài liệu tiếng Việt:",
                    height=240,
                    placeholder="Dán nội dung Hợp đồng lao động, Hóa đơn hoặc Biên bản họp vào đây...",
                    key="msd_manual_text_input"
                )

        # 2. Xử lý Preview PDF nếu có
        file_data = None
        if input_mode == "Upload PDF" and uploaded_file is not None:
            if uploaded_file.name != st.session_state.msd_last_filename:
                for key, val in defaults.items():
                    st.session_state[key] = val
                st.session_state.msd_input_mode = input_mode
                st.session_state.msd_last_filename = uploaded_file.name

            file_data = uploaded_file.read()

            # Tạo preview ảnh nếu có Poppler
            if poppler_path_env and not st.session_state.msd_preview_images:
                with st.spinner("Đang kết xuất bản xem trước PDF..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(file_data)
                        temp_path = tmp.name
                    try:
                        st.session_state.msd_preview_images = convert_pdf_to_images(
                            temp_path, 1, 3, poppler_path_env
                        )
                    except Exception:
                        pass
                    finally:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)

            with st.container(border=True):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 14px;">📄 Tài liệu PDF: {uploaded_file.name}</span>
                    <span class="saas-badge saas-badge-success">{len(file_data)/1024:.1f} KB</span>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.msd_preview_images:
                    cols_img = st.columns(len(st.session_state.msd_preview_images))
                    for idx, p_img in enumerate(st.session_state.msd_preview_images):
                        cols_img[idx].image(p_img, caption=f"Trang {idx+1}", use_container_width=True)
                else:
                    st.info("ℹ️ Chế độ trích xuất trực tiếp văn bản qua PyMuPDF (High-speed Direct Extraction).")

        # Khung văn bản trích xuất (nếu đã có text)
        if st.session_state.msd_full_text:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 14px;">📝 Văn bản đã bóc tách</span>
                    <span class="saas-badge saas-badge-indigo">Extracted Text</span>
                </div>
                """, unsafe_allow_html=True)
                st.text_area(
                    "Nội dung văn bản:",
                    value=st.session_state.msd_full_text,
                    height=220,
                    label_visibility="collapsed"
                )

    with col_insights:
        # Kiểm tra điều kiện chạy
        has_content = (input_mode == "Upload PDF" and uploaded_file is not None) or (input_mode == "Nhập văn bản trực tiếp" and manual_text.strip())

        if not has_content:
            st.markdown("""
            <div style="background: rgba(79, 70, 229, 0.03); border: 1px dashed #CBD5E1; border-radius: 12px; padding: 3rem 1.5rem; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 8px;">💡</div>
                <div style="font-weight: 600; color: #0F172A; font-size: 15px;">Sẵn sàng phân loại tài liệu</div>
                <div style="color: #64748B; font-size: 13px; max-width: 420px; margin: 4px auto 0 auto;">
                    Vui lòng tải lên file PDF hoặc dán nội dung văn bản bên cột trái để kích hoạt mô hình PhoBERT.
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        # BƯỚC 2: PHÂN LOẠI PHOBERT LOCAL
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px;">2. Phân loại Mô hình PhoBERT (Local)</span>
                <span class="saas-badge saas-badge-indigo">Offline AI</span>
            </div>
            """, unsafe_allow_html=True)

            if not st.session_state.msd_local_done:
                st.caption("Trích xuất nội dung văn bản và đưa vào mô hình PhoBERT fine-tuned để nhận diện loại tài liệu.")
                if st.button("🚀 Chạy Phân loại PhoBERT", key="btn_run_phobert", type="primary", use_container_width=True):
                    with st.status("Đang phân tích văn bản qua PhoBERT...", expanded=True) as status:
                        try:
                            # 1. Trích xuất text
                            if input_mode == "Upload PDF":
                                st.write("Đang đọc luồng nhị phân PDF (PyMuPDF)...")
                                ext_text = convert_pdf_to_txt(file_data)
                                if len(ext_text.strip()) < 100 and st.session_state.msd_preview_images:
                                    st.write("Văn bản ngắn, kích hoạt OCR bổ sung từ ảnh...")
                                    ocr_text = extract_text_from_list_of_images(
                                        st.session_state.msd_preview_images, "vie", True
                                    )
                                    ext_text = ext_text + "\n" + ocr_text
                                st.session_state.msd_full_text = ext_text.strip()
                            else:
                                st.session_state.msd_full_text = manual_text.strip()

                            if not st.session_state.msd_full_text:
                                st.error("Không tìm thấy nội dung văn bản hợp lệ.")
                                st.stop()

                            st.write("Đang suy luận qua Transformer PhoBERT...")
                            p_result = classify_document_phobert(st.session_state.msd_full_text)
                            st.session_state.msd_phobert_result = p_result
                            st.session_state.msd_local_done = True
                            status.update(label="✓ Phân loại PhoBERT hoàn tất!", state="complete", expanded=False)
                        except Exception as e:
                            st.error(f"Lỗi phân tích: {e}")
                            st.stop()
                    st.rerun()
            else:
                p_res = st.session_state.msd_phobert_result
                if p_res and "error" not in p_res:
                    pred_label = p_res.get("display_label", "N/A")
                    conf = p_res.get("confidence", 0.0) * 100

                    m1, m2 = st.columns([1.5, 1])
                    with m1:
                        st.markdown(f"""
                        <div style="margin-top: 2px;">
                            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 600;">Dự đoán PhoBERT</div>
                            <div style="font-size: 20px; font-weight: 800; color: #4F46E5;">{pred_label}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.metric("Độ tin cậy", f"{conf:.1f}%")

                    # Confidence progress
                    st.progress(min(conf / 100.0, 1.0), text=f"Xác suất lớp chính: {conf:.1f}%")

                    # Phân bổ xác suất từng lớp
                    probs = p_res.get("probabilities", {})
                    if probs:
                        with st.expander("Xem chi tiết xác suất các lớp", expanded=False):
                            for l_name, p_val in probs.items():
                                st.progress(p_val, text=f"{l_name.replace('_', ' ').title()}: {p_val*100:.1f}%")

                    if st.button("Phân loại lại", key="btn_re_phobert", use_container_width=True):
                        st.session_state.msd_local_done = False
                        st.session_state.msd_llm_done = False
                        st.rerun()

        # BƯỚC 3: PHÂN TÍCH SÂU BẰNG LLM
        if st.session_state.msd_local_done:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 14px;">3. Phân tích Sâu & Tương tác (LLM)</span>
                    <span class="saas-badge saas-badge-success">GenAI</span>
                </div>
                """, unsafe_allow_html=True)

                if not st.session_state.msd_llm_done:
                    st.caption("Sử dụng mô hình ngôn ngữ lớn để tóm tắt, trích xuất cấu trúc và giải thích văn bản.")
                    if st.button("🚀 Chạy Phân tích Sâu bằng LLM", key="btn_run_llm_deep", type="primary", use_container_width=True):
                        if not api_key:
                            st.error("Chưa cấu hình API Key trong file .env!")
                        else:
                            with st.spinner("Đang gọi LLM phân tích chuyên sâu..."):
                                try:
                                    prompt = build_llm_document_analysis_prompt(
                                        text=st.session_state.msd_full_text,
                                        phobert_result=st.session_state.msd_phobert_result
                                    )
                                    llm_res = asyncio.run(generate_groq_response(api_key, prompt))
                                    st.session_state.msd_ai_results = {"analysis": llm_res}
                                    st.session_state.msd_llm_done = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Lỗi LLM: {e}")

                if st.session_state.msd_llm_done:
                    tab_analysis, tab_qa, tab_trans = st.tabs([
                        "📊 Phân tích Chi tiết",
                        "💬 Chat với Tài liệu",
                        "🌐 Dịch thuật"
                    ])

                    with tab_analysis:
                        st.markdown(st.session_state.msd_ai_results.get("analysis", ""))
                        if st.button("Làm mới Phân tích", key="btn_refresh_analysis"):
                            st.session_state.msd_llm_done = False
                            st.rerun()

                    with tab_qa:
                        st.markdown("**Hỏi đáp ngữ cảnh dựa trên tài liệu:**")
                        user_q = st.text_input(
                            "Đặt câu hỏi cho tài liệu:",
                            placeholder="Ví dụ: Giá trị hợp đồng là bao nhiêu? Ngày hết hạn khi nào?",
                            key="msd_qa_input"
                        )
                        if st.button("Gửi câu hỏi", key="btn_send_qa", type="primary"):
                            if not user_q.strip():
                                st.warning("Vui lòng nhập câu hỏi.")
                            elif not api_key:
                                st.error("Thiếu API Key.")
                            else:
                                with st.spinner("Đang tìm câu trả lời từ tài liệu..."):
                                    ctx = st.session_state.msd_full_text[:12000]
                                    qa_prompt = f"""
Bạn là trợ lý AI chuyên nghiệp phân tích tài liệu.
Chỉ trả lời dựa trên nội dung được cung cấp bên dưới. Nếu không có thông tin, hãy nói rõ là không có trong tài liệu.

NỘI DUNG:
{ctx}

CÂU HỎI:
{user_q}
"""
                                    ans = asyncio.run(generate_groq_response(api_key, qa_prompt))
                                    st.markdown(f"**Trả lời:**\n\n{ans}")

                    with tab_trans:
                        st.markdown("**Dịch tài liệu sang ngôn ngữ đích:**")
                        c_lang, c_btn = st.columns([2, 1])
                        with c_lang:
                            t_lang = st.selectbox("Ngôn ngữ đích:", ["English", "Japanese", "Chinese", "Korean"], key="msd_trans_lang")
                        with c_btn:
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            run_trans = st.button("Dịch ngay", key="btn_run_trans", use_container_width=True)

                        if run_trans:
                            if not api_key:
                                st.error("Thiếu API Key.")
                            else:
                                with st.spinner(f"Đang dịch sang {t_lang}..."):
                                    tr_prompt = f"Hãy dịch toàn bộ nội dung tài liệu sau sang {t_lang}, giữ cấu trúc văn bản:\n\n{st.session_state.msd_full_text[:6000]}"
                                    tr_res = asyncio.run(generate_groq_response(api_key, tr_prompt))
                                    st.text_area("Bản dịch hoàn tất:", value=tr_res, height=300)

    if st.session_state.msd_llm_done:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        display_random_meme()
