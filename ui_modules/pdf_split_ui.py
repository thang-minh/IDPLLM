# ui_modules/pdf_split_ui.py
import streamlit as st
import fitz # Để lấy số trang hiển thị cho người dùng
import io
from logic.pdf_utils import split_pdf, create_zip_from_files_data # Import hàm logic
from ui_utils.fun_meme import display_random_meme # Tùy chọn

def show_pdf_split_ui():
    st.markdown("<h1 style='text-align: center;'>✂️ Tách file PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên file PDF và chọn cách bạn muốn tách nó thành các file nhỏ hơn.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Session state
    if 'psplit_output_files_data' not in st.session_state:
        st.session_state.psplit_output_files_data = [] # List of (filename, bytes)
    if 'psplit_uploaded_filename' not in st.session_state:
        st.session_state.psplit_uploaded_filename = None
    if 'psplit_zip_bytes' not in st.session_state:
        st.session_state.psplit_zip_bytes = None

    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF cần tách:",
        type="pdf",
        key="psplit_pdf_uploader",
        help="File PDF bạn muốn chia nhỏ."
    )

    if uploaded_pdf_file:
        if uploaded_pdf_file.name != st.session_state.psplit_uploaded_filename:
            st.session_state.psplit_output_files_data = []
            st.session_state.psplit_zip_bytes = None
            st.session_state.psplit_uploaded_filename = uploaded_pdf_file.name

        try:
            # Đọc bytes một lần để tránh lỗi khi getvalue() nhiều lần
            pdf_bytes_content = uploaded_pdf_file.getvalue()
            with fitz.open(stream=io.BytesIO(pdf_bytes_content), filetype="pdf") as doc:
                total_pages = len(doc)
            st.info(f"File PDF đã tải lên có **{total_pages}** trang.")
        except Exception as e:
            st.error(f"Không thể đọc thông tin file PDF: {e}")
            return # Dừng nếu không đọc được file

        if total_pages == 0:
            st.warning("File PDF này không có trang nào để tách.")
            return

        st.markdown("---")
        st.subheader("⚙️ Chọn Chế độ Tách PDF:")

        split_mode_options = {
            "ranges": "Tách theo khoảng trang tùy chỉnh",
            "every_n_pages": "Tách mỗi N trang một file",
            "single_pages": "Tách mỗi trang thành một file riêng"
        }
        split_mode_display = st.radio(
            "Chế độ tách:",
            options=list(split_mode_options.values()),
            key="psplit_mode_radio",
            horizontal=True, # Hiển thị ngang cho đẹp
            label_visibility="collapsed"
        )
        # Lấy key của mode từ display name
        selected_mode_key = [k for k, v in split_mode_options.items() if v == split_mode_display][0]


        ranges_input = ""
        n_pages_input = 1

        if selected_mode_key == "ranges":
            ranges_input = st.text_input(
                "Nhập khoảng trang hoặc các trang cần tách:",
                placeholder="Ví dụ: 1-3, 5, 8-10",
                key="psplit_ranges_input",
                help="Các trang/khoảng trang cách nhau bởi dấu phẩy. Mỗi phần sẽ tạo thành một file PDF mới. Trang được đánh số từ 1."
            )
        elif selected_mode_key == "every_n_pages":
            n_pages_input = st.number_input(
                "Số trang cho mỗi file sau khi tách (N):",
                min_value=1, max_value=total_pages, value=1, step=1,
                key="psplit_n_pages_input"
            )
        
        st.markdown("---")
        if st.button("🚀 Bắt đầu Tách PDF", type="primary", use_container_width=True, key="psplit_split_button"):
            st.session_state.psplit_output_files_data = [] # Reset kết quả cũ
            st.session_state.psplit_zip_bytes = None

            with st.spinner("⏳ Đang tách file PDF..."):
                try:
                    st.session_state.psplit_output_files_data = split_pdf(
                        pdf_bytes_content, # Sử dụng bytes đã đọc
                        mode=selected_mode_key,
                        ranges_str=ranges_input if selected_mode_key == "ranges" else None,
                        n_pages_per_split=n_pages_input if selected_mode_key == "every_n_pages" else 1
                    )
                    if st.session_state.psplit_output_files_data:
                        st.success(f"🎉 Đã tách PDF thành công thành {len(st.session_state.psplit_output_files_data)} file!")
                        # Tạo file ZIP nếu có nhiều hơn 1 file kết quả
                        if len(st.session_state.psplit_output_files_data) > 1:
                            st.session_state.psplit_zip_bytes = create_zip_from_files_data(st.session_state.psplit_output_files_data)
                    else: # split_pdf có thể trả về list rỗng nếu không có gì để tách dù không lỗi
                        st.warning("Không có file nào được tạo ra từ quá trình tách. Vui lòng kiểm tra lại cấu hình tách.")

                except ValueError as ve:
                    st.error(f"Lỗi khi tách PDF: {ve}")
                except Exception as e:
                    st.error(f"Lỗi không mong muốn khi tách PDF: {type(e).__name__} - {e}")
        
        # Hiển thị nút tải xuống
        if st.session_state.psplit_output_files_data:
            st.markdown("---")
            st.subheader("📦 Kết quả Tách PDF:")

            if st.session_state.psplit_zip_bytes and len(st.session_state.psplit_output_files_data) > 1:
                zip_filename = f"{''.join(uploaded_pdf_file.name.split('.')[:-1])}_split_parts.zip"
                st.download_button(
                    label=f"📥 Tải tất cả ({len(st.session_state.psplit_output_files_data)} file) dưới dạng ZIP",
                    data=st.session_state.psplit_zip_bytes,
                    file_name=zip_filename,
                    mime="application/zip",
                    key="psplit_download_zip_button",
                    use_container_width=True
                )
                st.markdown("Hoặc tải từng file riêng lẻ bên dưới:")
            
            # Luôn hiển thị download cho từng file (hoặc chỉ khi < N file để tránh clutter)
            # Giới hạn hiển thị download từng file nếu quá nhiều
            max_individual_downloads_to_show = 10 
            if len(st.session_state.psplit_output_files_data) <= max_individual_downloads_to_show:
                cols = st.columns(min(len(st.session_state.psplit_output_files_data), 3)) # Tối đa 3 cột
                for i, (filename, data_bytes) in enumerate(st.session_state.psplit_output_files_data):
                    cols[i % len(cols)].download_button(
                        label=f"📥 Tải {filename}",
                        data=data_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key=f"psplit_download_single_{i}"
                    )
            elif len(st.session_state.psplit_output_files_data) > 1 : # Nếu nhiều hơn 1 file và > max_individual_downloads_to_show
                st.caption(f"Có {len(st.session_state.psplit_output_files_data)} file được tạo. Sử dụng nút tải ZIP ở trên để tải tất cả.")


            st.markdown("---")
            if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                 display_random_meme()

    else:
        st.info("Vui lòng tải lên một file PDF để bắt đầu quá trình tách file.")
        if st.session_state.psplit_uploaded_filename is not None: # Reset nếu file bị gỡ
            st.session_state.psplit_output_files_data = []
            st.session_state.psplit_zip_bytes = None
            st.session_state.psplit_uploaded_filename = None