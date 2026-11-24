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

def display_sentiment_result(result: dict):
    if not result:
        return

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-weight: 700; font-size: 15px; color: #0F172A;">2. Kết quả Phân tích Cảm xúc</span>
            <span class="badge-soft-indigo">AI Sentiment Output</span>
        </div>
        """, unsafe_allow_html=True)

        if "error" in result:
            st.error(result["error"])
            return

        score = float(result.get("diem_so_cam_xuc", 0.0))
        confidence = float(result.get("do_tin_cay", 0.0))
        sentiment_label = result.get("cam_xuc_chinh", "Không xác định")

        # Soft Badge tương ứng với điểm cảm xúc
        if score >= 0.15:
            badge_sentiment = f'<span class="badge-soft-success">● {sentiment_label} (Tích cực)</span>'
        elif score <= -0.15:
            badge_sentiment = f'<span class="badge-soft-danger">● {sentiment_label} (Tiêu cực)</span>'
        else:
            badge_sentiment = f'<span class="badge-soft-neutral">● {sentiment_label} (Trung tính)</span>'

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.05em; margin-bottom: 6px;">
                Phân loại cảm xúc
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #0F172A; margin-bottom: 8px;">
                {sentiment_label}
            </div>
            {badge_sentiment}
            """, unsafe_allow_html=True)

        with col2:
            st.metric("Chỉ số Cảm xúc (Score)", f"{score:+.2f}", help="Thang điểm từ -1.0 (Rất tiêu cực) đến +1.0 (Rất tích cực)")

        with col3:
            st.metric("Độ tin cậy của AI", f"{confidence * 100:.1f}%")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Progress bar chuẩn hóa từ -1..1 sang 0..1
        normalized = max(0.0, min(1.0, (score + 1.0) / 2.0))
        st.progress(normalized, text=f"Thang cảm xúc: {score:+.2f}  (-1.0 Tiêu cực ➔ 0.0 Trung tính ➔ +1.0 Tích cực)")

        # Chi tiết phân tích
        explanation = result.get("giai_thich_ngan", "")
        if explanation:
            st.markdown(f"""
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 12px 14px; margin: 12px 0; font-size: 13.5px; color: #1E40AF; line-height: 1.5;">
                <b>💡 Giải thích của AI:</b><br/>{explanation}
            </div>
            """, unsafe_allow_html=True)

        # Từ khóa cảm xúc
        keywords = result.get("tu_khoa_cam_xuc", [])
        if keywords:
            tags_html = " ".join([f'<span class="badge-soft-neutral" style="margin-right: 4px;">{kw}</span>' for kw in keywords])
            st.markdown(f"**Từ khóa trọng tâm:** &nbsp;{tags_html}", unsafe_allow_html=True)

        # Gợi ý xử lý
        suggestions = result.get("goi_y_xu_ly", [])
        if suggestions:
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            st.markdown("**Gợi ý phản hồi / hướng xử lý đề xuất:**")
            for item in suggestions:
                st.markdown(f"- {item}")

        with st.expander("🧾 Xem định dạng JSON gốc"):
            st.json(result)
            json_data = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                "Tải xuống JSON",
                data=json_data,
                file_name="sentiment_analysis.json",
                mime="application/json",
                use_container_width=True
            )

def display_sentiment_history():
    history = st.session_state.get("sa_history", [])
    if not history:
        return

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: 700; font-size: 15px; color: #0F172A;">3. Lịch sử Phân tích Phiên làm việc</span>
            <span class="badge-soft-neutral">Session History</span>
        </div>
        """, unsafe_allow_html=True)

        rows = []
        for item in history:
            result = item.get("result", {})
            rows.append({
                "Thời gian": item.get("time"),
                "Văn bản trích đoạn": item.get("text_preview"),
                "Cảm xúc": result.get("cam_xuc_chinh", "N/A"),
                "Điểm số": result.get("diem_so_cam_xuc", 0.0),
                "Độ tin cậy": f"{float(result.get('do_tin_cay', 0.0))*100:.0f}%",
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        c_dl, c_clear = st.columns([2, 1])
        with c_dl:
            csv_data = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 Xuất Lịch sử ra CSV",
                data=csv_data,
                file_name="sentiment_history.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_clear:
            if st.button("Xóa Lịch sử", use_container_width=True):
                st.session_state.sa_history = []
                st.rerun()

def show_sentiment_analyzer_ui(api_key):
    init_sentiment_state()

    # Header chuẩn SaaS
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-soft-indigo">NLP Analytics</span>
                <span class="badge-soft-success">Sentiment AI</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em; color: #0F172A;">Phân tích Cảm xúc Văn bản</h2>
            <p style="color: #475569; font-size: 14px; margin: 4px 0 0 0;">
                Đánh giá sắc thái cảm xúc, trích xuất từ khóa chủ đạo và đưa ra khuyến nghị phản hồi tối ưu bằng mô hình ngôn ngữ lớn.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #0F172A;">1. Nội dung Phân tích</span>
            <span class="badge-soft-neutral">Input Text</span>
        </div>
        """, unsafe_allow_html=True)

        example_type = st.selectbox(
            "Chọn mẫu phản hồi có sẵn để thử nghiệm:",
            [
                "Không dùng ví dụ",
                "Đánh giá tích cực (Hài lòng dịch vụ)",
                "Đánh giá tiêu cực (Khiếu nại sản phẩm)",
                "Phản hồi trung tính (Xác nhận thông tin)",
                "Phản hồi hỗn hợp (Vừa khen vừa góp ý)",
            ]
        )

        examples = {
            "Đánh giá tích cực (Hài lòng dịch vụ)": "Dịch vụ hỗ trợ giải quyết hồ sơ rất nhanh chóng, giao diện dễ dùng và xử lý tài liệu chính xác tuyệt đối. Tôi rất hài lòng!",
            "Đánh giá tiêu cực (Khiếu nại sản phẩm)": "Hệ thống phản hồi quá chậm, tài liệu scan bị lỗi không đọc được chữ, yêu cầu bên kỹ thuật kiểm tra và hoàn tiền gấp!",
            "Phản hồi trung tính (Xác nhận thông tin)": "Tôi đã nhận được bản hợp đồng điện tử qua email. Sẽ xem xét và phản hồi lại vào thứ Hai tuần tới.",
            "Phản hồi hỗn hợp (Vừa khen vừa góp ý)": "Tính năng OCR nhận diện khá tốt, tuy nhiên tốc độ trích xuất bảng biểu cần cải thiện thêm để mượt mà hơn.",
        }

        default_text = ""
        if example_type != "Không dùng ví dụ":
            default_text = examples.get(example_type, "")

        text_input = st.text_area(
            "Nội dung văn bản cần đánh giá:",
            value=default_text,
            height=160,
            key="sa_text_input",
            placeholder="Nhập hoặc dán nội dung email, tin nhắn chăm sóc khách hàng, review đánh giá sản phẩm..."
        )

        col_run, col_clear = st.columns([2, 1])
        with col_run:
            analyze_clicked = st.button(
                "🚀 Phân tích Sắc thái Cảm xúc",
                type="primary",
                use_container_width=True,
                disabled=not text_input.strip()
            )
        with col_clear:
            if st.button("Làm mới", use_container_width=True):
                st.session_state.sa_analysis_result = None
                st.rerun()

        if analyze_clicked:
            if not api_key:
                st.error("Chưa cấu hình API Key trong file .env!")
            else:
                with st.status("AI đang phân tích ngữ cảnh và cảm xúc...", expanded=True) as status:
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
                                "text_preview": text_input[:100] + ("..." if len(text_input) > 100 else ""),
                                "result": result,
                            })
                            st.session_state.sa_history = st.session_state.sa_history[:20]
                        status.update(label="✓ Phân tích cảm xúc hoàn tất!", state="complete", expanded=False)
                    except Exception as e:
                        st.session_state.sa_analysis_result = {"error": f"Lỗi: {str(e)}"}
                        status.update(label="Phân tích thất bại.", state="error")

    display_sentiment_result(st.session_state.sa_analysis_result)
    display_sentiment_history()

    if st.session_state.sa_analysis_result and "error" not in st.session_state.sa_analysis_result:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        display_random_meme()
