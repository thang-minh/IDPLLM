# ui_modules/converter_ui.py
import streamlit as st
import tempfile
import os
from logic.converter_logic import images_to_pdf, pdf_to_word, word_to_pdf

def show_converter_ui():
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-soft-indigo">Document Tools</span>
                <span class="badge-soft-success">Offline Converter</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em; color: #0F172A;">Chuyển đổi Định dạng Tài liệu (Local)</h2>
            <p style="color: #475569; font-size: 14px; margin: 4px 0 0 0;">
                Chuyển đổi tốc độ cao giữa các định dạng Ảnh, PDF và tài liệu Microsoft Word hoàn toàn trên máy cục bộ.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🖼️ Ghép Ảnh sang PDF", "📝 PDF sang Word (.docx)", "📄 Word sang PDF"])

    # TAB 1: ẢNH -> PDF
    with tab1:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">Ghép nhiều ảnh thành tài liệu PDF</span>
                <span class="badge-soft-neutral">IMG ➔ PDF</span>
            </div>
            """, unsafe_allow_html=True)

            uploaded_imgs = st.file_uploader(
                "Chọn hoặc kéo thả các tệp ảnh (JPG, PNG, JPEG):",
                type=['jpg', 'png', 'jpeg'],
                accept_multiple_files=True,
                key="img2pdf_uploader"
            )

            if uploaded_imgs:
                st.markdown(f"Đã chọn **{len(uploaded_imgs)}** tệp ảnh.")
                if st.button("🚀 Chuyển đổi sang PDF", key="btn_img2pdf", type="primary", use_container_width=True):
                    with st.spinner("Đang kết hợp và đóng gói ảnh thành file PDF..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                result_path = images_to_pdf(uploaded_imgs, tmp.name)

                            with open(result_path, "rb") as f:
                                st.download_button(
                                    "📥 Tải xuống tập tin PDF hoàn tất",
                                    f,
                                    file_name="converted_images.pdf",
                                    mime="application/pdf",
                                    type="primary",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Lỗi chuyển đổi ảnh: {e}")

    # TAB 2: PDF -> WORD
    with tab2:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">Chuyển đổi PDF sang Microsoft Word</span>
                <span class="badge-soft-indigo">PDF ➔ DOCX</span>
            </div>
            """, unsafe_allow_html=True)

            uploaded_pdf = st.file_uploader(
                "Tải lên tệp PDF cần chuyển đổi sang Word:",
                type=['pdf'],
                key="pdf2word_uploader"
            )

            if uploaded_pdf:
                if st.button("🚀 Bắt đầu Chuyển đổi sang .DOCX", key="btn_pdf2word", type="primary", use_container_width=True):
                    with st.status("Đang phân tích layout và tái tạo định dạng Word...", expanded=True) as status:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                                tmp_in.write(uploaded_pdf.read())
                                input_path = tmp_in.name

                            output_path = input_path.replace(".pdf", ".docx")
                            status.write("Đang ánh xạ cấu trúc bảng và văn bản...")
                            pdf_to_word(input_path, output_path)

                            status.update(label="✓ Chuyển đổi sang Word thành công!", state="complete", expanded=False)

                            with open(output_path, "rb") as f:
                                st.download_button(
                                    "📥 Tải xuống tệp Word (.docx)",
                                    f,
                                    file_name=f"{uploaded_pdf.name.rsplit('.', 1)[0]}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    type="primary",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Lỗi chuyển đổi PDF sang Word: {e}")

    # TAB 3: WORD -> PDF
    with tab3:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">Chuyển đổi Microsoft Word sang PDF</span>
                <span class="badge-soft-neutral">DOCX ➔ PDF</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 10px 12px; margin-bottom: 12px; font-size: 13px; color: #1E40AF;">
                ℹ️ Tính năng này sử dụng COM Automation trên Windows và yêu cầu hệ thống đã cài đặt Microsoft Word.
            </div>
            """, unsafe_allow_html=True)

            uploaded_word = st.file_uploader(
                "Tải lên tệp Word (.docx):",
                type=['docx'],
                key="word2pdf_uploader"
            )

            if uploaded_word:
                if st.button("🚀 Chuyển đổi sang PDF", key="btn_word2pdf", type="primary", use_container_width=True):
                    with st.spinner("Đang kết xuất tệp PDF từ Word..."):
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
                                tmp_in.write(uploaded_word.read())
                                input_path = tmp_in.name

                            output_path = input_path.replace(".docx", ".pdf")
                            res = word_to_pdf(input_path, output_path)

                            if res and os.path.exists(res):
                                with open(res, "rb") as f:
                                    st.download_button(
                                        "📥 Tải xuống tệp PDF",
                                        f,
                                        file_name=f"{uploaded_word.name.rsplit('.', 1)[0]}.pdf",
                                        mime="application/pdf",
                                        type="primary",
                                        use_container_width=True
                                    )
                            else:
                                st.warning("Không thể xuất file PDF. Hãy đảm bảo máy tính đã cài đặt Microsoft Word.")
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
