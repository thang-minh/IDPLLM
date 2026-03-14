# ui_modules/pdf_editor_ui.py
import streamlit as st
import fitz # Để lấy số trang, kích thước trang
import io
from PIL import Image # <<<< ----- THÊM DÒNG IMPORT NÀY Ở ĐÂY

from logic.pdf_utils import manipulate_pdf_pages, add_text_overlay_to_page, get_page_list 
# (Hoặc logic.pdf_edit_logic nếu bạn tạo file riêng)
# Đảm bảo get_page_list cũng được import nếu manipulate_pdf_pages hoặc các hàm khác cần nó
from ui_utils.fun_meme import display_random_meme

def show_pdf_editor_ui():
    st.markdown("<h1 style='text-align: center;'>✏️ Biên tập PDF Cơ bản</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Thực hiện các thao tác cơ bản như xoay, xóa, sắp xếp lại trang và thêm chú thích văn bản.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Session state cho module này
    if 'pe_pdf_bytes' not in st.session_state:
        st.session_state.pe_pdf_bytes = None
    if 'pe_uploaded_filename' not in st.session_state:
        st.session_state.pe_uploaded_filename = None
    if 'pe_page_previews' not in st.session_state:
        st.session_state.pe_page_previews = []
    if 'pe_num_pages' not in st.session_state:
        st.session_state.pe_num_pages = 0

    # --- Tải file PDF ---
    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF cần biên tập:",
        type="pdf",
        key="pe_pdf_uploader"
    )

    if uploaded_pdf_file:
        # Nếu file mới được tải lên, hoặc chưa có pe_pdf_bytes
        if uploaded_pdf_file.name != st.session_state.pe_uploaded_filename or st.session_state.pe_pdf_bytes is None:
            st.session_state.pe_pdf_bytes = uploaded_pdf_file.getvalue()
            st.session_state.pe_uploaded_filename = uploaded_pdf_file.name
            st.session_state.pe_page_previews = [] # Xóa preview cũ
            st.session_state.pe_num_pages = 0
            st.info(f"Đã tải lên: {st.session_state.pe_uploaded_filename}. Đang tạo preview...")
            # Tạo preview ngay khi có file mới
            try:
                # Mở PDF từ bytes trong session state để preview
                with fitz.open(stream=io.BytesIO(st.session_state.pe_pdf_bytes), filetype="pdf") as doc:
                    st.session_state.pe_num_pages = len(doc)
                    # Chỉ tạo preview nếu có trang
                    if st.session_state.pe_num_pages > 0:
                        for i in range(min(st.session_state.pe_num_pages, 10)): # Preview tối đa 10 trang
                            page = doc.load_page(i)
                            pix = page.get_pixmap(dpi=96) # DPI thấp hơn cho preview nhanh
                            # Sử dụng Image từ PIL đã import
                            st.session_state.pe_page_previews.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
                    else:
                        st.session_state.pe_page_previews = [] # Đảm bảo là list rỗng nếu không có trang

                # Không cần st.rerun() ở đây, việc gán vào session state và các widget sẽ tự cập nhật
                # Tuy nhiên, nếu bạn muốn thấy preview ngay lập tức sau khi upload mà không cần tương tác thêm,
                # st.rerun() có thể hữu ích, nhưng hãy cẩn thận để tránh vòng lặp vô hạn.
                # Trong trường hợp này, việc hiển thị preview ở dưới sẽ tự động diễn ra khi script chạy lại.
            except Exception as e:
                st.error(f"Lỗi khi đọc PDF để preview: {e}")
                st.session_state.pe_pdf_bytes = None # Reset nếu lỗi
                st.session_state.pe_page_previews = []
                st.session_state.pe_num_pages = 0
            st.rerun() # Chạy lại để cập nhật UI sau khi xử lý file upload và tạo preview

    # --- Hiển thị và các thao tác nếu đã có PDF ---
    if st.session_state.pe_pdf_bytes and st.session_state.pe_num_pages > 0:
        # ... (phần còn lại của hàm show_pdf_editor_ui giữ nguyên như bạn đã có) ...
        st.success(f"Tài liệu '{st.session_state.pe_uploaded_filename}' ({st.session_state.pe_num_pages} trang) đã sẵn sàng để biên tập.")
        
        # --- Hiển thị Page Previews ---
        if st.session_state.pe_page_previews:
            st.subheader("📄 Xem trước các trang (tối đa 10 trang đầu):")
            cols = st.columns(5) # 5 ảnh trên một hàng
            for i, img in enumerate(st.session_state.pe_page_previews):
                with cols[i % 5]:
                    st.image(img, caption=f"Trang {i+1}", use_container_width=True)
        st.markdown("---")


        # --- Các chức năng biên tập ---
        st.subheader("🛠️ Công cụ Biên tập")
        
        edit_action = st.selectbox("Chọn thao tác biên tập:", 
                                   ["--- Chọn ---", "Xoay Trang", "Xóa Trang", "Sắp xếp lại Trang", "Chèn Trang Trắng", "Thêm Chú thích Văn bản"],
                                   key="pe_edit_action_select")

        # --- Xoay Trang ---
        if edit_action == "Xoay Trang":
            with st.form("rotate_form"):
                st.markdown("##### Xoay Trang")
                pages_to_rotate_str = st.text_input("Nhập số trang cần xoay (ví dụ: 1, 3-5, all):", key="pe_pages_rotate_str")
                rotation_angle = st.selectbox("Chọn góc xoay:", [90, 180, 270], key="pe_rotate_angle")
                submit_rotate = st.form_submit_button("🌀 Áp dụng Xoay")
                if submit_rotate and pages_to_rotate_str:
                    with st.spinner("Đang xoay trang..."):
                        try:
                            # Hàm get_page_list cần được import từ logic.pdf_utils
                            pages_0_idx = get_page_list(st.session_state.pe_num_pages, pages_to_rotate_str)
                            rotations = {p: rotation_angle for p in pages_0_idx}
                            st.session_state.pe_pdf_bytes = manipulate_pdf_pages(st.session_state.pe_pdf_bytes, page_rotations=rotations)
                            st.success(f"Đã xoay các trang. Preview sẽ được cập nhật.")
                            st.session_state.pe_page_previews = [] 
                            st.rerun()
                        except ValueError as ve: st.error(f"Lỗi: {ve}")
                        except Exception as e: st.error(f"Lỗi không mong muốn khi xoay trang: {e}")
        
        # --- Xóa Trang ---
        elif edit_action == "Xóa Trang":
            with st.form("delete_form"):
                st.markdown("##### Xóa Trang")
                pages_to_delete_str = st.text_input("Nhập số trang cần xóa (ví dụ: 2, 4-6):", key="pe_pages_delete_str")
                submit_delete = st.form_submit_button("🗑️ Áp dụng Xóa")
                if submit_delete and pages_to_delete_str:
                    with st.spinner("Đang xóa trang..."):
                        try:
                            pages_0_idx = get_page_list(st.session_state.pe_num_pages, pages_to_delete_str)
                            st.session_state.pe_pdf_bytes = manipulate_pdf_pages(st.session_state.pe_pdf_bytes, pages_to_delete=pages_0_idx)
                            st.success(f"Đã xóa các trang. Preview sẽ được cập nhật.")
                            st.session_state.pe_page_previews = []
                            st.rerun()
                        except ValueError as ve: st.error(f"Lỗi: {ve}")
                        except Exception as e: st.error(f"Lỗi không mong muốn khi xóa trang: {e}")

        # --- Sắp xếp lại Trang ---
        elif edit_action == "Sắp xếp lại Trang":
            with st.form("reorder_form"):
                st.markdown("##### Sắp xếp lại Trang")
                st.caption(f"Tài liệu hiện có {st.session_state.pe_num_pages} trang (đánh số từ 1 đến {st.session_state.pe_num_pages}).")
                default_order = ','.join(map(str, range(1, st.session_state.pe_num_pages + 1)))
                new_order_str = st.text_input(f"Nhập thứ tự trang mới (ví dụ: {default_order}):", 
                                              value=default_order,
                                              key="pe_new_order_str", help="Nhập đầy đủ các số trang từ 1 đến N theo thứ tự mới, cách nhau bởi dấu phẩy.")
                submit_reorder = st.form_submit_button("🔄 Áp dụng Sắp xếp")
                if submit_reorder and new_order_str:
                    with st.spinner("Đang sắp xếp lại trang..."):
                        try:
                            new_order_1_idx = [int(p.strip()) for p in new_order_str.split(',')]
                            if len(new_order_1_idx) != st.session_state.pe_num_pages or \
                               len(set(new_order_1_idx)) != st.session_state.pe_num_pages or \
                               not all(1 <= p <= st.session_state.pe_num_pages for p in new_order_1_idx):
                                raise ValueError(f"Thứ tự trang mới không hợp lệ. Cần đủ {st.session_state.pe_num_pages} số trang từ 1 đến {st.session_state.pe_num_pages}, không trùng lặp.")
                            
                            new_order_0_idx = [p - 1 for p in new_order_1_idx]
                            st.session_state.pe_pdf_bytes = manipulate_pdf_pages(st.session_state.pe_pdf_bytes, new_page_order=new_order_0_idx)
                            st.success("Đã sắp xếp lại trang. Preview sẽ được cập nhật.")
                            st.session_state.pe_page_previews = []
                            st.rerun()
                        except ValueError as ve: st.error(f"Lỗi: {ve}")
                        except Exception as e: st.error(f"Lỗi không mong muốn khi sắp xếp trang: {e}")

        # --- Chèn Trang Trắng ---
        elif edit_action == "Chèn Trang Trắng":
             with st.form("insert_blank_form"):
                st.markdown("##### Chèn Trang Trắng")
                default_w, default_h = 595.0, 842.0 # A4 points
                try:
                    if st.session_state.pe_pdf_bytes: # Kiểm tra nếu có bytes
                        with fitz.open(stream=io.BytesIO(st.session_state.pe_pdf_bytes), filetype="pdf") as temp_doc:
                            if len(temp_doc) > 0:
                                first_page_rect = temp_doc[0].rect
                                default_w, default_h = first_page_rect.width, first_page_rect.height
                except: pass

                insert_pos_1_idx = st.number_input(f"Chèn SAU trang số (nhập 0 để chèn vào ĐẦU, {st.session_state.pe_num_pages} để chèn vào CUỐI):", 
                                                   min_value=0, max_value=st.session_state.pe_num_pages, 
                                                   value=st.session_state.pe_num_pages, step=1, key="pe_insert_blank_pos")
                
                col_w, col_h = st.columns(2)
                page_w = col_w.number_input("Chiều rộng trang trắng (points):", value=default_w, step=10.0, format="%.2f", key="pe_blank_w")
                page_h = col_h.number_input("Chiều cao trang trắng (points):", value=default_h, step=10.0, format="%.2f", key="pe_blank_h")
                
                submit_insert_blank = st.form_submit_button("➕ Áp dụng Chèn Trang")
                if submit_insert_blank:
                    with st.spinner("Đang chèn trang trắng..."):
                        try:
                            insert_after_0_idx = insert_pos_1_idx -1 
                            if insert_pos_1_idx == 0 : insert_after_0_idx = -1 
                                                        
                            inserts = {insert_after_0_idx: (page_w, page_h)}
                            st.session_state.pe_pdf_bytes = manipulate_pdf_pages(st.session_state.pe_pdf_bytes, insert_blank_after=inserts)
                            st.success("Đã chèn trang trắng. Preview sẽ được cập nhật.")
                            st.session_state.pe_page_previews = []
                            st.rerun()
                        except ValueError as ve: st.error(f"Lỗi: {ve}")
                        except Exception as e: st.error(f"Lỗi không mong muốn khi chèn trang: {e}")
        
        # --- Thêm Chú thích Văn bản ---
        elif edit_action == "Thêm Chú thích Văn bản":
            with st.form("add_text_form"):
                st.markdown("##### Thêm Chú thích Văn bản")
                page_num_text_1_idx = st.number_input("Thêm vào trang số:", min_value=1, max_value=st.session_state.pe_num_pages, value=1, step=1, key="pe_text_page_num")
                text_to_add = st.text_area("Nội dung Text:", key="pe_text_content_area", placeholder="Nội dung chú thích") # Thay đổi key
                
                st.markdown("###### Định vị và Kích thước Textbox:")
                col_t_pos, col_t_size = st.columns(2)
                text_x0 = col_t_pos.number_input("X0 (từ trái):", value=50.0, step=10.0, format="%.2f", key="pe_text_x0_num")
                text_y0 = col_t_pos.number_input("Y0 (từ trên):", value=50.0, step=10.0, format="%.2f", key="pe_text_y0_num")
                text_x1 = col_t_size.number_input("X1 (đến phải):", value=250.0, step=10.0, format="%.2f", key="pe_text_x1_num")
                text_y1 = col_t_size.number_input("Y1 (đến dưới):", value=100.0, step=10.0, format="%.2f", key="pe_text_y1_num")

                st.markdown("###### Thuộc tính Văn bản:")
                col_t_font, col_t_color_rot = st.columns(2)
                text_fontsize = col_t_font.number_input("Cỡ chữ:", value=11, min_value=6, max_value=72, step=1, key="pe_text_fontsize_num")
                font_name_options = {"Helvetica": "helv", "Times": "timas", "Courier": "cour"}
                selected_font_display = col_t_font.selectbox("Font chữ (chuẩn PDF):", options=list(font_name_options.keys()), key="pe_text_font_select")
                font_name_logic = font_name_options[selected_font_display]
                # Tùy chọn font path (nếu có)
                font_path_input = col_t_font.text_input("Đường dẫn file .ttf (tùy chọn cho TV):", key="pe_text_font_path", help="Nếu cung cấp, sẽ ưu tiên font này.")


                hex_color_text = col_t_color_rot.color_picker("Màu chữ:", value="#000000", key="pe_text_color_picker") # Đen mặc định
                r_text = int(hex_color_text[1:3], 16) / 255.0
                g_text = int(hex_color_text[3:5], 16) / 255.0
                b_text = int(hex_color_text[5:7], 16) / 255.0
                text_color_logic = (r_text,g_text,b_text)
                text_opacity_logic = col_t_color_rot.slider("Độ mờ Text:", 0.0, 1.0, 1.0, 0.05, key="pe_text_opacity_slider")
                text_rotate_logic = col_t_color_rot.slider("Xoay Text (°):", -90, 90, 0, 5, key="pe_text_rotate_slider")
                
                submit_add_text = st.form_submit_button("✍️ Áp dụng Thêm Text")
                if submit_add_text and text_to_add.strip():
                    if text_x1 <= text_x0 or text_y1 <= text_y0:
                        st.error("Tọa độ X1, Y1 của textbox phải lớn hơn X0, Y0.")
                    else:
                        with st.spinner("Đang thêm text vào trang..."):
                            try:
                                page_num_0_idx = page_num_text_1_idx - 1
                                text_rect_logic = (text_x0, text_y0, text_x1, text_y1) 
                                effective_font_path = font_path_input if font_path_input and os.path.exists(font_path_input) else None

                                st.session_state.pe_pdf_bytes = add_text_overlay_to_page(
                                    st.session_state.pe_pdf_bytes, page_num_0_idx, text_to_add,
                                    text_rect_logic, fontname=font_name_logic, fontsize=text_fontsize,
                                    color_tuple=text_color_logic, rotate=text_rotate_logic,
                                    opacity=text_opacity_logic, font_path=effective_font_path
                                )
                                st.success("Đã thêm text. Preview sẽ được cập nhật.")
                                st.session_state.pe_page_previews = []
                                st.rerun()
                            except ValueError as ve: st.error(f"Lỗi: {ve}")
                            except Exception as e: st.error(f"Lỗi không mong muốn khi thêm text: {e}")

        # --- Nút Tải về PDF đã biên tập ---
        st.markdown("---")
        if st.session_state.pe_pdf_bytes: # Chỉ hiện nếu có pdf_bytes
            edited_filename_base = "".join(st.session_state.pe_uploaded_filename.split('.')[:-1])
            edited_filename = f"{edited_filename_base}_edited.pdf"
            st.download_button(
                "📥 Tải xuống PDF đã biên tập",
                data=st.session_state.pe_pdf_bytes,
                file_name=edited_filename,
                mime="application/pdf",
                key="pe_download_edited_pdf_button",
                use_container_width=True
            )
            st.markdown("---")
            if 'display_random_meme' in globals() and callable(globals()['display_random_meme']):
                display_random_meme()

    elif uploaded_pdf_file is None and st.session_state.pe_uploaded_filename is None:
        st.info("Vui lòng tải lên một file PDF để bắt đầu biên tập.")
        # Reset state nếu không có file và trước đó đã có file
        if st.session_state.pe_uploaded_filename is not None:
            st.session_state.pe_pdf_bytes = None
            st.session_state.pe_uploaded_filename = None
            st.session_state.pe_page_previews = []
            st.session_state.pe_num_pages = 0