# # ui_modules/form_extractor_ui.py
# import streamlit as st
# from PIL import Image
# import asyncio

# from logic.common_processing import extract_text_from_image_pil # Sử dụng hàm đã cải tiến
# from logic.form_extractor_logic import parse_text_with_groq_form
# from ui_utils.fun_meme import display_random_meme

# def show_form_extractor_ui(api_key):
#     st.markdown("<h1 style='text-align: center;'>📄 Trích xuất Thông tin từ Form (Ảnh)</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Tải lên ảnh CMND/CCCD, Hóa đơn, hoặc Đơn xin việc để tự động trích xuất thông tin chi tiết.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     if 'fe_ocr_text' not in st.session_state: st.session_state.fe_ocr_text = ""
#     if 'fe_ai_result' not in st.session_state: st.session_state.fe_ai_result = None
#     if 'fe_last_filename' not in st.session_state: st.session_state.fe_last_filename = None

#     uploaded_image_file = st.file_uploader(
#         "📤 Tải ảnh lên (JPG, PNG, JPEG)",
#         type=["jpg", "jpeg", "png"],
#         key="fe_image_uploader",
#         help="Hệ thống sẽ thực hiện OCR và sau đó dùng AI để trích xuất thông tin."
#     )

#     if uploaded_image_file:
#         if uploaded_image_file.name != st.session_state.fe_last_filename:
#             st.session_state.fe_ocr_text = ""
#             st.session_state.fe_ai_result = None
#             st.session_state.fe_last_filename = uploaded_image_file.name

#         col1_img, col2_ocr = st.columns([1, 2])

#         with col1_img:
#             with st.container(border=True):
#                 st.subheader("🖼️ Ảnh đã tải lên:")
#                 image = Image.open(uploaded_image_file)
#                 st.image(image,use_container_width =True)

#         with col2_ocr:
#             with st.container(border=True):
#                 st.subheader("📜 Văn bản OCR từ ảnh:")
#                 if not st.session_state.fe_ocr_text: # Chỉ OCR nếu chưa có
#                     with st.spinner("🧠 Đang chạy OCR trên ảnh..."):
#                         try:
#                             # Sử dụng hàm đã cải tiến, có thể bật preprocess nếu cần
#                             st.session_state.fe_ocr_text = extract_text_from_image_pil(image, lang="vie", preprocess=True) # Thử preprocess
#                         except ValueError as ve:
#                             st.error(f"Lỗi OCR: {ve}")
#                             st.session_state.fe_ocr_text = ""
#                         except Exception as e_ocr:
#                             st.error(f"Lỗi OCR không xác định: {e_ocr}")
#                             st.session_state.fe_ocr_text = ""
                
#                 st.text_area("Kết quả OCR:", st.session_state.fe_ocr_text, height=300, key="fe_ocr_display_area",
#                              help="Đây là văn bản được trích xuất từ ảnh bằng công nghệ OCR.")
        
#         st.markdown("---")
#         if st.session_state.fe_ocr_text.strip():
#             if st.button("🚀 Trích xuất Thông tin bằng AI", key="fe_extract_ai_button", type="primary", use_container_width=True):
#                 if not api_key:
#                     st.error("API Key chưa được cấu hình. Không thể trích xuất thông tin bằng AI.")
#                 else:
#                     with st.spinner("🤖 AI đang phân tích văn bản OCR và trích xuất thông tin..."):
#                         try:
#                             st.session_state.fe_ai_result = asyncio.run(parse_text_with_groq_form(api_key, st.session_state.fe_ocr_text))
#                         except ValueError as ve: # Lỗi từ logic AI
#                             st.error(f"Lỗi AI: {ve}")
#                             st.session_state.fe_ai_result = {"error": str(ve)}
#                         except Exception as e_ai_form:
#                             st.error(f"Lỗi không mong muốn khi AI trích xuất form: {e_ai_form}")
#                             st.session_state.fe_ai_result = {"error": str(e_ai_form)}
        
#         if st.session_state.fe_ai_result:
#             with st.container(border=True):
#                 st.subheader("📊 Kết quả Trích xuất Thông tin từ AI:")
#                 if "error" in st.session_state.fe_ai_result:
#                     st.error(f"Lỗi: {st.session_state.fe_ai_result['error']}")
#                     if "raw_response" in st.session_state.fe_ai_result:
#                         with st.expander("Xem phản hồi gốc từ AI"):
#                             st.text(st.session_state.fe_ai_result["raw_response"])
#                 else:
#                     st.json(st.session_state.fe_ai_result)
#                     # Nút tải JSON
#                     import json
#                     json_string = json.dumps(st.session_state.fe_ai_result, ensure_ascii=False, indent=4)
#                     st.download_button(
#                         label="📥 Tải kết quả JSON",
#                         data=json_string,
#                         file_name=f"form_extraction_{uploaded_image_file.name.split('.')[0]}.json",
#                         mime="application/json",
#                         key="fe_download_json_button"
#                     )
#             st.markdown("---")
#             display_random_meme()

#     else:
#         st.info("Vui lòng tải lên một file ảnh (JPG, PNG) để bắt đầu trích xuất thông tin từ form.")

# ui_modules/form_extractor_ui.py
import streamlit as st
from PIL import Image
import asyncio
import pandas as pd # Cần thêm pandas để vẽ biểu đồ

# Import các logic cũ
from logic.common_processing import extract_text_from_image_pil
from logic.form_extractor_logic import parse_text_with_groq_form
# Import logic mới
from logic.local_model_logic import predict_image_type 
from ui_utils.fun_meme import display_random_meme

def show_form_extractor_ui(api_key):
    st.markdown("<h1 style='text-align: center;'>📄 Phân loại & Trích xuất Giấy tờ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Sử dụng mô hình <b>AI Local</b> để phân loại nhanh và <b>GenAI (API)</b> để trích xuất chi tiết.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Khởi tạo session state
    if 'fe_ocr_text' not in st.session_state: st.session_state.fe_ocr_text = ""
    if 'fe_ai_result' not in st.session_state: st.session_state.fe_ai_result = None
    if 'fe_local_pred' not in st.session_state: st.session_state.fe_local_pred = None # Lưu kết quả model local
    if 'fe_last_filename' not in st.session_state: st.session_state.fe_last_filename = None

    uploaded_image_file = st.file_uploader(
        "📤 Tải ảnh lên (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        key="fe_image_uploader"
    )

    if uploaded_image_file:
        # Reset state nếu file thay đổi
        if uploaded_image_file.name != st.session_state.fe_last_filename:
            st.session_state.fe_ocr_text = ""
            st.session_state.fe_ai_result = None
            st.session_state.fe_local_pred = None
            st.session_state.fe_last_filename = uploaded_image_file.name

        image = Image.open(uploaded_image_file)
        
        # --- PHẦN 1: CHẠY MODEL LOCAL (TỰ ĐỘNG) ---
        col_img, col_info = st.columns([1, 1.5])
        
        with col_img:
            st.image(image, caption="Ảnh gốc", use_container_width=True)

        with col_info:
            st.subheader("🔍 Kết quả Phân loại (Local Model)")
            
            # Nếu chưa có kết quả dự đoán thì chạy ngay lập tức
            if st.session_state.fe_local_pred is None:
                with st.spinner("⚡ Đang chạy model phân loại cục bộ..."):
                    st.session_state.fe_local_pred = predict_image_type(image)
            
            # Hiển thị kết quả local
            pred_result = st.session_state.fe_local_pred
            
            if "error" in pred_result:
                st.error(f"Lỗi Model Local: {pred_result['error']}")
            else:
                # Hiển thị Label to
                label = pred_result['label']
                conf = pred_result['confidence']
                
                # Tô màu dựa trên độ tự tin
                color = "green" if conf > 80 else "orange" if conf > 50 else "red"
                st.markdown(f"### Dự đoán: <span style='color:{color}'>{label}</span>", unsafe_allow_html=True)
                st.markdown(f"**Độ tin cậy:** {conf:.2f}%")
                
                # Vẽ biểu đồ cột xác suất các lớp
                st.write("Chi tiết xác suất:")
                chart_data = pd.DataFrame(
                    list(pred_result['details'].items()),
                    columns=["Loại giấy tờ", "Xác suất (%)"]
                )
                st.bar_chart(chart_data, x="Loại giấy tờ", y="Xác suất (%)")

        st.markdown("---")

        # --- PHẦN 2: CHẠY OCR & API (THỦ CÔNG) ---
        st.subheader("🤖 Trích xuất chi tiết (API Cloud)")
        st.info("Nếu kết quả phân loại trên đã đúng (hoặc bạn muốn xem chi tiết), hãy bấm nút dưới đây để OCR và gọi AI trích xuất dữ liệu.")

        col_ocr, col_json = st.columns(2)

        # Nút bấm để kích hoạt quy trình API
        if st.button("🚀 Chạy OCR & Trích xuất (Call API)", type="primary", use_container_width=True):
            if not api_key:
                st.error("⚠️ Chưa nhập API Key!")
            else:
                # 1. Chạy OCR
                with st.status("Đang xử lý...", expanded=True) as status:
                    st.write("👀 Đang đọc văn bản (OCR)...")
                    try:
                        st.session_state.fe_ocr_text = extract_text_from_image_pil(image, lang="vie", preprocess=True)
                    except Exception as e:
                        st.error(f"Lỗi OCR: {e}")
                        st.stop()
                    
                    st.write("🧠 Đang gửi cho AI phân tích...")
                    try:
                        st.session_state.fe_ai_result = asyncio.run(parse_text_with_groq_form(api_key, st.session_state.fe_ocr_text))
                    except Exception as e:
                        st.error(f"Lỗi API: {e}")
                        st.stop()
                        
                    status.update(label="Hoàn tất!", state="complete", expanded=False)

        # Hiển thị kết quả sau khi bấm nút
        with col_ocr:
            if st.session_state.fe_ocr_text:
                st.text_area("Văn bản OCR:", st.session_state.fe_ocr_text, height=300)

        with col_json:
            if st.session_state.fe_ai_result:
                st.success("Kết quả từ AI:")
                st.json(st.session_state.fe_ai_result)
                
                # So sánh nhẹ kết quả
                ai_type = st.session_state.fe_ai_result.get("loai_giay_to", "Không rõ")
                local_type = st.session_state.fe_local_pred['label'] if st.session_state.fe_local_pred else "N/A"
                
                st.caption(f"ℹ️ So sánh: Model Local đoán là **{local_type}** | API trích xuất là **{ai_type}**")

    else:
        st.info("Vui lòng tải lên một file ảnh để bắt đầu.")