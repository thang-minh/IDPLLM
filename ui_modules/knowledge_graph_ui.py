# # ui_modules/knowledge_graph_ui.py
# import streamlit as st
# import asyncio
# from streamlit_agraph import agraph, Node, Edge, Config
# from logic.graph_logic import build_graph_data

# def show_knowledge_graph_ui(api_key):
#     st.header("🕸️ Knowledge Graph - Sơ đồ Tri thức Tài liệu")
#     st.markdown("""
#     Trực quan hóa mối quan hệ giữa các tài liệu. 
#     Hệ thống sẽ tự động liên kết các file có cùng **Tên công ty** hoặc **Mã dự án**.
#     """)

#     uploaded_files = st.file_uploader(
#         "Tải lên nhiều file PDF để tìm mối liên hệ (Khuyên dùng: Hợp đồng + Hóa đơn)", 
#         type=['pdf'], 
#         accept_multiple_files=True
#     )

#     if uploaded_files and st.button("🚀 Phân tích & Vẽ Đồ thị"):
#         if not api_key:
#             st.error("Cần API Key để trích xuất thực thể thông minh.")
#             return

#         with st.spinner("🤖 AI đang đọc tài liệu và xâu chuỗi dữ liệu..."):
#             # Chạy logic lấy nodes và edges
#             nodes, edges = asyncio.run(build_graph_data(uploaded_files, api_key))

#         if not nodes:
#             st.warning("Không tìm thấy mối liên hệ nào hoặc không đọc được text.")
#         else:
#             st.success(f"Đã tìm thấy {len(nodes)} đối tượng và {len(edges)} mối liên kết!")
#             st.markdown("---")
            
#             # Cấu hình đồ thị
#             config = Config(
#                 width="100%",
#                 height=600,
#                 directed=False, 
#                 physics=True, 
#                 hierarchy=False,
#                 # Các node cùng nhóm sẽ hút nhau
#                 nodeHighlightBehavior=True, 
#                 highlightColor="#F7A7A6", 
#                 collapsible=True
#             )

#             # VẼ ĐỒ THỊ
#             return_value = agraph(nodes=nodes, edges=edges, config=config)

# ui_modules/knowledge_graph_ui.py

import asyncio
import json

import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Config

from logic.graph_logic import build_graph_data


# =========================================================
# STATE
# =========================================================

def init_kg_state():
    defaults = {
        "kg_nodes": None,
        "kg_edges": None,
        "kg_report": None,
        "kg_last_files": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_kg_state():
    st.session_state.kg_nodes = None
    st.session_state.kg_edges = None
    st.session_state.kg_report = None


# =========================================================
# DISPLAY HELPERS
# =========================================================

def report_to_entity_dataframe(report):
    rows = []

    for doc in report.get("documents", []):
        file_name = doc.get("file_name")
        entities = doc.get("entities", {})

        for entity_type, values in entities.items():
            for value in values:
                rows.append({
                    "Tài liệu": file_name,
                    "Loại thực thể": entity_type,
                    "Giá trị": value,
                })

    return pd.DataFrame(rows)


def report_to_document_link_dataframe(report):
    links = report.get("document_links", [])

    if not links:
        return pd.DataFrame(columns=["Tài liệu 1", "Tài liệu 2", "Loại liên kết", "Giá trị chung"])

    rows = []

    for link in links:
        rows.append({
            "Tài liệu 1": link.get("source"),
            "Tài liệu 2": link.get("target"),
            "Loại liên kết": link.get("shared_type"),
            "Giá trị chung": link.get("shared_value"),
        })

    return pd.DataFrame(rows)


def report_to_doc_status_dataframe(report):
    rows = []

    for doc in report.get("documents", []):
        rows.append({
            "Tài liệu": doc.get("file_name"),
            "Độ dài text": doc.get("text_length"),
            "Cách trích xuất": doc.get("extraction_method"),
        })

    return pd.DataFrame(rows)


# =========================================================
# MAIN UI
# =========================================================

def show_knowledge_graph_ui(api_key, poppler_path_env=None):
    init_kg_state()

    st.markdown(
        "<h1 style='text-align: center;'>Knowledge Graph - Sơ đồ tri thức tài liệu</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style='text-align: center;'>
        Phân tích nhiều tài liệu PDF, trích xuất thực thể và trực quan hóa mối liên hệ giữa 
        <b>tài liệu</b>, <b>công ty</b>, <b>mã số thuế</b>, <b>dự án</b>, <b>hợp đồng</b>, <b>hóa đơn</b>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Tải lên nhiều file PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Nên dùng nhóm tài liệu có liên quan như hợp đồng, hóa đơn, biên bản, báo cáo.",
    )

    if not uploaded_files:
        st.info("Vui lòng tải lên ít nhất 2 file PDF để tạo sơ đồ liên kết.")
        return

    current_files = tuple([f.name for f in uploaded_files])

    if current_files != st.session_state.kg_last_files:
        reset_kg_state()
        st.session_state.kg_last_files = current_files

    with st.container(border=True):
        st.subheader("1. Cấu hình phân tích")

        col1, col2, col3 = st.columns(3)

        with col1:
            use_llm = st.checkbox(
                "Dùng LLM để trích xuất thực thể",
                value=True,
                help="Nếu tắt, hệ thống chỉ dùng regex local. Nếu bật, kết quả chính xác hơn nhưng cần API key.",
            )

        with col2:
            enable_physics = st.checkbox(
                "Bật physics graph",
                value=True,
                help="Bật để graph tự giãn node. Tắt nếu graph bị rung quá nhiều.",
            )

        with col3:
            graph_height = st.slider(
                "Chiều cao graph",
                min_value=400,
                max_value=900,
                value=650,
                step=50,
            )

        if use_llm and not api_key:
            st.warning("Bạn đang bật LLM nhưng chưa có API key. Hệ thống sẽ không thể gọi AI.")

        run_clicked = st.button(
            "Phân tích và tạo Knowledge Graph",
            type="primary",
            use_container_width=True,
        )

    if run_clicked:
        if len(uploaded_files) < 2:
            st.warning("Nên tải ít nhất 2 tài liệu để thấy mối liên hệ.")
        else:
            with st.status("Đang phân tích tài liệu...", expanded=True) as status:
                try:
                    st.write("Đang đọc text/OCR từ PDF...")
                    st.write("Đang trích xuất thực thể...")
                    st.write("Đang xây dựng nodes và edges...")

                    nodes, edges, report = asyncio.run(
                        build_graph_data(
                            uploaded_files=uploaded_files,
                            api_key=api_key,
                            poppler_path_env=poppler_path_env,
                            use_llm=use_llm,
                        )
                    )

                    st.session_state.kg_nodes = nodes
                    st.session_state.kg_edges = edges
                    st.session_state.kg_report = report

                    status.update(
                        label="Hoàn tất tạo Knowledge Graph.",
                        state="complete",
                        expanded=False,
                    )

                    st.rerun()

                except Exception as e:
                    status.update(
                        label="Lỗi khi tạo Knowledge Graph.",
                        state="error",
                        expanded=True,
                    )
                    st.error(f"Lỗi: {e}")

    if not st.session_state.kg_report:
        st.info("Sau khi bấm phân tích, hệ thống sẽ hiển thị graph và bảng thực thể tại đây.")
        return

    nodes = st.session_state.kg_nodes or []
    edges = st.session_state.kg_edges or []
    report = st.session_state.kg_report

    st.markdown("---")
    st.subheader("2. Tổng quan kết quả")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Số tài liệu", len(report.get("documents", [])))

    with c2:
        st.metric("Số node", report.get("node_count", len(nodes)))

    with c3:
        st.metric("Số edge", report.get("edge_count", len(edges)))

    with c4:
        st.metric("Liên kết tài liệu", len(report.get("document_links", [])))

    doc_status_df = report_to_doc_status_dataframe(report)

    with st.expander("Trạng thái đọc tài liệu", expanded=False):
        st.dataframe(doc_status_df, use_container_width=True)

    st.markdown("---")

    tab_graph, tab_entities, tab_links, tab_json = st.tabs(
        [
            "Sơ đồ Knowledge Graph",
            "Bảng thực thể",
            "Liên kết tài liệu",
            "JSON Report",
        ]
    )

    with tab_graph:
        st.subheader("Sơ đồ liên kết")

        if not nodes:
            st.warning("Không có node để vẽ graph.")
        else:
            config = Config(
                width="100%",
                height=graph_height,
                directed=False,
                physics=enable_physics,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#FDE68A",
                collapsible=True,
            )

            agraph(
                nodes=nodes,
                edges=edges,
                config=config,
            )

            st.caption(
                "Gợi ý đọc graph: node màu xanh dương là tài liệu, các node còn lại là thực thể. "
                "Đường nối đỏ giữa hai tài liệu cho biết chúng có chung một thực thể."
            )

    with tab_entities:
        st.subheader("Thực thể được trích xuất")

        entity_df = report_to_entity_dataframe(report)

        if entity_df.empty:
            st.info("Chưa phát hiện thực thể nào.")
        else:
            filter_type = st.multiselect(
                "Lọc theo loại thực thể",
                options=sorted(entity_df["Loại thực thể"].unique()),
                default=sorted(entity_df["Loại thực thể"].unique()),
            )

            filtered_df = entity_df[entity_df["Loại thực thể"].isin(filter_type)]

            st.dataframe(filtered_df, use_container_width=True)

            csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                "Tải bảng thực thể CSV",
                data=csv_data,
                file_name="knowledge_graph_entities.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab_links:
        st.subheader("Các tài liệu có liên quan")

        link_df = report_to_document_link_dataframe(report)

        if link_df.empty:
            st.info("Chưa tìm thấy tài liệu có thực thể chung.")
        else:
            st.dataframe(link_df, use_container_width=True)

            st.markdown("**Diễn giải:**")
            for _, row in link_df.iterrows():
                st.write(
                    f"- `{row['Tài liệu 1']}` liên quan `{row['Tài liệu 2']}` "
                    f"vì cùng `{row['Loại liên kết']}` = **{row['Giá trị chung']}**."
                )

    with tab_json:
        st.subheader("Báo cáo JSON")

        # Không đưa full text vào JSON tải xuống để tránh file quá lớn
        export_report = json.loads(json.dumps(report, ensure_ascii=False, default=str))

        for doc in export_report.get("documents", []):
            if "text" in doc:
                doc["text_preview"] = doc["text"][:500]
                del doc["text"]

        st.json(export_report)

        json_data = json.dumps(
            export_report,
            ensure_ascii=False,
            indent=4,
        )

        st.download_button(
            "Tải JSON report",
            data=json_data,
            file_name="knowledge_graph_report.json",
            mime="application/json",
            use_container_width=True,
        )