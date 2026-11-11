# ui_modules/knowledge_graph_ui.py
import asyncio
import json
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Config

from logic.graph_logic import build_graph_data
from ui_utils.ui_components import render_page_header, render_empty_state

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
            "Độ dài văn bản": doc.get("text_length"),
            "Phương thức trích xuất": doc.get("extraction_method"),
        })
    return pd.DataFrame(rows)

def show_knowledge_graph_ui(api_key, poppler_path_env=None):
    init_kg_state()

    badges = [
        {"text": "● Graph Network", "type": "indigo"},
        {"text": "Entity Linking", "type": "neutral"},
    ]
    render_page_header(
        title="Knowledge Graph & Entity Linking",
        description="Trực quan hóa mạng lưới quan hệ thực thể, phát hiện liên kết chéo giữa nhiều tài liệu (Hợp đồng, Hóa đơn, Mã dự án).",
        breadcrumb="AI KNOWLEDGE / KNOWLEDGE GRAPH",
        badges=badges
    )

    uploaded_files = st.file_uploader(
        "Tải lên nhiều tập tin PDF để xây dựng sơ đồ quan hệ:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Khuyến nghị: Tải lên nhóm tài liệu cùng dự án như Hợp đồng, Hóa đơn thanh toán, Phụ lục và Biên bản giao nhận."
    )

    if not uploaded_files:
        render_empty_state(
            icon="🕸️",
            title="Chưa có tài liệu nào được chọn",
            description="Hãy tải lên ít nhất 2 tập tin PDF để hệ thống phân tích thực thể chung và vẽ sơ đồ mạng lưới liên kết."
        )
        return

    current_files = tuple([f.name for f in uploaded_files])
    if current_files != st.session_state.kg_last_files:
        reset_kg_state()
        st.session_state.kg_last_files = current_files

    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #0F172A;">⚙️ Tham số Phân tích Đồ thị</span>
            <span class="badge-soft-neutral">Graph Configuration</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            use_llm = st.checkbox("Sử dụng LLM trích xuất thực thể", value=True, help="Kết hợp mô hình AI để trích xuất thực thể ngữ nghĩa chính xác hơn.")
        with col2:
            enable_physics = st.checkbox("Bật mô phỏng vật lý (Physics)", value=True, help="Tự động dãn khoảng cách các node trong không gian 2D.")
        with col3:
            graph_height = st.slider("Chiều cao khung vẽ (px):", min_value=450, max_value=850, value=600, step=50)

        if use_llm and not api_key:
            st.warning("Chưa cấu hình API Key. Hệ thống sẽ tự động dùng bộ bóc tách quy tắc biểu thức chính quy (Regex).")

        run_clicked = st.button("🚀 Khởi tạo Sơ đồ Tri thức", type="primary", use_container_width=True)

    if run_clicked:
        if len(uploaded_files) < 2:
            st.warning("Cần tối thiểu 2 tài liệu để thiết lập quan hệ chéo giữa các hồ sơ.")
        else:
            with st.status("Đang đọc và khai phá thực thể từ các tệp PDF...", expanded=True) as status:
                try:
                    status.write("1/3 Trích xuất văn bản và bóc tách thực thể (Công ty, MST, Hợp đồng)...")
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
                    status.update(label="✓ Xây dựng Knowledge Graph thành công!", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    status.update(label="Lỗi khởi tạo đồ thị.", state="error")
                    st.error(f"Lỗi: {e}")

    if not st.session_state.kg_report:
        return

    nodes = st.session_state.kg_nodes or []
    edges = st.session_state.kg_edges or []
    report = st.session_state.kg_report

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Tổng quan Mạng lưới Tri thức")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tài liệu nạp", len(report.get("documents", [])))
    with c2:
        st.metric("Tổng số Nodes", report.get("node_count", len(nodes)))
    with c3:
        st.metric("Liên kết (Edges)", report.get("edge_count", len(edges)))
    with c4:
        st.metric("Mối nối Tài liệu", len(report.get("document_links", [])))

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    tab_graph, tab_entities, tab_links, tab_json = st.tabs([
        "🕸️ Sơ đồ Tương tác",
        "📋 Danh mục Thực thể",
        "🔗 Liên kết Đối ứng",
        "🧾 Báo cáo JSON"
    ])

    with tab_graph:
        if not nodes:
            st.warning("Không có node nào được tạo từ tập tài liệu này.")
        else:
            with st.container(border=True):
                config = Config(
                    width="100%",
                    height=graph_height,
                    directed=False,
                    physics=enable_physics,
                    hierarchical=False,
                    nodeHighlightBehavior=True,
                    highlightColor="#EEF2FF",
                    collapsible=True,
                )
                agraph(nodes=nodes, edges=edges, config=config)
                st.caption("ℹ️ Node màu xanh là hồ sơ tài liệu. Các node còn lại là thực thể được chia sẻ giữa các tài liệu.")

    with tab_entities:
        with st.container(border=True):
            entity_df = report_to_entity_dataframe(report)
            if entity_df.empty:
                st.info("Chưa phát hiện thực thể phù hợp.")
            else:
                f_types = st.multiselect(
                    "Lọc loại thực thể:",
                    options=sorted(entity_df["Loại thực thể"].unique()),
                    default=sorted(entity_df["Loại thực thể"].unique())
                )
                filtered_df = entity_df[entity_df["Loại thực thể"].isin(f_types)]
                st.dataframe(filtered_df, use_container_width=True)

                csv_bytes = filtered_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 Tải danh mục CSV",
                    data=csv_bytes,
                    file_name="knowledge_entities.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with tab_links:
        with st.container(border=True):
            link_df = report_to_document_link_dataframe(report)
            if link_df.empty:
                st.info("Không tìm thấy mối liên hệ trực tiếp giữa các tài liệu.")
            else:
                st.dataframe(link_df, use_container_width=True)
                st.markdown("**Diễn giải quan hệ:**")
                for _, r in link_df.iterrows():
                    st.markdown(f"- **`{r['Tài liệu 1']}`** kết nối với **`{r['Tài liệu 2']}`** qua thuộc tính `{r['Loại liên kết']}`: **{r['Giá trị chung']}**")

    with tab_json:
        with st.container(border=True):
            export_report = json.loads(json.dumps(report, ensure_ascii=False, default=str))
            for doc in export_report.get("documents", []):
                if "text" in doc:
                    doc["text_preview"] = doc["text"][:300]
                    del doc["text"]
            st.json(export_report)
            st.download_button(
                "📥 Tải Báo cáo Graph JSON",
                data=json.dumps(export_report, ensure_ascii=False, indent=2),
                file_name="knowledge_graph_report.json",
                mime="application/json",
                type="primary",
                use_container_width=True
            )
