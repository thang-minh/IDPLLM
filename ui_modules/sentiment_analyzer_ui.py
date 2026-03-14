# ui_modules/sentiment_analyzer_ui.py
import streamlit as st
import asyncio
import json # Để hiển thị JSON đẹp hơn

from logic.sentiment_analyzer_logic import analyze_sentiment_with_groq
from ui_utils.fun_meme import display_random_meme

def show_sentiment_analyzer_ui(api_key):
    st.markdown("<h1 style='text-align: center;'>🤖 Phân tích Cảm xúc Văn bản</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Nhập một đoạn văn bản để AI phân tích và đánh giá cảm xúc tổng thể.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if 'sa_analysis_result' not in st.session_state: st.session_state.sa_analysis_result = None
    
    with st.container(border=True):
        st.subheader("📝 Nhập văn bản cần phân tích:")
        text_input = st.text_area(
            "Nội dung văn bản:",
            height=200,
            key="sa_text_input",
            placeholder="Ví dụ: Hôm nay trời đẹp và tôi cảm thấy rất vui!"
        )

        if st.button("🔍 Phân tích Cảm xúc Ngay", key="sa_analyze_button", type="primary", use_container_width=True, disabled=not text_input.strip()):
            if not api_key:
                st.error("API Key chưa được cấu hình. Không thể phân tích cảm xúc.")
            elif not text_input.strip():
                st.warning("Vui lòng nhập văn bản để phân tích.")
            else:
                with st.spinner("💬 AI đang phân tích cảm xúc..."):
                    try:
                        st.session_state.sa_analysis_result = asyncio.run(analyze_sentiment_with_groq(api_key, text_input))
                    except ValueError as ve:
                        st.error(f"Lỗi AI: {ve}")
                        st.session_state.sa_analysis_result = {"error": str(ve)}
                    except Exception as e_sa:
                        st.error(f"Lỗi không mong muốn khi phân tích cảm xúc: {e_sa}")
                        st.session_state.sa_analysis_result = {"error": str(e_sa)}
    
    if st.session_state.sa_analysis_result:
        st.markdown("---")
        with st.container(border=True):
            st.subheader("📈 Kết quả Phân tích Cảm xúc:")
            result = st.session_state.sa_analysis_result
            if "error" in result:
                st.error(f"Lỗi: {result['error']}")
                if "raw_response" in result:
                    with st.expander("Xem phản hồi gốc từ AI"):
                        st.text(result["raw_response"])
            else:
                col_main, col_score = st.columns([3,1])
                with col_main:
                    st.info(f"**Cảm xúc chính:** {result.get('cam_xuc_chinh', 'N/A')}")
                    st.write(f"**Giải thích:** {result.get('giai_thich_ngan', 'N/A')}")
                with col_score:
                    score = result.get('diem_so_cam_xuc', 0.0)
                    if score > 0.5: color = "green"
                    elif score > 0.1: color = "lightgreen"
                    elif score < -0.5: color = "red"
                    elif score < -0.1: color = "pink"
                    else: color = "grey"
                    st.metric(label="Điểm số Cảm xúc", value=f"{score:.2f}", delta_color="off", 
                              help="Từ -1.0 (rất tiêu cực) đến 1.0 (rất tích cực)")
                    st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:5px; border-radius:5px;'>{score:.2f}</div>", unsafe_allow_html=True)


                st.write(f"**Từ khóa cảm xúc:** {', '.join(result.get('tu_khoa_cam_xuc', ['N/A']))}")
                
                with st.expander("Xem chi tiết JSON kết quả"):
                    st.json(result)
        st.markdown("---")
        display_random_meme()