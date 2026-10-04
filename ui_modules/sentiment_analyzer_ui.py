# # ui_modules/sentiment_analyzer_ui.py
# import streamlit as st
# import asyncio
# import json # Để hiển thị JSON đẹp hơn

# from logic.sentiment_analyzer_logic import analyze_sentiment_with_groq
# from ui_utils.fun_meme import display_random_meme

# def show_sentiment_analyzer_ui(api_key):
#     st.markdown("<h1 style='text-align: center;'>🤖 Phân tích Cảm xúc Văn bản</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Nhập một đoạn văn bản để AI phân tích và đánh giá cảm xúc tổng thể.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     if 'sa_analysis_result' not in st.session_state: st.session_state.sa_analysis_result = None
    
#     with st.container(border=True):
#         st.subheader("📝 Nhập văn bản cần phân tích:")
#         text_input = st.text_area(
#             "Nội dung văn bản:",
#             height=200,
#             key="sa_text_input",
#             placeholder="Ví dụ: Hôm nay trời đẹp và tôi cảm thấy rất vui!"
#         )

#         if st.button("🔍 Phân tích Cảm xúc Ngay", key="sa_analyze_button", type="primary", use_container_width=True, disabled=not text_input.strip()):
#             if not api_key:
#                 st.error("API Key chưa được cấu hình. Không thể phân tích cảm xúc.")
#             elif not text_input.strip():
#                 st.warning("Vui lòng nhập văn bản để phân tích.")
#             else:
#                 with st.spinner("💬 AI đang phân tích cảm xúc..."):
#                     try:
#                         st.session_state.sa_analysis_result = asyncio.run(analyze_sentiment_with_groq(api_key, text_input))
#                     except ValueError as ve:
#                         st.error(f"Lỗi AI: {ve}")
#                         st.session_state.sa_analysis_result = {"error": str(ve)}
#                     except Exception as e_sa:
#                         st.error(f"Lỗi không mong muốn khi phân tích cảm xúc: {e_sa}")
#                         st.session_state.sa_analysis_result = {"error": str(e_sa)}
    
#     if st.session_state.sa_analysis_result:
#         st.markdown("---")
#         with st.container(border=True):
#             st.subheader("📈 Kết quả Phân tích Cảm xúc:")
#             result = st.session_state.sa_analysis_result
#             if "error" in result:
#                 st.error(f"Lỗi: {result['error']}")
#                 if "raw_response" in result:
#                     with st.expander("Xem phản hồi gốc từ AI"):
#                         st.text(result["raw_response"])
#             else:
#                 col_main, col_score = st.columns([3,1])
#                 with col_main:
#                     st.info(f"**Cảm xúc chính:** {result.get('cam_xuc_chinh', 'N/A')}")
#                     st.write(f"**Giải thích:** {result.get('giai_thich_ngan', 'N/A')}")
#                 with col_score:
#                     score = result.get('diem_so_cam_xuc', 0.0)
#                     if score > 0.5: color = "green"
#                     elif score > 0.1: color = "lightgreen"
#                     elif score < -0.5: color = "red"
#                     elif score < -0.1: color = "pink"
#                     else: color = "grey"
#                     st.metric(label="Điểm số Cảm xúc", value=f"{score:.2f}", delta_color="off", 
#                               help="Từ -1.0 (rất tiêu cực) đến 1.0 (rất tích cực)")
#                     st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:5px; border-radius:5px;'>{score:.2f}</div>", unsafe_allow_html=True)


#                 st.write(f"**Từ khóa cảm xúc:** {', '.join(result.get('tu_khoa_cam_xuc', ['N/A']))}")
                
#                 with st.expander("Xem chi tiết JSON kết quả"):
#                     st.json(result)
#         st.markdown("---")
#         display_random_meme()

# ui_modules/sentiment_analyzer_ui.py

import asyncio
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from logic.sentiment_analyzer_logic import analyze_sentiment_with_groq
from ui_utils.fun_meme import display_random_meme


def init_sentiment_state():
    defaults = {
        "sa_analysis_result": None,
        "sa_history": [],
        "sa_last_text": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_sentiment_status(score: float):
    if score >= 0.6:
        return "Rất tích cực", "success"
    if score >= 0.15:
        return "Tích cực", "success"
    if score > -0.15:
        return "Trung tính", "info"
    if score > -0.6:
        return "Tiêu cực", "warning"
    return "Rất tiêu cực", "error"


def display_score_bar(score: float):
    normalized = (score + 1) / 2
    normalized = max(0.0, min(1.0, normalized))

    st.progress(
        normalized,
        text=f"Thang điểm cảm xúc: {score:.2f}  |  -1.0 rất tiêu cực → 1.0 rất tích cực"
    )


def display_sentiment_result(result: dict):
    if not result:
        return

    st.markdown("---")
    st.subheader("2. Kết quả phân tích cảm xúc")

    if "error" in result:
        st.error(result["error"])

        if "raw_response" in result:
            with st.expander("Xem phản hồi gốc từ AI"):
                st.text(result["raw_response"])

        return

    score = float(result.get("diem_so_cam_xuc", 0.0))
    confidence = float(result.get("do_tin_cay", 0.0))
    sentiment_label = result.get("cam_xuc_chinh", "Không xác định")
    status_label, status_type = get_sentiment_status(score)

    col1, col2, col3 = st.columns(3)

    with col1:
        if status_type == "success":
            st.success(f"Cảm xúc chính: **{sentiment_label}**")
        elif status_type == "warning":
            st.warning(f"Cảm xúc chính: **{sentiment_label}**")
        elif status_type == "error":
            st.error(f"Cảm xúc chính: **{sentiment_label}**")
        else:
            st.info(f"Cảm xúc chính: **{sentiment_label}**")

    with col2:
        st.metric("Điểm cảm xúc", f"{score:.2f}")

    with col3:
        st.metric("Độ tin cậy", f"{confidence * 100:.1f}%")

    display_score_bar(score)

    st.write(f"**Mức độ:** {result.get('muc_do', 'Không xác định')}")
    st.write(f"**Ngôn ngữ:** {result.get('ngon_ngu', 'Không xác định')}")

    secondary_emotions = result.get("cam_xuc_phu", [])

    if secondary_emotions:
        st.write("**Cảm xúc phụ:**")
        st.write(", ".join(secondary_emotions))

    keywords = result.get("tu_khoa_cam_xuc", [])

    if keywords:
        st.write("**Từ khóa/cụm từ cảm xúc:**")
        st.write(", ".join(keywords))

    explanation = result.get("giai_thich_ngan", "")

    if explanation:
        st.markdown("**Giải thích:**")
        st.info(explanation)

    suggestions = result.get("goi_y_xu_ly", [])

    if suggestions:
        st.markdown("**Gợi ý xử lý/phản hồi:**")
        for item in suggestions:
            st.write(f"- {item}")

    with st.expander("Xem JSON kết quả", expanded=False):
        st.json(result)

        json_data = json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        )

        st.download_button(
            "Tải kết quả JSON",
            data=json_data,
            file_name="sentiment_analysis_result.json",
            mime="application/json",
            use_container_width=True
        )


def display_sentiment_history():
    history = st.session_state.get("sa_history", [])

    if not history:
        return

    st.markdown("---")
    st.subheader("3. Lịch sử phân tích trong phiên")

    rows = []

    for item in history:
        result = item.get("result", {})
        rows.append({
            "Thời gian": item.get("time"),
            "Văn bản": item.get("text_preview"),
            "Cảm xúc": result.get("cam_xuc_chinh", "N/A"),
            "Điểm": result.get("diem_so_cam_xuc", 0.0),
            "Độ tin cậy": result.get("do_tin_cay", 0.0),
        })

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Tải lịch sử CSV",
        data=csv_data,
        file_name="sentiment_history.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("Xóa lịch sử", use_container_width=True):
        st.session_state.sa_history = []
        st.success("Đã xóa lịch sử.")
        st.rerun()


def show_sentiment_analyzer_ui(api_key):
    init_sentiment_state()

    st.markdown(
        "<h1 style='text-align: center;'>Phân tích cảm xúc văn bản</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align: center;'>
        Nhập văn bản để AI đánh giá cảm xúc tổng thể, điểm cảm xúc, từ khóa ảnh hưởng và gợi ý xử lý.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    with st.container(border=True):
        st.subheader("1. Nhập văn bản")

        example_type = st.selectbox(
            "Chọn ví dụ nhanh",
            [
                "Không dùng ví dụ",
                "Đánh giá tích cực",
                "Đánh giá tiêu cực",
                "Phản hồi trung tính",
                "Phản hồi hỗn hợp",
            ]
        )

        examples = {
            "Đánh giá tích cực": "Sản phẩm giao nhanh, đóng gói cẩn thận, chất lượng rất tốt. Tôi rất hài lòng và sẽ tiếp tục ủng hộ.",
            "Đánh giá tiêu cực": "Dịch vụ quá tệ, giao hàng chậm, nhân viên hỗ trợ không nhiệt tình. Tôi cảm thấy rất thất vọng.",
            "Phản hồi trung tính": "Tôi đã nhận được sản phẩm. Chất lượng ở mức bình thường, chưa có điểm gì quá nổi bật.",
            "Phản hồi hỗn hợp": "Sản phẩm khá tốt và giá hợp lý, nhưng thời gian giao hàng hơi lâu và hộp bị móp nhẹ.",
        }

        default_text = ""

        if example_type != "Không dùng ví dụ":
            default_text = examples[example_type]

        text_input = st.text_area(
            "Nội dung văn bản:",
            value=default_text,
            height=220,
            key="sa_text_input",
            placeholder="Ví dụ: Hôm nay trời đẹp và tôi cảm thấy rất vui!"
        )

        col_run, col_clear = st.columns([2, 1])

        with col_run:
            analyze_clicked = st.button(
                "Phân tích cảm xúc",
                type="primary",
                use_container_width=True,
                disabled=not text_input.strip()
            )

        with col_clear:
            clear_clicked = st.button(
                "Xóa kết quả",
                use_container_width=True
            )

        if clear_clicked:
            st.session_state.sa_analysis_result = None
            st.rerun()

        if analyze_clicked:
            if not api_key:
                st.error("API Key chưa được cấu hình. Không thể phân tích cảm xúc.")
            elif not text_input.strip():
                st.warning("Vui lòng nhập văn bản để phân tích.")
            else:
                with st.status("AI đang phân tích cảm xúc...", expanded=True) as status:
                    try:
                        result = asyncio.run(
                            analyze_sentiment_with_groq(
                                api_key=api_key,
                                text_to_analyze=text_input
                            )
                        )

                        st.session_state.sa_analysis_result = result

                        if "error" not in result:
                            st.session_state.sa_history.insert(0, {
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "text_preview": text_input[:120] + ("..." if len(text_input) > 120 else ""),
                                "result": result,
                            })

                            st.session_state.sa_history = st.session_state.sa_history[:20]

                        status.update(
                            label="Phân tích hoàn tất.",
                            state="complete",
                            expanded=False
                        )

                    except Exception as e:
                        st.session_state.sa_analysis_result = {
                            "error": f"Lỗi không mong muốn: {str(e)}"
                        }

                        status.update(
                            label="Phân tích thất bại.",
                            state="error",
                            expanded=True
                        )

    display_sentiment_result(st.session_state.sa_analysis_result)

    display_sentiment_history()

    if st.session_state.sa_analysis_result and "error" not in st.session_state.sa_analysis_result:
        st.markdown("---")
        display_random_meme()