# File: ui_modules/converter_ui.py
import streamlit as st
import tempfile
import os
from logic.converter_logic import images_to_pdf, pdf_to_word, word_to_pdf

def show_converter_ui():  # <--- TÊN HÀM PHẢI CHÍNH XÁC NHƯ THẾ NÀY
    st.header("🛠️ Công cụ Chuyển đổi Tài liệu (Local)")
    
    tab1, tab2, tab3 = st.tabs(["🖼️ Ảnh sang PDF", "📝 PDF sang Word", "📄 Word sang PDF"])

    # TAB 1: ẢNH -> PDF
    with tab1:
        uploaded_imgs = st.file_uploader("Chọn ảnh (JPG, PNG)", type=['jpg','png','jpeg'], accept_multiple_files=True, key="img2pdf_uploader")
        if uploaded_imgs and st.button("Chuyển sang PDF", key="btn_img2pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                # Gọi hàm logic
                result_path = images_to_pdf(uploaded_imgs, tmp.name)
                
                with open(result_path, "rb") as f:
                    st.download_button("⬇️ Tải file PDF", f, file_name="converted_images.pdf", mime="application/pdf")

    # TAB 2: PDF -> WORD
    with tab2:
        uploaded_pdf = st.file_uploader("Chọn file PDF", type=['pdf'], key="pdf2word_uploader")
        if uploaded_pdf and st.button("Chuyển sang Word", key="btn_pdf2word"):
            with st.spinner("Đang chuyển đổi... (Có thể mất vài giây)"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
                    tmp_in.write(uploaded_pdf.read())
                    input_path = tmp_in.name
                
                output_path = input_path.replace(".pdf", ".docx")
                
                try:
                    pdf_to_word(input_path, output_path)
                    
                    with open(output_path, "rb") as f:
                        st.download_button("⬇️ Tải file Word (.docx)", f, file_name="converted_doc.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    # TAB 3: WORD -> PDF
    with tab3:
        st.info("Tính năng này yêu cầu máy chủ phải cài đặt Microsoft Word.")
        uploaded_word = st.file_uploader("Chọn file Word (.docx)", type=['docx'], key="word2pdf_uploader")
        if uploaded_word and st.button("Chuyển sang PDF", key="btn_word2pdf"):
             with st.spinner("Đang chuyển đổi..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
                    tmp_in.write(uploaded_word.read())
                    input_path = tmp_in.name
                
                output_path = input_path.replace(".docx", ".pdf")
                
                try:
                    res = word_to_pdf(input_path, output_path)
                    if res:
                        with open(res, "rb") as f:
                            st.download_button("⬇️ Tải file PDF", f, file_name="converted_word.pdf", mime="application/pdf")
                    else:
                        st.error("Server không hỗ trợ thư viện docx2pdf hoặc không có MS Word.")
                except Exception as e:
                    st.error(f"Lỗi: {e}")