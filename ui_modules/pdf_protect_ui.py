# ui_modules/pdf_protect_ui.py
import streamlit as st
import fitz # Cần fitz để lấy các hằng số ENCRYPT_
from logic.pdf_security_logic import protect_pdf # Đảm bảo import đúng
from ui_utils.fun_meme import display_random_meme

ENCRYPTION_METHODS_DISPLAY = { # Tên hiển thị và giá trị hằng số
    "AES 256-bit (Rất mạnh, Khuyến nghị)": fitz.PDF_ENCRYPT_AES_256,
    "AES 128-bit (Mạnh)": fitz.PDF_ENCRYPT_AES_128,
    "RC4 128-bit (Trung bình)": fitz.PDF_ENCRYPT_RC4_128,
}

def show_pdf_protect_ui():
    st.markdown("<h1 style='text-align: center;'>🔒 Bảo vệ PDF bằng Mật khẩu & Quyền</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Thêm mật khẩu mở file, mật khẩu quyền và thiết lập các hạn chế cho file PDF của bạn.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Khởi tạo session state
    if 'pprot_protected_pdf_bytes' not in st.session_state:
        st.session_state.pprot_protected_pdf_bytes = None
    if 'pprot_uploaded_filename' not in st.session_state:
        st.session_state.pprot_uploaded_filename = None
    # Giá trị mặc định cho các input
    default_values = {
        'user_pass': "",
        'owner_pass': "",
        'allow_print': True,
        'allow_copy': True,
        'allow_modify': False,
        'allow_annotate': False,
        'allow_assemble': False,
        'encryption': list(ENCRYPTION_METHODS_DISPLAY.keys())[0] # Mặc định AES 256
    }
    for key, value in default_values.items():
        if f'pprot_{key}' not in st.session_state:
            st.session_state[f'pprot_{key}'] = value


    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF cần bảo vệ:",
        type="pdf",
        key="pprot_pdf_uploader_widget",
        help="File PDF bạn muốn thêm các lớp bảo vệ."
    )

    if uploaded_pdf_file:
        if uploaded_pdf_file.name != st.session_state.pprot_uploaded_filename:
            st.session_state.pprot_protected_pdf_bytes = None 
            st.session_state.pprot_uploaded_filename = uploaded_pdf_file.name
        
        st.info(f"Đã tải lên: {uploaded_pdf_file.name}")
        st.markdown("---")

        with st.container(border=True):
            st.subheader("🔑 Thiết lập Mật khẩu")
            col_user_pass, col_owner_pass = st.columns(2)
            with col_user_pass:
                st.session_state.pprot_user_pass = st.text_input(
                    "Mật khẩu Mở File (User Password - tùy chọn):",
                    type="password",
                    value=st.session_state.pprot_user_pass,
                    key="pprot_user_pass_widget",
                    help="Người dùng sẽ cần nhập mật khẩu này để mở PDF. Để trống nếu không muốn."
                )
            with col_owner_pass:
                st.session_state.pprot_owner_pass = st.text_input(
                    "Mật khẩu Quyền (Owner Password - tùy chọn):",
                    type="password",
                    value=st.session_state.pprot_owner_pass,
                    key="pprot_owner_pass_widget",
                    help="Mật khẩu này cho phép bỏ qua các hạn chế quyền và thay đổi cài đặt bảo mật. Nên đặt nếu bạn đặt Mật khẩu Mở File hoặc muốn hạn chế quyền."
                )
            if st.session_state.pprot_user_pass and not st.session_state.pprot_owner_pass:
                st.caption("Lưu ý: Nếu chỉ đặt Mật khẩu Mở File, nó cũng sẽ được dùng làm Mật khẩu Quyền.")
            if not st.session_state.pprot_user_pass and not st.session_state.pprot_owner_pass:
                st.caption("Thông báo: Không đặt mật khẩu nào có thể làm giảm hiệu quả của việc hạn chế quyền.")

        with st.container(border=True):
            st.subheader("⚙️ Thiết lập Quyền Hạn chế")
            col_perm1, col_perm2 = st.columns(2)
            with col_perm1:
                st.session_state.pprot_allow_print = st.checkbox("Cho phép In ấn", value=st.session_state.pprot_allow_print, key="pprot_perm_print_widget", help="Cho phép người dùng in tài liệu.")
                st.session_state.pprot_allow_copy = st.checkbox("Cho phép Sao chép Nội dung", value=st.session_state.pprot_allow_copy, key="pprot_perm_copy_widget", help="Cho phép sao chép văn bản và hình ảnh.")
                st.session_state.pprot_allow_assemble = st.checkbox("Cho phép Lắp ráp Tài liệu", value=st.session_state.pprot_allow_assemble, key="pprot_perm_assemble_widget", help="Cho phép chèn, xóa, xoay trang.")

            with col_perm2:
                st.session_state.pprot_allow_modify = st.checkbox("Cho phép Chỉnh sửa Nội dung", value=st.session_state.pprot_allow_modify, key="pprot_perm_modify_widget", help="Cho phép thay đổi nội dung (không bao gồm chú thích/form).")
                st.session_state.pprot_allow_annotate = st.checkbox("Cho phép Chú thích & Điền Form", value=st.session_state.pprot_allow_annotate, key="pprot_perm_annotate_widget", help="Cho phép thêm/sửa chú thích và điền biểu mẫu.")
        
        with st.container(border=True):
            st.subheader("🛡️ Phương thức Mã hóa")
            st.session_state.pprot_encryption = st.selectbox(
                "Chọn mức độ mã hóa:",
                options=list(ENCRYPTION_METHODS_DISPLAY.keys()),
                index=list(ENCRYPTION_METHODS_DISPLAY.keys()).index(st.session_state.pprot_encryption),
                key="pprot_encryption_select_widget",
                help="AES 256-bit là mạnh nhất và được khuyến nghị."
            )
            encryption_method_value = ENCRYPTION_METHODS_DISPLAY[st.session_state.pprot_encryption]

        st.markdown("---")
        if st.button("🔒 Áp dụng Bảo vệ cho PDF", type="primary", use_container_width=True, key="pprot_protect_button_widget"):
            st.session_state.pprot_protected_pdf_bytes = None
            
            user_pass_to_logic = st.session_state.pprot_user_pass if st.session_state.pprot_user_pass else None
            owner_pass_to_logic = st.session_state.pprot_owner_pass if st.session_state.pprot_owner_pass else None

            with st.spinner("⏳ Đang áp dụng bảo vệ cho PDF..."):
                try:
                    pdf_bytes_content = uploaded_pdf_file.getvalue()
                    st.session_state.pprot_protected_pdf_bytes = protect_pdf(
                        pdf_bytes_content,
                        user_password=user_pass_to_logic,
                        owner_password=owner_pass_to_logic,
                        allow_print=st.session_state.pprot_allow_print,
                        allow_copy=st.session_state.pprot_allow_copy,
                        allow_modify=st.session_state.pprot_allow_modify,
                        allow_annotate_forms=st.session_state.pprot_allow_annotate,
                        allow_assemble=st.session_state.pprot_allow_assemble,
                        encryption_method=encryption_method_value
                    )
                    st.success("🎉 Đã bảo vệ PDF thành công!")
                except ValueError as ve:
                    st.error(f"Lỗi khi bảo vệ PDF: {ve}")
                except Exception as e:
                    st.error(f"Lỗi không mong muốn khi bảo vệ PDF: {type(e).__name__} - {e}")

        if st.session_state.pprot_protected_pdf_bytes:
            protected_filename_base = "".join(st.session_state.pprot_uploaded_filename.split('.')[:-1])
            protected_filename = f"{protected_filename_base}_protected.pdf"
            st.download_button(
                label="📥 Tải xuống PDF đã bảo vệ",
                data=st.session_state.pprot_protected_pdf_bytes,
                file_name=protected_filename,
                mime="application/pdf",
                key="pprot_download_button_widget",
                use_container_width=True
            )
            st.markdown("---")
            if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                display_random_meme()
    else:
        st.info("Vui lòng tải lên một file PDF để bắt đầu bảo vệ.")
        if st.session_state.pprot_uploaded_filename is not None: # Reset nếu file bị gỡ
            st.session_state.pprot_protected_pdf_bytes = None
            st.session_state.pprot_uploaded_filename = None
            # Reset các giá trị input về mặc định
            for key, value in default_values.items():
                 st.session_state[f'pprot_{key}'] = value