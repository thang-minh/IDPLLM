# ui_modules/compare_module_ui.py
import streamlit as st
import io

from logic.compare_logic import extract_text_from_image_for_compare, compare_texts_to_html
from ui_utils.fun_meme import display_random_meme

def show_compare_module_ui():
    # Header chuẩn SaaS
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-soft-indigo">Visual Diff</span>
                <span class="badge-soft-success">OCR Comparison</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em; color: #0F172A;">So sánh Nội dung Tài liệu (Ảnh)</h2>
            <p style="color: #475569; font-size: 14px; margin: 4px 0 0 0;">
                Tải lên 2 phiên bản ảnh chụp/scan của tài liệu để OCR và so sánh từng ký tự khác biệt (Diff Viewer).
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if 'cm_text1' not in st.session_state: st.session_state.cm_text1 = ""
    if 'cm_text2' not in st.session_state: st.session_state.cm_text2 = ""
    if 'cm_comparison_html' not in st.session_state: st.session_state.cm_comparison_html = None
    if 'cm_last_file1_name' not in st.session_state: st.session_state.cm_last_file1_name = None
    if 'cm_last_file2_name' not in st.session_state: st.session_state.cm_last_file2_name = None

    # 2 Cột Upload Tài liệu Song Song
    col1_upload, col2_upload = st.columns(2, gap="medium")

    with col1_upload:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">📄 Tài liệu 1 (Bản gốc / Cũ)</span>
                <span class="badge-soft-neutral">Version A</span>
            </div>
            """, unsafe_allow_html=True)
            file1 = st.file_uploader(
                "Tải lên ảnh tài liệu 1 (JPG, PNG):",
                type=["jpg", "jpeg", "png"],
                key="cm_file1_uploader"
            )
            if file1:
                st.image(file1, caption=f"Tài liệu 1: {file1.name}", use_container_width=True)
                if file1.name != st.session_state.cm_last_file1_name:
                    st.session_state.cm_text1 = ""
                    st.session_state.cm_comparison_html = None
                    st.session_state.cm_last_file1_name = file1.name

    with col2_upload:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">📄 Tài liệu 2 (Bản đối chiếu / Mới)</span>
                <span class="badge-soft-indigo">Version B</span>
            </div>
            """, unsafe_allow_html=True)
            file2 = st.file_uploader(
                "Tải lên ảnh tài liệu 2 (JPG, PNG):",
                type=["jpg", "jpeg", "png"],
                key="cm_file2_uploader"
            )
            if file2:
                st.image(file2, caption=f"Tài liệu 2: {file2.name}", use_container_width=True)
                if file2.name != st.session_state.cm_last_file2_name:
                    st.session_state.cm_text2 = ""
                    st.session_state.cm_comparison_html = None
                    st.session_state.cm_last_file2_name = file2.name

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    if file1 and file2:
        if st.button("🚀 Kích hoạt So sánh Văn bản Hai Ảnh", type="primary", use_container_width=True, key="cm_compare_button"):
            st.session_state.cm_text1 = ""
            st.session_state.cm_text2 = ""
            st.session_state.cm_comparison_html = None

            with st.status("Đang OCR và tính toán điểm khác biệt...", expanded=True) as status:
                ocr_error = False
                try:
                    file1_bytes = io.BytesIO(file1.read())
                    file2_bytes = io.BytesIO(file2.read())
                    status.write("1/3 Quét OCR văn bản tài liệu 1...")
                    st.session_state.cm_text1 = extract_text_from_image_for_compare(file1_bytes, lang='vie+eng')
                except Exception as e1:
                    st.error(f"Lỗi OCR Tài liệu 1: {e1}")
                    ocr_error = True

                try:
                    status.write("2/3 Quét OCR văn bản tài liệu 2...")
                    st.session_state.cm_text2 = extract_text_from_image_for_compare(file2_bytes, lang='vie+eng')
                except Exception as e2:
                    st.error(f"Lỗi OCR Tài liệu 2: {e2}")
                    ocr_error = True

                if not ocr_error and st.session_state.cm_text1.strip() and st.session_state.cm_text2.strip():
                    try:
                        status.write("3/3 Phân tích sự sai khác chuỗi ký tự (Diff Engine)...")
                        st.session_state.cm_comparison_html = compare_texts_to_html(st.session_state.cm_text1, st.session_state.cm_text2)
                        status.update(label="✓ So sánh hoàn tất thành công!", state="complete", expanded=False)
                    except Exception as e_comp:
                        st.error(f"Lỗi tính toán so sánh: {e_comp}")
                elif not ocr_error:
                    status.update(label="Không đủ văn bản sau OCR để so sánh.", state="error")
                    st.warning("Một hoặc cả hai tài liệu không thu được văn bản rõ ràng qua OCR.")

        # Hiển thị Kết quả So sánh
        if st.session_state.cm_comparison_html:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 700; font-size: 15px; color: #0F172A;">📊 Bảng Sai khác Nội dung Chi tiết (HTML Diff)</span>
                    <span class="badge-soft-success">● Đã phát hiện sai khác</span>
                </div>
                """, unsafe_allow_html=True)

                st.components.v1.html(st.session_state.cm_comparison_html, scrolling=True, height=550)

                st.download_button(
                    "📥 Tải xuống Báo cáo So sánh (.HTML)",
                    data=st.session_state.cm_comparison_html.encode("utf-8"),
                    file_name="so_sanh_tai_lieu.html",
                    mime="text/html",
                    type="primary",
                    key="cm_download_html_button",
                    use_container_width=True
                )

            with st.expander("📝 Đối chiếu chi tiết văn bản thô (Raw OCR Text)"):
                col_txt1, col_txt2 = st.columns(2)
                with col_txt1:
                    st.text_area("Văn bản Tài liệu 1:", st.session_state.cm_text1, height=220, key="cm_text1_display")
                with col_txt2:
                    st.text_area("Văn bản Tài liệu 2:", st.session_state.cm_text2, height=220, key="cm_text2_display")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            display_random_meme()

    elif not file1 and not file2:
        st.info("Vui lòng tải lên cả hai tập tin ảnh để kích hoạt công cụ so sánh.")
