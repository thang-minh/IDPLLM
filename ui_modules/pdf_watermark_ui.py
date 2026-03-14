# ui_modules/pdf_watermark_ui.py
import streamlit as st
from logic.pdf_utils import add_text_watermark_to_pdf, add_image_watermark_to_pdf # Import hàm logic
from ui_utils.fun_meme import display_random_meme # Tùy chọn
import os # Để kiểm tra file font

# Danh sách font cơ bản (PyMuPDF hỗ trợ các font này mà không cần file ngoài)
# Tuy nhiên, để có tiếng Việt tốt, cần font .ttf
AVAILABLE_FONTS_PDF_STANDARD = {
    "Helvetica": "helv",
    "Times Roman": "timas", # Times New Roman
    "Courier": "cour",
    # "Symbol": "symb", # Font ký tự đặc biệt
    # "ZapfDingbats": "zadb" # Font ký tự đặc biệt
}
# Bạn có thể thêm một thư mục 'fonts' vào dự án và đặt các file .ttf vào đó
# Ví dụ: USER_FONTS_DIR = "fonts"
# Sau đó quét thư mục này để lấy danh sách font người dùng


def show_pdf_watermark_ui():
    st.markdown("<h1 style='text-align: center;'>💧 Đóng dấu Watermark cho PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Thêm dấu bản quyền, thông tin nhận dạng hoặc trạng thái cho tài liệu PDF của bạn.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Session state
    if 'pwm_watermarked_pdf_bytes' not in st.session_state:
        st.session_state.pwm_watermarked_pdf_bytes = None
    if 'pwm_uploaded_pdf_name' not in st.session_state:
        st.session_state.pwm_uploaded_pdf_name = None

    # --- Cột chính cho upload PDF và các tùy chọn chung ---
    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF cần đóng dấu:",
        type="pdf",
        key="pwm_pdf_uploader",
        help="File PDF bạn muốn thêm watermark."
    )

    if uploaded_pdf_file:
        if uploaded_pdf_file.name != st.session_state.pwm_uploaded_pdf_name:
            st.session_state.pwm_watermarked_pdf_bytes = None # Reset khi file mới
            st.session_state.pwm_uploaded_pdf_name = uploaded_pdf_file.name
        
        st.info(f"Đã tải lên: {uploaded_pdf_file.name}")
        st.markdown("---")

        col_options, col_preview_placeholder = st.columns([2,1]) # Preview có thể thêm sau

        with col_options:
            st.subheader("⚙️ Tùy chỉnh Watermark")
            watermark_type = st.radio(
                "Loại Watermark:",
                options=["Văn bản (Text)", "Hình ảnh (Image)"],
                key="pwm_watermark_type",
                horizontal=True
            )

            page_spec_options = {
                "all": "Tất cả các trang",
                "even": "Chỉ trang chẵn",
                "odd": "Chỉ trang lẻ",
                "custom": "Trang tùy chỉnh (ví dụ: 1,3-5,8)"
            }
            page_spec_display = st.selectbox(
                "Áp dụng cho:",
                options=list(page_spec_options.values()),
                key="pwm_page_spec_select"
            )
            page_spec_key = [k for k,v in page_spec_options.items() if v == page_spec_display][0]
            
            custom_pages_input = ""
            if page_spec_key == "custom":
                custom_pages_input = st.text_input(
                    "Nhập số trang (cách nhau bởi dấu phẩy, ví dụ: 1,3-5,8):",
                    key="pwm_custom_pages_input"
                )
                page_spec_to_logic = custom_pages_input # Sẽ được validate trong hàm logic
            else:
                page_spec_to_logic = page_spec_key


            # --- Tùy chọn cho Watermark Văn bản ---
            if watermark_type == "Văn bản (Text)":
                wm_text = st.text_input("Nội dung Watermark:", value="ĐACN1 VKU © 2025", key="pwm_text_input")
                
                col_font1, col_font2 = st.columns(2)
                with col_font1:
                    # Tạm thời dùng font chuẩn, khuyến khích người dùng tự cung cấp font .ttf cho TV
                    # font_name_selected_display = st.selectbox("Chọn Font:", options=list(AVAILABLE_FONTS_PDF_STANDARD.keys()), key="pwm_font_name")
                    # font_name_for_logic = AVAILABLE_FONTS_PDF_STANDARD[font_name_selected_display]
                    st.caption("Lưu ý: Để có tiếng Việt tốt nhất, hãy cung cấp file font .ttf.")
                    font_file_path_input = st.text_input("Đường dẫn file font .ttf (tùy chọn):", placeholder="Để trống nếu dùng font chuẩn (có thể lỗi TV)", key="pwm_font_path")
                    # Kiểm tra nếu file font tồn tại (chỉ mang tính gợi ý, không chặn)
                    if font_file_path_input and not os.path.exists(font_file_path_input):
                        st.warning(f"Không tìm thấy file font tại: {font_file_path_input}")


                    font_size = st.slider("Kích thước Font:", min_value=8, max_value=150, value=48, step=1, key="pwm_font_size")
                
                with col_font2:
                    hex_color = st.color_picker("Màu chữ:", value="#808080", key="pwm_color_picker") # Xám mặc định
                    # Chuyển màu hex sang tuple (R,G,B) dạng 0-1 cho PyMuPDF
                    r = int(hex_color[1:3], 16) / 255.0
                    g = int(hex_color[3:5], 16) / 255.0
                    b = int(hex_color[5:7], 16) / 255.0
                    text_color_tuple = (r,g,b)

                    text_opacity = st.slider("Độ mờ (Opacity):", min_value=0.0, max_value=1.0, value=0.3, step=0.05, key="pwm_text_opacity")
                
                text_angle = st.slider("Góc xoay ( Độ ° ):", min_value=-90, max_value=90, value=45, step=5, key="pwm_text_angle")
                
                text_pos_options = {
                    "center": "Giữa trang (Center)", 
                    "diagonal_topleft_bottomright": "Chéo từ Trái-Trên xuống Phải-Dưới",
                    "custom": "Tùy chỉnh vị trí (X, Y)"
                }
                text_pos_display = st.selectbox("Vị trí Text:", options=list(text_pos_options.values()), key="pwm_text_pos_select")
                text_pos_key = [k for k,v in text_pos_options.items() if v == text_pos_display][0]
                
                custom_text_xy = (0,0)
                if text_pos_key == "custom":
                    cx, cy = st.columns(2)
                    custom_text_x = cx.number_input("Tọa độ X (từ trái):", value=50, step=10, key="pwm_text_x")
                    custom_text_y = cy.number_input("Tọa độ Y (từ trên):", value=100, step=10, key="pwm_text_y")
                    custom_text_xy = (custom_text_x, custom_text_y)

            # --- Tùy chọn cho Watermark Hình ảnh ---
            elif watermark_type == "Hình ảnh (Image)":
                uploaded_wm_image = st.file_uploader(
                    "Tải lên file ảnh Watermark (PNG, JPG):",
                    type=["png", "jpg", "jpeg"],
                    key="pwm_image_uploader"
                )
                if uploaded_wm_image:
                    st.image(uploaded_wm_image, caption="Preview ảnh Watermark", width=100)
                
                img_opacity = st.slider("Độ mờ (Opacity):", min_value=0.0, max_value=1.0, value=0.3, step=0.05, key="pwm_img_opacity")
                img_scale = st.slider("Tỷ lệ (Scale) ảnh:", min_value=0.1, max_value=3.0, value=0.5, step=0.1, key="pwm_img_scale")
                
                img_pos_options = {
                    "center": "Giữa trang (Center)",
                    "tile": "Lát gạch (Tile)",
                    "custom": "Tùy chỉnh vị trí (X, Y)"
                }
                img_pos_display = st.selectbox("Vị trí Ảnh:", options=list(img_pos_options.values()), key="pwm_img_pos_select")
                img_pos_key = [k for k,v in img_pos_options.items() if v == img_pos_display][0]

                custom_img_xy = (0,0)
                if img_pos_key == "custom":
                    cix, ciy = st.columns(2)
                    custom_img_x = cix.number_input("Tọa độ X (từ trái):", value=50, step=10, key="pwm_img_x")
                    custom_img_y = ciy.number_input("Tọa độ Y (từ trên):", value=100, step=10, key="pwm_img_y")
                    custom_img_xy = (custom_img_x, custom_img_y)


            st.markdown("---")
            if st.button("💧 Áp dụng Watermark", type="primary", use_container_width=True, key="pwm_apply_button"):
                pdf_bytes_content = uploaded_pdf_file.getvalue()
                st.session_state.pwm_watermarked_pdf_bytes = None # Reset

                with st.spinner("⏳ Đang thêm watermark vào PDF..."):
                    try:
                        if watermark_type == "Văn bản (Text)":
                            font_to_use = font_file_path_input if font_file_path_input and os.path.exists(font_file_path_input) else None
                            # Nếu không dùng font file, có thể lấy font_name_for_logic từ selectbox font chuẩn
                            # Hiện tại, nếu font_path không hợp lệ, logic sẽ dùng font mặc định của PIL
                            
                            st.session_state.pwm_watermarked_pdf_bytes = add_text_watermark_to_pdf(
                                pdf_bytes_content, wm_text,
                                page_spec=page_spec_to_logic,
                                font_path=font_to_use,
                                # font_name_pdf=font_name_for_logic, # Cần nếu không dùng font_path và PIL
                                font_size=font_size,
                                color=text_color_tuple,
                                opacity=text_opacity,
                                position=text_pos_key,
                                custom_pos=custom_text_xy,
                                angle=text_angle
                            )
                        elif watermark_type == "Hình ảnh (Image)":
                            if not uploaded_wm_image:
                                st.error("Vui lòng tải lên file ảnh cho watermark.")
                                return # Dừng nếu chưa có ảnh watermark
                            wm_image_bytes_content = uploaded_wm_image.getvalue()
                            st.session_state.pwm_watermarked_pdf_bytes = add_image_watermark_to_pdf(
                                pdf_bytes_content, wm_image_bytes_content,
                                page_spec=page_spec_to_logic,
                                opacity=img_opacity,
                                position=img_pos_key,
                                custom_pos=custom_img_xy,
                                scale=img_scale
                            )
                        st.success("🎉 Đã thêm watermark vào PDF thành công!")
                    except ValueError as ve:
                        st.error(f"Lỗi khi thêm watermark: {ve}")
                    except Exception as e:
                        st.error(f"Lỗi không mong muốn: {type(e).__name__} - {e}")
            
            if st.session_state.pwm_watermarked_pdf_bytes:
                watermarked_filename = f"{''.join(uploaded_pdf_file.name.split('.')[:-1])}_watermarked.pdf"
                st.download_button(
                    "📥 Tải PDF đã đóng dấu",
                    data=st.session_state.pwm_watermarked_pdf_bytes,
                    file_name=watermarked_filename,
                    mime="application/pdf",
                    key="pwm_download_button",
                    use_container_width=True
                )
                st.markdown("---")
                if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                    display_random_meme()

    else:
        st.info("Vui lòng tải lên một file PDF để bắt đầu đóng dấu watermark.")
        if st.session_state.pwm_uploaded_pdf_name is not None: # Reset nếu file bị gỡ
            st.session_state.pwm_watermarked_pdf_bytes = None
            st.session_state.pwm_uploaded_pdf_name = None