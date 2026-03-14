# ui_modules/pdf_unlock_ui.py
import streamlit as st
from logic.pdf_security_logic import unlock_pdf # Đảm bảo import đúng
from ui_utils.fun_meme import display_random_meme

def show_pdf_unlock_ui():
    st.markdown("<h1 style='text-align: center;'>🔓 Mở khóa PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên file PDF được bảo vệ để cố gắng loại bỏ mật khẩu và các hạn chế về quyền.</p>", unsafe_allow_html=True)
    st.info("💡 **Lưu ý:** Nếu file PDF yêu cầu mật khẩu để mở (User Password), bạn cần cung cấp mật khẩu đó. Tính năng này không dùng để 'bẻ khóa' PDF mà bạn không có quyền truy cập.")
    st.markdown("---")

    # Khởi tạo session state cho module này
    if 'pulk_unlocked_pdf_bytes' not in st.session_state:
        st.session_state.pulk_unlocked_pdf_bytes = None
    if 'pulk_uploaded_filename' not in st.session_state:
        st.session_state.pulk_uploaded_filename = None
    if 'pulk_current_password' not in st.session_state:
        st.session_state.pulk_current_password = ""


    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF cần mở khóa:",
        type="pdf",
        key="pulk_pdf_uploader_widget", # Key riêng cho widget
        help="File PDF bạn muốn loại bỏ bảo vệ."
    )

    # Sử dụng st.session_state để giữ giá trị password giữa các lần rerun
    st.session_state.pulk_current_password = st.text_input(
        "🔑 Nhập mật khẩu hiện tại của PDF (nếu có):",
        type="password",
        value=st.session_state.pulk_current_password, # Giữ lại giá trị đã nhập
        key="pulk_password_input_widget",
        help="Nếu PDF yêu cầu mật khẩu để mở, hãy nhập vào đây. Nếu chỉ có mật khẩu quyền (owner password) mà bạn biết, cũng có thể nhập."
    )

    if uploaded_pdf_file:
        if uploaded_pdf_file.name != st.session_state.pulk_uploaded_filename:
            st.session_state.pulk_unlocked_pdf_bytes = None 
            st.session_state.pulk_uploaded_filename = uploaded_pdf_file.name
        
        st.markdown("---")
        if st.button("🔓 Bắt đầu Mở khóa PDF", type="primary", use_container_width=True, key="pulk_unlock_button_widget"):
            st.session_state.pulk_unlocked_pdf_bytes = None 
            with st.spinner("⏳ Đang cố gắng mở khóa PDF..."):
                try:
                    pdf_bytes_content = uploaded_pdf_file.getvalue()
                    password_to_try = st.session_state.pulk_current_password # Lấy từ session_state
                    
                    st.session_state.pulk_unlocked_pdf_bytes = unlock_pdf(pdf_bytes_content, password_to_try)
                    st.success("🎉 Xử lý mở khóa PDF hoàn tất!")
                    st.info("Lưu ý: Nếu PDF không có bảo vệ nào, file tải về sẽ giống file gốc nhưng có thể đã được tối ưu hóa lại và cấp đủ quyền.")
                except ValueError as ve: # Lỗi đã được chuẩn hóa từ logic
                    st.error(f"{ve}")
                except Exception as e: # Các lỗi không lường trước khác
                    st.error(f"Lỗi không mong muốn khi mở khóa: {type(e).__name__} - {e}")
        
        if st.session_state.pulk_unlocked_pdf_bytes:
            unlocked_filename_base = "".join(st.session_state.pulk_uploaded_filename.split('.')[:-1])
            unlocked_filename = f"{unlocked_filename_base}_unlocked.pdf"
            st.download_button(
                label="📥 Tải xuống PDF đã mở khóa",
                data=st.session_state.pulk_unlocked_pdf_bytes,
                file_name=unlocked_filename,
                mime="application/pdf",
                key="pulk_download_button_widget",
                use_container_width=True
            )
            st.markdown("---")
            if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                display_random_meme()
    else:
        st.info("Vui lòng tải lên một file PDF để bắt đầu.")
        if st.session_state.pulk_uploaded_filename is not None: # Reset nếu file bị gỡ
            st.session_state.pulk_unlocked_pdf_bytes = None
            st.session_state.pulk_uploaded_filename = None
            st.session_state.pulk_current_password = ""