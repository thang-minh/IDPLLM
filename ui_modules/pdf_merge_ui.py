# ui_modules/pdf_merge_ui.py
import streamlit as st
from logic.pdf_utils import merge_pdfs # Import hàm logic
from ui_utils.fun_meme import display_random_meme # Tùy chọn

def show_pdf_merge_ui():
    st.markdown("<h1 style='text-align: center;'>📎 Hợp nhất (Ghép) nhiều file PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên các file PDF bạn muốn ghép lại thành một tài liệu duy nhất. Các file sẽ được ghép theo thứ tự bạn tải lên hoặc thứ tự hiển thị.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if 'pm_merged_pdf_bytes' not in st.session_state:
        st.session_state.pm_merged_pdf_bytes = None
    if 'pm_uploaded_files_count' not in st.session_state: # Để theo dõi sự thay đổi của file upload
        st.session_state.pm_uploaded_files_count = 0


    uploaded_files = st.file_uploader(
        "📤 Tải lên các file PDF cần ghép:",
        type="pdf",
        accept_multiple_files=True,
        key="pm_pdf_uploader",
        help="Bạn có thể chọn nhiều file PDF cùng lúc. Thứ tự ghép có thể dựa trên tên file hoặc thứ tự tải lên."
    )

    if uploaded_files:
        # Nếu danh sách file thay đổi, reset kết quả cũ
        if len(uploaded_files) != st.session_state.pm_uploaded_files_count:
            st.session_state.pm_merged_pdf_bytes = None
            st.session_state.pm_uploaded_files_count = len(uploaded_files)

        st.subheader(f"📑 Các file đã chọn ({len(uploaded_files)} file):")
        # Sắp xếp file theo tên để có thứ tự nhất quán nếu người dùng không chọn theo thứ tự
        # Hoặc bạn có thể cho phép người dùng sắp xếp lại (phức tạp hơn về UI)
        # Hiện tại, xử lý theo thứ tự file_uploader trả về (thường là thứ tự chọn)
        # Để có thứ tự rõ ràng hơn, ta có thể sắp xếp theo tên:
        # sorted_uploaded_files = sorted(uploaded_files, key=lambda f: f.name)
        
        # Giữ nguyên thứ tự tải lên cho đơn giản:
        sorted_uploaded_files = uploaded_files 

        for i, uploaded_file in enumerate(sorted_uploaded_files):
            st.write(f"{i+1}. {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        st.markdown("---")

        if st.button("🚀 Hợp nhất các file PDF đã chọn", type="primary", use_container_width=True, key="pm_merge_button"):
            if len(sorted_uploaded_files) < 2:
                st.warning("Vui lòng tải lên ít nhất 2 file PDF để thực hiện việc ghép.")
            else:
                with st.spinner("⏳ Đang hợp nhất các file PDF..."):
                    try:
                        list_of_pdf_bytes = [file.getvalue() for file in sorted_uploaded_files]
                        st.session_state.pm_merged_pdf_bytes = merge_pdfs(list_of_pdf_bytes)
                        st.success("🎉 Đã hợp nhất các file PDF thành công!")
                    except ValueError as ve:
                        st.error(f"Lỗi khi hợp nhất: {ve}")
                        st.session_state.pm_merged_pdf_bytes = None
                    except Exception as e:
                        st.error(f"Lỗi không mong muốn khi hợp nhất PDF: {type(e).__name__} - {e}")
                        st.session_state.pm_merged_pdf_bytes = None
        
        if st.session_state.pm_merged_pdf_bytes:
            merged_filename = "merged_document.pdf" # Tên file mặc định
            # Bạn có thể thử tạo tên file thông minh hơn dựa trên tên các file gốc
            # Ví dụ: merged_file1_file2_... .pdf
            
            st.download_button(
                label="📥 Tải xuống file PDF đã hợp nhất",
                data=st.session_state.pm_merged_pdf_bytes,
                file_name=merged_filename,
                mime="application/pdf",
                key="pm_download_merged_button",
                use_container_width=True
            )
            st.markdown("---")
            if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                 display_random_meme()
                 
    else: # Nếu không có file nào được tải lên
        st.info("Vui lòng tải lên ít nhất hai file PDF để bắt đầu quá trình hợp nhất.")
        # Reset state nếu không có file
        if st.session_state.pm_uploaded_files_count > 0:
            st.session_state.pm_merged_pdf_bytes = None
            st.session_state.pm_uploaded_files_count = 0