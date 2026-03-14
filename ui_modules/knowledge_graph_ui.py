# ui_modules/knowledge_graph_ui.py
import streamlit as st
import asyncio
from streamlit_agraph import agraph, Node, Edge, Config
from logic.graph_logic import build_graph_data

def show_knowledge_graph_ui(api_key):
    st.header("🕸️ Knowledge Graph - Sơ đồ Tri thức Tài liệu")
    st.markdown("""
    Trực quan hóa mối quan hệ giữa các tài liệu. 
    Hệ thống sẽ tự động liên kết các file có cùng **Tên công ty** hoặc **Mã dự án**.
    """)

    uploaded_files = st.file_uploader(
        "Tải lên nhiều file PDF để tìm mối liên hệ (Khuyên dùng: Hợp đồng + Hóa đơn)", 
        type=['pdf'], 
        accept_multiple_files=True
    )

    if uploaded_files and st.button("🚀 Phân tích & Vẽ Đồ thị"):
        if not api_key:
            st.error("Cần API Key để trích xuất thực thể thông minh.")
            return

        with st.spinner("🤖 AI đang đọc tài liệu và xâu chuỗi dữ liệu..."):
            # Chạy logic lấy nodes và edges
            nodes, edges = asyncio.run(build_graph_data(uploaded_files, api_key))

        if not nodes:
            st.warning("Không tìm thấy mối liên hệ nào hoặc không đọc được text.")
        else:
            st.success(f"Đã tìm thấy {len(nodes)} đối tượng và {len(edges)} mối liên kết!")
            st.markdown("---")
            
            # Cấu hình đồ thị
            config = Config(
                width="100%",
                height=600,
                directed=False, 
                physics=True, 
                hierarchy=False,
                # Các node cùng nhóm sẽ hút nhau
                nodeHighlightBehavior=True, 
                highlightColor="#F7A7A6", 
                collapsible=True
            )

            # VẼ ĐỒ THỊ
            return_value = agraph(nodes=nodes, edges=edges, config=config)