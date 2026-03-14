# ui_modules/pdf_redaction_ui.py
import streamlit as st
import tempfile
import os
from logic.redaction_logic import redact_pdf
import fitz # Để render ảnh preview

def show_pdf_redaction_ui():
    st.header("🛡️ Redaction AI - Che Thông tin Nhạy cảm")
    st.markdown("Tự động phát hiện và che (bôi đen) các thông tin cá nhân (PII) như Email, SĐT, CCCD.")

    uploaded_file = st.file_uploader("Tải file PDF cần xử lý", type=['pdf'])

    if uploaded_file:
        # Lưu file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(uploaded_file.read())
            input_path = tmp_in.name

        st.markdown("### ⚙️ Chọn thông tin cần che:")
        col1, col2, col3 = st.columns(3)
        with col1:
            redact_email = st.checkbox("📧 Email", value=True)
        with col2:
            redact_phone = st.checkbox("📞 Số điện thoại (VN)", value=True)
        with col3:
            redact_id = st.checkbox("🆔 CCCD / CMND", value=False)

        if st.button("🚀 Thực hiện Bảo mật (Redact)", type="primary"):
            # Tạo list các mục cần che
            items = []
            if redact_email: items.append("email")
            if redact_phone: items.append("phone")
            if redact_id: items.append("id_card")

            if not items:
                st.warning("Vui lòng chọn ít nhất một loại thông tin để che.")
            else:
                output_path = input_path.replace(".pdf", "_redacted.pdf")
                
                with st.spinner("Đang quét và xử lý bảo mật..."):
                    try:
                        # Gọi logic xử lý
                        count = redact_pdf(input_path, output_path, items)
                        
                        st.success(f"✅ Hoàn tất! Đã che **{count}** vị trí nhạy cảm.")
                        
                        # Hiển thị nút tải về
                        with open(output_path, "rb") as f:
                            st.download_button(
                                "⬇️ Tải file đã bảo mật",
                                f,
                                file_name="secure_document.pdf",
                                mime="application/pdf"
                            )
                        
                        # --- PREVIEW (Xem trước trang đầu) ---
                        st.markdown("---")
                        st.markdown("### 👀 Xem trước kết quả (Trang 1)")
                        doc = fitz.open(output_path)
                        page = doc.load_page(0)
                        pix = page.get_pixmap()
                        st.image(pix.tobytes(), caption="Trang 1 sau khi che mật", use_column_width=True)
                        doc.close()

                    except Exception as e:
                        st.error(f"Lỗi xử lý: {e}")