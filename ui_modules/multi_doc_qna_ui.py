# ui_modules/multi_doc_qna_ui.py
import streamlit as st
import asyncio

from logic.multi_doc_qna_logic import (
    extract_text_from_uploaded_files,
    get_text_chunks,
    get_embedding_model,
    create_vector_store_from_chunks,
    search_similar_chunks,
    get_answer_from_llm_with_context
)
from ui_utils.fun_meme import display_random_meme

# =========================================================
# HELPER FUNCTIONS & STATE
# =========================================================

def init_session_state_mdqna():
    defaults = {
        "mdqna_vector_store": None,
        "mdqna_embedding_model": None,
        "mdqna_processed_files": set(),
        "mdqna_retrieved_chunks": [],
        "mdqna_llm_answer": "",
        "mdqna_total_chunks": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_pipeline_tracker(current_step: int):
    steps = [
        ("1. Nạp Tài liệu PDF", 1),
        ("2. Xây dựng Vector FAISS", 2),
        ("3. Hỏi đáp RAG & Đối thoại", 3)
    ]
    html_parts = []
    for label, step_idx in steps:
        if step_idx < current_step:
            cls = "pipeline-step completed"
            icon = "✓"
        elif step_idx == current_step:
            cls = "pipeline-step active"
            icon = "●"
        else:
            cls = "pipeline-step"
            icon = "○"
        html_parts.append(f'<span class="{cls}">{icon} {label}</span>')

    separator = '<span class="pipeline-separator"> ➔ </span>'
    bar_html = f'<div class="pipeline-step-bar">{separator.join(html_parts)}</div>'
    st.markdown(bar_html, unsafe_allow_html=True)

# =========================================================
# MAIN MULTI-DOC Q&A UI (RAG ENGINE)
# =========================================================

def show_multi_doc_qna_ui(api_key, poppler_path_env=None):
    init_session_state_mdqna()

    # SaaS Header
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="saas-badge saas-badge-indigo">RAG Knowledge Engine</span>
                <span class="saas-badge saas-badge-success">FAISS Vector Search</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em;">Hỏi đáp & Tìm kiếm Đa Tài liệu</h2>
            <p style="color: #64748B; font-size: 14px; margin: 4px 0 0 0;">
                Truy vấn ngữ nghĩa và tương tác với kho tài liệu bằng mô hình nhúng vector Sentence-Transformers và LLM RAG.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Xác định step hiện tại cho Tracker
    step = 1
    if st.session_state.mdqna_vector_store is not None:
        step = 3
    render_pipeline_tracker(step)

    # =========================================================
    # SPLIT VIEW 2 CỘT NGANG HÀNG
    # CỘT TRÁI: QUẢN LÝ TẬP TIN & INDEXING VECTOR
    # CỘT PHẢI: TRUY VẤN NGỮ NGHĨA & HỎI ĐÁP RAG
    # =========================================================
    col_files, col_chat = st.columns([1, 1.25], gap="large")

    with col_files:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px;">1. Kho Tài liệu PDF Nguồn</span>
                <span class="saas-badge saas-badge-indigo">Multi-PDF</span>
            </div>
            """, unsafe_allow_html=True)

            uploaded_files = st.file_uploader(
                "Tải lên một hoặc nhiều file PDF:",
                type="pdf",
                accept_multiple_files=True,
                key="mdqna_file_uploader",
                help="Chọn nhiều tập tin PDF để tạo chỉ mục vector dùng chung."
            )

            new_files_to_process = []
            if uploaded_files:
                current_file_names = {f.name for f in uploaded_files}
                if not st.session_state.mdqna_processed_files.issuperset(current_file_names) or not st.session_state.mdqna_vector_store:
                    new_files_to_process = uploaded_files

                # Danh sách file đã chọn
                st.markdown("**Danh sách tài liệu đã nạp:**")
                for f in uploaded_files:
                    is_indexed = f.name in st.session_state.mdqna_processed_files
                    badge_status = '<span class="saas-badge saas-badge-success">Đã index</span>' if is_indexed else '<span class="saas-badge saas-badge-warning">Chờ index</span>'
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: rgba(0,0,0,0.02); border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 4px; font-size: 13px;">
                        <span>📄 <b>{f.name}</b> ({len(f.getvalue())/1024:.1f} KB)</span>
                        {badge_status}
                    </div>
                    """, unsafe_allow_html=True)

                if new_files_to_process:
                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    if st.button("⚡ Xây dựng Chỉ mục Vector (FAISS)", type="primary", use_container_width=True, key="mdqna_process_button"):
                        with st.status("Đang xây dựng cơ sở tri thức vector...", expanded=True) as status:
                            try:
                                status.write("1/4 Trích xuất nội dung văn bản từ các tệp PDF...")
                                docs_data = extract_text_from_uploaded_files(new_files_to_process, poppler_path_env)
                                if not docs_data:
                                    st.warning("Không có nội dung văn bản hợp lệ để xử lý.")
                                    return

                                status.write("2/4 Phân rã văn bản thành các đoạn (Text Chunking)...")
                                text_chunks_with_metadata = get_text_chunks(docs_data)
                                if not text_chunks_with_metadata:
                                    st.warning("Không thể phân rã thành các chunk.")
                                    return

                                st.session_state.mdqna_total_chunks = len(text_chunks_with_metadata)

                                status.write("3/4 Nạp mô hình Embedding Sentence-Transformers...")
                                if st.session_state.mdqna_embedding_model is None:
                                    st.session_state.mdqna_embedding_model = get_embedding_model(
                                        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
                                    )

                                status.write(f"4/4 Tính toán vector và lưu vào FAISS Index ({len(text_chunks_with_metadata)} chunks)...")
                                st.session_state.mdqna_vector_store = create_vector_store_from_chunks(
                                    text_chunks_with_metadata,
                                    st.session_state.mdqna_embedding_model
                                )

                                if st.session_state.mdqna_vector_store:
                                    st.session_state.mdqna_processed_files.update(current_file_names)
                                    status.update(label=f"✓ Đã index thành công {len(new_files_to_process)} tài liệu!", state="complete", expanded=False)
                                    st.rerun()
                                else:
                                    st.error("Không thể khởi tạo FAISS vector store.")
                            except Exception as e:
                                st.error(f"Lỗi xây dựng index: {e}")
            else:
                st.caption("Hãy tải lên ít nhất một file PDF để bắt đầu xây dựng cơ sở tri thức.")

        # Thống kê Vector Store
        if st.session_state.mdqna_vector_store:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 14px;">📊 Trạng thái Cơ sở Tri thức</span>
                    <span class="saas-badge saas-badge-success">Ready</span>
                </div>
                """, unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Tài liệu đã nạp", len(st.session_state.mdqna_processed_files))
                with m2:
                    st.metric("Vector Chunks", st.session_state.mdqna_total_chunks or "Ready")

    with col_chat:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px;">2. Truy vấn Ngữ nghĩa & Hỏi đáp RAG</span>
                <span class="saas-badge saas-badge-indigo">Interactive</span>
            </div>
            """, unsafe_allow_html=True)

            if not st.session_state.mdqna_vector_store:
                st.markdown("""
                <div style="background: rgba(79, 70, 229, 0.03); border: 1px dashed #CBD5E1; border-radius: 10px; padding: 2.5rem 1.5rem; text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 8px;">💬</div>
                    <div style="font-weight: 600; color: #0F172A; font-size: 14px;">Chờ xây dựng cơ sở tri thức</div>
                    <div style="color: #64748B; font-size: 12.5px; max-width: 380px; margin: 4px auto 0 auto;">
                        Sau khi nạp PDF và tạo index vector ở cột bên trái, bạn có thể đặt câu hỏi hoặc tra cứu văn bản theo ngữ nghĩa tại đây.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return

            query = st.text_input(
                "Nhập câu hỏi hoặc nội dung cần tra cứu:",
                key="mdqna_query_input",
                placeholder="Ví dụ: Nghĩa vụ của bên A trong hợp đồng là gì? Số tiền thanh toán đợt 1 bao nhiêu?"
            )

            btn_c1, btn_c2 = st.columns(2)
            with btn_c1:
                run_search = st.button("🔍 Tìm Đoạn liên quan (FAISS)", use_container_width=True, disabled=not query.strip())
            with btn_c2:
                run_rag = st.button("🤖 Hỏi Đáp Bằng AI (RAG)", type="primary", use_container_width=True, disabled=not query.strip() or not api_key)

            if run_search:
                with st.spinner("Đang truy vấn các đoạn văn bản tương đồng cao nhất..."):
                    st.session_state.mdqna_llm_answer = ""
                    try:
                        st.session_state.mdqna_retrieved_chunks = search_similar_chunks(
                            query, st.session_state.mdqna_vector_store, top_k=5
                        )
                        if not st.session_state.mdqna_retrieved_chunks:
                            st.warning("Không tìm thấy đoạn văn bản phù hợp.")
                    except Exception as e:
                        st.error(f"Lỗi tìm kiếm: {e}")

            if run_rag:
                if not api_key:
                    st.error("Chưa cấu hình API Key trong file .env!")
                else:
                    with st.spinner("Đang tìm ngữ cảnh và sinh câu trả lời..."):
                        st.session_state.mdqna_retrieved_chunks = []
                        context_chunks = search_similar_chunks(query, st.session_state.mdqna_vector_store, top_k=3)
                        if not context_chunks:
                            st.session_state.mdqna_llm_answer = "Không tìm thấy thông tin phù hợp trong các tài liệu đã nạp."
                        else:
                            try:
                                ans = asyncio.run(get_answer_from_llm_with_context(api_key, query, context_chunks))
                                st.session_state.mdqna_llm_answer = ans
                                st.session_state.mdqna_retrieved_chunks = context_chunks
                            except Exception as e:
                                st.error(f"Lỗi AI trả lời: {e}")

        # Hiển thị Kết quả Phản hồi
        if st.session_state.mdqna_llm_answer or st.session_state.mdqna_retrieved_chunks:
            with st.container(border=True):
                st.markdown("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 14px;">3. Kết quả Phản hồi & Nguồn trích dẫn</span>
                    <span class="saas-badge saas-badge-success">Answer & Context</span>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.mdqna_llm_answer:
                    st.markdown(f"""
                    <div style="background: rgba(79, 70, 229, 0.05); border-left: 3px solid #4F46E5; border-radius: 0 8px 8px 0; padding: 12px 14px; margin-bottom: 12px; font-size: 14px; line-height: 1.6;">
                        <b>🤖 Câu trả lời từ AI:</b><br/>
                        {st.session_state.mdqna_llm_answer}
                    </div>
                    """, unsafe_allow_html=True)

                if st.session_state.mdqna_retrieved_chunks:
                    st.markdown("**Các đoạn trích dẫn nguồn liên quan nhất:**")
                    for i, chunk in enumerate(st.session_state.mdqna_retrieved_chunks):
                        src_name = chunk.get("metadata", {}).get("source", "PDF Document")
                        score = chunk.get("score", 0.0)
                        with st.expander(f"Trích dẫn #{i+1} — Nguồn: {src_name} (Độ khớp: {score:.3f})", expanded=(i == 0)):
                            st.markdown(chunk["text"])

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            display_random_meme()
