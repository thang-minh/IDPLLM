# ui_modules/pdf_signer_ui.py
import streamlit as st
from PIL import Image # Để lấy kích thước ảnh preview chữ ký

# Import các hàm logic từ thư mục logic
from logic.pdf_signer_logic import sign_pdf
from ui_utils.fun_meme import display_random_meme

def show_pdf_signer_ui():
    st.markdown("<h1 style='text-align: center;'>✍️ Ký và Đóng dấu số PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên file PDF và ảnh chữ ký/dấu của bạn để dễ dàng chèn vào tài liệu.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if 'ps_signed_pdf_bytes' not in st.session_state: st.session_state.ps_signed_pdf_bytes = None
    if 'ps_last_pdf_name' not in st.session_state: st.session_state.ps_last_pdf_name = None
    if 'ps_last_sig_name' not in st.session_state: st.session_state.ps_last_sig_name = None

    col_pdf, col_sig_options = st.columns([2, 1])

    with col_pdf:
        with st.container(border=True):
            st.subheader("📄 Tài liệu PDF")
            uploaded_pdf = st.file_uploader(
                "Tải lên file PDF cần ký:",
                type=["pdf"],
                key="ps_pdf_uploader",
                help="File PDF bạn muốn chèn chữ ký/dấu."
            )
            if uploaded_pdf and uploaded_pdf.name != st.session_state.ps_last_pdf_name:
                st.session_state.ps_signed_pdf_bytes = None # Reset khi PDF mới
                st.session_state.ps_last_pdf_name = uploaded_pdf.name


    with col_sig_options:
        with st.container(border=True):
            st.subheader("✒️ Chữ ký / Dấu")
            uploaded_signature_img = st.file_uploader(
                "Tải lên ảnh Chữ ký/Dấu:",
                type=["png", "jpg", "jpeg"],
                key="ps_signature_uploader",
                help="Ảnh PNG (khuyến khích nền trong suốt) hoặc JPG/JPEG."
            )
            if uploaded_signature_img:
                if uploaded_signature_img.name != st.session_state.ps_last_sig_name:
                    st.session_state.ps_signed_pdf_bytes = None # Reset khi ảnh chữ ký mới
                    st.session_state.ps_last_sig_name = uploaded_signature_img.name
                
                st.image(uploaded_signature_img, caption="Preview Chữ ký/Dấu", width=150)
                
                st.markdown("###### Tùy chỉnh chữ ký:")
                # Lấy số trang từ PDF nếu đã tải lên (cần PyMuPDF để đọc số trang)
                num_pages = 1
                if uploaded_pdf:
                    try:
                        import fitz
                        pdf_doc_temp = fitz.open(stream=uploaded_pdf.getvalue(), filetype="pdf")
                        num_pages = len(pdf_doc_temp)
                        pdf_doc_temp.close()
                    except Exception:
                        num_pages = 1 # Mặc định nếu không đọc được

                page_number = st.number_input("Số trang để ký (bắt đầu từ 1):", min_value=1, max_value=num_pages, value=1, step=1, key="ps_page_num")
                
                col_x, col_y = st.columns(2)
                pos_x = col_x.number_input("Vị trí X (từ trái):", min_value=0, value=50, step=10, key="ps_pos_x")
                pos_y = col_y.number_input("Vị trí Y (từ trên):", min_value=0, value=700, step=10, key="ps_pos_y")
                
                img_width = st.slider("Chiều rộng chữ ký trên PDF (pixels):", min_value=30, max_value=300, value=100, step=10, key="ps_img_width")
                opacity = st.slider("Độ mờ chữ ký (Opacity):", min_value=0.1, max_value=1.0, value=1.0, step=0.1, key="ps_opacity", help="1.0 là rõ nét, 0.1 là rất mờ.")


    if uploaded_pdf and uploaded_signature_img:
        st.markdown("---")
        if st.button("🖋️ Ký và Xem trước (Tạo file PDF mới)", type="primary", use_container_width=True, key="ps_sign_button"):
            with st.spinner("Đang chèn chữ ký vào PDF..."):
                pdf_bytes = uploaded_pdf.getvalue() # getvalue() để đọc lại nếu file đã được đọc trước đó
                signature_bytes = uploaded_signature_img.getvalue()
                try:
                    st.session_state.ps_signed_pdf_bytes = sign_pdf(
                        pdf_bytes, signature_bytes,
                        page_number=page_number - 1, # Logic dùng 0-indexed
                        pos=(pos_x, pos_y),
                        img_width=img_width,
                        opacity=opacity
                    )
                    st.success("🎉 Đã chèn chữ ký vào PDF thành công!")
                except ValueError as ve:
                    st.error(f"Lỗi khi ký PDF: {ve}")
                    st.session_state.ps_signed_pdf_bytes = None
                except Exception as e_sign:
                    st.error(f"Lỗi không mong muốn khi ký PDF: {e_sign}")
                    st.session_state.ps_signed_pdf_bytes = None

        if st.session_state.ps_signed_pdf_bytes:
            st.download_button(
                "📥 Tải PDF đã ký",
                data=st.session_state.ps_signed_pdf_bytes,
                file_name=f"signed_{uploaded_pdf.name}",
                mime="application/pdf",
                key="ps_download_signed_pdf_button",
                use_container_width=True
            )
            # Nhúng PDF để xem trước (có thể làm chậm nếu file lớn)
            # st.success("Xem trước PDF đã ký bên dưới:")
            # st.components.v1.iframe(src=f"data:application/pdf;base64,{base64.b64encode(st.session_state.ps_signed_pdf_bytes).decode()}", height=600)
            st.markdown("---")
            display_random_meme()
            
    elif not uploaded_pdf and not uploaded_signature_img :
        st.info("Vui lòng tải lên file PDF và ảnh chữ ký/dấu để bắt đầu.")
    elif not uploaded_pdf:
        st.warning("Vui lòng tải lên file PDF.")
    elif not uploaded_signature_img:
        st.warning("Vui lòng tải lên ảnh chữ ký/dấu.")