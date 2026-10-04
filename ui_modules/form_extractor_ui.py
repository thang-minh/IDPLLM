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
# import streamlit as st
# from PIL import Image
# import asyncio
# import pandas as pd # Cần thêm pandas để vẽ biểu đồ

# # Import các logic cũ
# from logic.common_processing import extract_text_from_image_pil
# from logic.form_extractor_logic import parse_text_with_groq_form
# # Import logic mới
# from logic.local_model_logic import predict_image_type 
# from ui_utils.fun_meme import display_random_meme

# def show_form_extractor_ui(api_key):
#     st.markdown("<h1 style='text-align: center;'>📄 Phân loại & Trích xuất Giấy tờ</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Sử dụng mô hình <b>AI Local</b> để phân loại nhanh và <b>GenAI (API)</b> để trích xuất chi tiết.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     # Khởi tạo session state
#     if 'fe_ocr_text' not in st.session_state: st.session_state.fe_ocr_text = ""
#     if 'fe_ai_result' not in st.session_state: st.session_state.fe_ai_result = None
#     if 'fe_local_pred' not in st.session_state: st.session_state.fe_local_pred = None # Lưu kết quả model local
#     if 'fe_last_filename' not in st.session_state: st.session_state.fe_last_filename = None

#     uploaded_image_file = st.file_uploader(
#         "📤 Tải ảnh lên (JPG, PNG)",
#         type=["jpg", "jpeg", "png"],
#         key="fe_image_uploader"
#     )

#     if uploaded_image_file:
#         # Reset state nếu file thay đổi
#         if uploaded_image_file.name != st.session_state.fe_last_filename:
#             st.session_state.fe_ocr_text = ""
#             st.session_state.fe_ai_result = None
#             st.session_state.fe_local_pred = None
#             st.session_state.fe_last_filename = uploaded_image_file.name

#         image = Image.open(uploaded_image_file)
        
#         # --- PHẦN 1: CHẠY MODEL LOCAL (TỰ ĐỘNG) ---
#         col_img, col_info = st.columns([1, 1.5])
        
#         with col_img:
#             st.image(image, caption="Ảnh gốc", use_container_width=True)

#         with col_info:
#             st.subheader("🔍 Kết quả Phân loại (Local Model)")
            
#             # Nếu chưa có kết quả dự đoán thì chạy ngay lập tức
#             if st.session_state.fe_local_pred is None:
#                 with st.spinner("⚡ Đang chạy model phân loại cục bộ..."):
#                     st.session_state.fe_local_pred = predict_image_type(image)
            
#             # Hiển thị kết quả local
#             pred_result = st.session_state.fe_local_pred
            
#             if "error" in pred_result:
#                 st.error(f"Lỗi Model Local: {pred_result['error']}")
#             else:
#                 # Hiển thị Label to
#                 label = pred_result['label']
#                 conf = pred_result['confidence']
                
#                 # Tô màu dựa trên độ tự tin
#                 color = "green" if conf > 80 else "orange" if conf > 50 else "red"
#                 st.markdown(f"### Dự đoán: <span style='color:{color}'>{label}</span>", unsafe_allow_html=True)
#                 st.markdown(f"**Độ tin cậy:** {conf:.2f}%")
                
#                 # Vẽ biểu đồ cột xác suất các lớp
#                 st.write("Chi tiết xác suất:")
#                 chart_data = pd.DataFrame(
#                     list(pred_result['details'].items()),
#                     columns=["Loại giấy tờ", "Xác suất (%)"]
#                 )
#                 st.bar_chart(chart_data, x="Loại giấy tờ", y="Xác suất (%)")

#         st.markdown("---")

#         # --- PHẦN 2: CHẠY OCR & API (THỦ CÔNG) ---
#         st.subheader("🤖 Trích xuất chi tiết (API Cloud)")
#         st.info("Nếu kết quả phân loại trên đã đúng (hoặc bạn muốn xem chi tiết), hãy bấm nút dưới đây để OCR và gọi AI trích xuất dữ liệu.")

#         col_ocr, col_json = st.columns(2)

#         # Nút bấm để kích hoạt quy trình API
#         if st.button("🚀 Chạy OCR & Trích xuất (Call API)", type="primary", use_container_width=True):
#             if not api_key:
#                 st.error("⚠️ Chưa nhập API Key!")
#             else:
#                 # 1. Chạy OCR
#                 with st.status("Đang xử lý...", expanded=True) as status:
#                     st.write("👀 Đang đọc văn bản (OCR)...")
#                     try:
#                         st.session_state.fe_ocr_text = extract_text_from_image_pil(image, lang="vie", preprocess=True)
#                     except Exception as e:
#                         st.error(f"Lỗi OCR: {e}")
#                         st.stop()
                    
#                     st.write("🧠 Đang gửi cho AI phân tích...")
#                     try:
#                         st.session_state.fe_ai_result = asyncio.run(parse_text_with_groq_form(api_key, st.session_state.fe_ocr_text))
#                     except Exception as e:
#                         st.error(f"Lỗi API: {e}")
#                         st.stop()
                        
#                     status.update(label="Hoàn tất!", state="complete", expanded=False)

#         # Hiển thị kết quả sau khi bấm nút
#         with col_ocr:
#             if st.session_state.fe_ocr_text:
#                 st.text_area("Văn bản OCR:", st.session_state.fe_ocr_text, height=300)

#         with col_json:
#             if st.session_state.fe_ai_result:
#                 st.success("Kết quả từ AI:")
#                 st.json(st.session_state.fe_ai_result)
                
#                 # So sánh nhẹ kết quả
#                 ai_type = st.session_state.fe_ai_result.get("loai_giay_to", "Không rõ")
#                 local_type = st.session_state.fe_local_pred['label'] if st.session_state.fe_local_pred else "N/A"
                
#                 st.caption(f"ℹ️ So sánh: Model Local đoán là **{local_type}** | API trích xuất là **{ai_type}**")

#     else:
#         st.info("Vui lòng tải lên một file ảnh để bắt đầu.")

# ui_modules/form_extractor_ui.py

import asyncio
import json

import pandas as pd
import streamlit as st
from PIL import Image

from logic.common_processing import extract_text_from_image_pil
from logic.form_extractor_logic import parse_text_with_groq_form
from logic.local_model_logic import predict_image_type, clear_local_model_cache
from ui_utils.fun_meme import display_random_meme


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def init_form_extractor_state():
    defaults = {
        "fe_ocr_text": "",
        "fe_ai_result": None,
        "fe_local_pred": None,
        "fe_last_filename": None,
        "fe_manual_label": None,
        "fe_uploaded_image": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_form_extractor_state(filename=None):
    st.session_state.fe_ocr_text = ""
    st.session_state.fe_ai_result = None
    st.session_state.fe_local_pred = None
    st.session_state.fe_manual_label = None
    st.session_state.fe_last_filename = filename


def get_confidence_status(confidence):
    if confidence >= 85:
        return "high", "Độ tin cậy cao", "success"
    if confidence >= 60:
        return "medium", "Độ tin cậy trung bình, nên kiểm tra thêm bằng OCR/AI", "warning"
    return "low", "Độ tin cậy thấp, ảnh có thể mờ hoặc không thuộc nhóm đã train", "error"


def display_local_prediction(pred_result):
    st.subheader("1. Phân loại ảnh bằng EfficientNetV2B0")

    if not pred_result:
        st.info("Chưa có kết quả phân loại.")
        return

    if "error" in pred_result:
        st.error(f"Lỗi model local: {pred_result['error']}")
        return

    label = pred_result["display_label"]
    raw_label = pred_result["label"]
    confidence = pred_result["confidence"]
    _, status_text, status_type = get_confidence_status(confidence)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        if status_type == "success":
            st.success(f"Loại tài liệu dự đoán: **{label}**")
        elif status_type == "warning":
            st.warning(f"Loại tài liệu dự đoán: **{label}**")
        else:
            st.error(f"Loại tài liệu dự đoán: **{label}**")

        st.caption(status_text)
        st.caption("Model: EfficientNetV2B0 fine-tune, chạy local/offline.")

    with col_b:
        st.metric("Độ tin cậy", f"{confidence:.2f}%")

    details = pred_result.get("details", {})
    if details:
        chart_data = pd.DataFrame(
            list(details.items()),
            columns=["Loại tài liệu", "Xác suất (%)"]
        )
        st.bar_chart(chart_data, x="Loại tài liệu", y="Xác suất (%)")

    st.session_state.fe_manual_label = st.selectbox(
        "Có thể sửa nhãn nếu model dự đoán chưa đúng:",
        options=list(details.keys()) if details else [raw_label],
        index=list(details.keys()).index(raw_label) if details and raw_label in details else 0,
        format_func=lambda x: x.replace("_", " "),
        key="fe_manual_label_select"
    )


def build_ai_context_prompt(ocr_text, local_pred, manual_label):
    local_label = "Không xác định"
    local_conf = 0.0

    if local_pred and "error" not in local_pred:
        local_label = local_pred.get("display_label", "Không xác định")
        local_conf = local_pred.get("confidence", 0.0)

    final_label = manual_label.replace("_", " ") if manual_label else local_label

    prompt = f"""
THÔNG TIN PHÂN LOẠI ẢNH LOCAL:
- Model ảnh: EfficientNetV2B0 fine-tune
- Nhãn model dự đoán: {local_label}
- Độ tin cậy: {local_conf:.2f}%
- Nhãn người dùng xác nhận/chỉnh sửa: {final_label}

NỘI DUNG OCR:
{ocr_text}

YÊU CẦU:
Hãy trích xuất thông tin quan trọng từ tài liệu trên.
Ưu tiên cấu trúc JSON nếu có thể.
Nếu là hóa đơn, trích xuất:
- loại giấy tờ
- tên bên bán
- tên bên mua
- mã số thuế
- số hóa đơn
- ngày lập
- tổng tiền
- thuế GTGT
- hàng hóa/dịch vụ chính

Nếu là sơ yếu lý lịch, trích xuất:
- loại giấy tờ
- họ tên
- ngày sinh
- quê quán
- địa chỉ
- số CCCD/CMND nếu có
- trình độ học vấn nếu có
- kinh nghiệm hoặc thông tin cá nhân chính

Nếu không đủ thông tin, hãy ghi null hoặc "không tìm thấy".
"""
    return prompt


def display_ai_result(uploaded_filename):
    if not st.session_state.fe_ai_result:
        return

    st.subheader("3. Kết quả trích xuất bằng LLM")

    result = st.session_state.fe_ai_result

    if isinstance(result, dict) and "error" in result:
        st.error(f"Lỗi: {result['error']}")

        if "raw_response" in result:
            with st.expander("Xem phản hồi gốc"):
                st.text(result["raw_response"])

        return

    st.success("Đã trích xuất thông tin thành công.")

    tab_json, tab_text = st.tabs(["JSON/Kết quả", "Văn bản OCR"])

    with tab_json:
        if isinstance(result, dict):
            st.json(result)
            json_string = json.dumps(result, ensure_ascii=False, indent=4)
        else:
            st.write(result)
            json_string = json.dumps(
                {"result": result},
                ensure_ascii=False,
                indent=4
            )

        safe_name = uploaded_filename.rsplit(".", 1)[0] if uploaded_filename else "document"
        st.download_button(
            label="Tải kết quả JSON",
            data=json_string,
            file_name=f"extraction_result_{safe_name}.json",
            mime="application/json",
            use_container_width=True
        )

    with tab_text:
        st.text_area(
            "Văn bản OCR:",
            st.session_state.fe_ocr_text,
            height=350
        )


# =========================================================
# MAIN UI
# =========================================================

def show_form_extractor_ui(api_key):
    init_form_extractor_state()

    st.markdown(
        "<h1 style='text-align: center;'>Phân loại ảnh & Trích xuất thông tin tài liệu</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align: center;'>
        Luồng xử lý: <b>Ảnh tài liệu</b> → <b>EfficientNetV2B0 phân loại local</b> → 
        <b>OCR</b> → <b>LLM trích xuất chi tiết</b>
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    with st.expander("Cấu hình model local", expanded=False):
        st.write("Model ảnh đang dùng:")
        st.code("models/model_AI_documen/best_document_image_classifier_2classes.keras")
        st.write("Class names:")
        st.code("models/model_AI_documen/class_names.txt")

        if st.button("Reload model local", use_container_width=True):
            clear_local_model_cache()
            st.session_state.fe_local_pred = None
            st.success("Đã xóa cache model. Hãy chạy lại phân loại.")

    uploaded_image_file = st.file_uploader(
        "Tải ảnh tài liệu lên",
        type=["jpg", "jpeg", "png"],
        key="fe_image_uploader",
        help="Hỗ trợ ảnh hóa đơn hoặc sơ yếu lý lịch. Ảnh PNG/RGBA sẽ được tự chuyển về RGB."
    )

    if not uploaded_image_file:
        st.info("Vui lòng tải lên một ảnh JPG/PNG để bắt đầu.")
        return

    if uploaded_image_file.name != st.session_state.fe_last_filename:
        reset_form_extractor_state(uploaded_image_file.name)

    try:
        image = Image.open(uploaded_image_file)
    except Exception as e:
        st.error(f"Không thể đọc ảnh: {e}")
        return

    # Convert để preview/predict ổn định
    preview_image = image.convert("RGB")

    col_img, col_pred = st.columns([1, 1.5])

    with col_img:
        with st.container(border=True):
            st.subheader("Ảnh đầu vào")
            st.image(preview_image, caption=uploaded_image_file.name, use_container_width=True)
            st.caption(f"Kích thước: {image.size[0]} x {image.size[1]} | Mode gốc: {image.mode}")

    with col_pred:
        with st.container(border=True):
            if st.session_state.fe_local_pred is None:
                if st.button("Chạy phân loại ảnh local", type="primary", use_container_width=True):
                    with st.spinner("Đang chạy EfficientNetV2B0..."):
                        st.session_state.fe_local_pred = predict_image_type(image)
                    st.rerun()
            else:
                display_local_prediction(st.session_state.fe_local_pred)

                if st.button("Chạy lại phân loại", use_container_width=True):
                    st.session_state.fe_local_pred = None
                    st.rerun()

    st.markdown("---")

    # Chỉ cho OCR sau khi đã có kết quả local
    if st.session_state.fe_local_pred is None:
        st.info("Hãy chạy phân loại ảnh local trước, sau đó mới chạy OCR và LLM.")
        return

    st.subheader("2. OCR và trích xuất chi tiết")

    col_ocr_action, col_ocr_preview = st.columns([1, 1.5])

    with col_ocr_action:
        with st.container(border=True):
            st.write("OCR sẽ đọc chữ trong ảnh, sau đó LLM sẽ trích xuất thông tin theo loại tài liệu.")

            preprocess_ocr = st.checkbox(
                "Bật tiền xử lý ảnh trước OCR",
                value=True,
                help="Nên bật nếu ảnh bị mờ, nghiêng nhẹ hoặc chất lượng thấp."
            )

            run_ocr_only = st.button(
                "Chạy OCR",
                use_container_width=True
            )

            run_full_pipeline = st.button(
                "Chạy OCR + LLM trích xuất",
                type="primary",
                use_container_width=True
            )

    if run_ocr_only or run_full_pipeline:
        with st.status("Đang xử lý OCR...", expanded=True) as status:
            try:
                st.write("Đang đọc văn bản từ ảnh...")
                st.session_state.fe_ocr_text = extract_text_from_image_pil(
                    image,
                    lang="vie",
                    preprocess=preprocess_ocr
                )

                if not st.session_state.fe_ocr_text.strip():
                    st.warning("OCR không đọc được văn bản rõ ràng từ ảnh.")
                else:
                    st.write("OCR hoàn tất.")

                status.update(label="OCR hoàn tất", state="complete", expanded=False)

            except Exception as e:
                st.error(f"Lỗi OCR: {e}")
                st.stop()

    if run_full_pipeline:
        if not api_key:
            st.error("Thiếu API Key để gọi LLM.")
        elif not st.session_state.fe_ocr_text.strip():
            st.error("Không có văn bản OCR để gửi cho LLM.")
        else:
            with st.status("Đang gọi LLM trích xuất thông tin...", expanded=True) as status:
                try:
                    final_label = st.session_state.get("fe_manual_label_select")

                    prompt_text = build_ai_context_prompt(
                        ocr_text=st.session_state.fe_ocr_text,
                        local_pred=st.session_state.fe_local_pred,
                        manual_label=final_label
                    )

                    # Ưu tiên dùng hàm parse cũ để giữ tương thích hệ thống.
                    # Nếu hàm parse_text_with_groq_form của bạn chỉ nhận text OCR,
                    # có thể truyền prompt_text để LLM có thêm ngữ cảnh local model.
                    st.session_state.fe_ai_result = asyncio.run(
                        parse_text_with_groq_form(api_key, prompt_text)
                    )

                    status.update(label="LLM trích xuất hoàn tất", state="complete", expanded=False)

                except Exception as e:
                    st.error(f"Lỗi LLM/API: {e}")
                    st.stop()

    with col_ocr_preview:
        with st.container(border=True):
            st.subheader("Văn bản OCR")

            if st.session_state.fe_ocr_text:
                st.text_area(
                    "Kết quả OCR:",
                    st.session_state.fe_ocr_text,
                    height=320
                )
            else:
                st.info("Chưa có kết quả OCR.")

    if st.session_state.fe_ai_result:
        st.markdown("---")
        display_ai_result(uploaded_image_file.name)

        st.markdown("---")
        display_random_meme()