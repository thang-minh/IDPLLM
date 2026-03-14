# ui_modules/compare_module_ui.py
import streamlit as st
import io # Cần cho việc truyền bytes vào hàm logic

# Import các hàm logic từ thư mục logic
from logic.compare_logic import extract_text_from_image_for_compare, compare_texts_to_html
from ui_utils.fun_meme import display_random_meme

def show_compare_module_ui():
    st.markdown("<h1 style='text-align: center;'>🆚 So sánh Nội dung Tài liệu (Ảnh)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên hai ảnh tài liệu để thực hiện OCR và so sánh sự khác biệt trong nội dung văn bản.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if 'cm_text1' not in st.session_state: st.session_state.cm_text1 = ""
    if 'cm_text2' not in st.session_state: st.session_state.cm_text2 = ""
    if 'cm_comparison_html' not in st.session_state: st.session_state.cm_comparison_html = None
    if 'cm_last_file1_name' not in st.session_state: st.session_state.cm_last_file1_name = None
    if 'cm_last_file2_name' not in st.session_state: st.session_state.cm_last_file2_name = None


    col1_upload, col2_upload = st.columns(2)
    with col1_upload:
        with st.container(border=True):
            st.subheader("📂 Tài liệu 1 (Ảnh)")
            file1 = st.file_uploader(
                "Tải lên ảnh tài liệu 1 (JPG, PNG)",
                type=["jpg", "jpeg", "png"],
                key="cm_file1_uploader",
                help="Ảnh đầu tiên để so sánh."
            )
            if file1:
                st.image(file1, caption="Tài liệu 1", use_column_width=True)
                if file1.name != st.session_state.cm_last_file1_name: # Reset nếu file mới
                    st.session_state.cm_text1 = ""
                    st.session_state.cm_comparison_html = None
                    st.session_state.cm_last_file1_name = file1.name


    with col2_upload:
        with st.container(border=True):
            st.subheader("📂 Tài liệu 2 (Ảnh)")
            file2 = st.file_uploader(
                "Tải lên ảnh tài liệu 2 (JPG, PNG)",
                type=["jpg", "jpeg", "png"],
                key="cm_file2_uploader",
                help="Ảnh thứ hai để so sánh."
            )
            if file2:
                st.image(file2, caption="Tài liệu 2", use_column_width=True)
                if file2.name != st.session_state.cm_last_file2_name: # Reset nếu file mới
                    st.session_state.cm_text2 = ""
                    st.session_state.cm_comparison_html = None
                    st.session_state.cm_last_file2_name = file2.name

    st.markdown("---")

    if file1 and file2:
        if st.button("🚀 So sánh Văn bản từ Hai Ảnh", type="primary", use_container_width=True, key="cm_compare_button"):
            st.session_state.cm_text1 = ""
            st.session_state.cm_text2 = ""
            st.session_state.cm_comparison_html = None # Reset kết quả cũ

            ocr_error = False
            with st.spinner("🔍 Đang OCR và so sánh nội dung..."):
                try:
                    # Đọc bytes một lần
                    file1_bytes = io.BytesIO(file1.read())
                    file2_bytes = io.BytesIO(file2.read())
                    
                    st.session_state.cm_text1 = extract_text_from_image_for_compare(file1_bytes, lang='vie+eng')
                except ValueError as ve:
                    st.error(f"Lỗi OCR Tài liệu 1: {ve}")
                    ocr_error = True
                except Exception as e1:
                    st.error(f"Lỗi không mong muốn khi OCR Tài liệu 1: {e1}")
                    ocr_error = True
                
                try:
                    st.session_state.cm_text2 = extract_text_from_image_for_compare(file2_bytes, lang='vie+eng')
                except ValueError as ve:
                    st.error(f"Lỗi OCR Tài liệu 2: {ve}")
                    ocr_error = True
                except Exception as e2:
                    st.error(f"Lỗi không mong muốn khi OCR Tài liệu 2: {e2}")
                    ocr_error = True

                if not ocr_error and st.session_state.cm_text1.strip() and st.session_state.cm_text2.strip():
                    try:
                        st.session_state.cm_comparison_html = compare_texts_to_html(st.session_state.cm_text1, st.session_state.cm_text2)
                        st.success("So sánh hoàn tất!")
                    except Exception as e_comp:
                        st.error(f"Lỗi khi so sánh văn bản: {e_comp}")
                        st.session_state.cm_comparison_html = f"<p>Lỗi khi so sánh: {e_comp}</p>"
                elif not ocr_error:
                    st.warning("Một hoặc cả hai tài liệu không có nội dung văn bản sau OCR để so sánh.")
                    st.session_state.cm_comparison_html = "<p>Không có đủ nội dung để so sánh.</p>"

        if st.session_state.cm_comparison_html:
            st.markdown("---")
            with st.container(border=True):
                st.subheader("📋 Kết quả So sánh Chi tiết (HTML Diff):")
                st.components.v1.html(st.session_state.cm_comparison_html, scrolling=True, height=600)
                st.download_button(
                    "📥 Tải kết quả so sánh (HTML)",
                    data=st.session_state.cm_comparison_html.encode("utf-8"), # HTML là string, cần encode
                    file_name="document_comparison.html",
                    mime="text/html",
                    key="cm_download_html_button"
                )
            
            with st.expander("📝 Xem văn bản OCR của từng tài liệu"):
                col_txt1, col_txt2 = st.columns(2)
                with col_txt1:
                    st.text_area("Văn bản Tài liệu 1:", st.session_state.cm_text1, height=200, key="cm_text1_display")
                with col_txt2:
                    st.text_area("Văn bản Tài liệu 2:", st.session_state.cm_text2, height=200, key="cm_text2_display")
            st.markdown("---")
            display_random_meme()

    elif not file1 and not file2:
        st.info("Vui lòng tải lên hai file ảnh (.jpg, .jpeg, .png) để bắt đầu so sánh.")
    elif not file1:
        st.warning("Vui lòng tải lên Tài liệu 1.")
    elif not file2:
        st.warning("Vui lòng tải lên Tài liệu 2.")