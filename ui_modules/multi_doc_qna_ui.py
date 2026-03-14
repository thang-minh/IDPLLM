# ui_modules/multi_doc_qna_ui.py
import streamlit as st
import asyncio

# Import các hàm logic
from logic.multi_doc_qna_logic import (
    extract_text_from_uploaded_files,
    get_text_chunks,
    get_embedding_model,
    create_vector_store_from_chunks,
    search_similar_chunks,
    get_answer_from_llm_with_context
)
from ui_utils.fun_meme import display_random_meme
from langchain_huggingface import HuggingFaceEmbeddings  # ← mới, không bị warning nữa
# --- Khởi tạo session state cho module ---
def init_session_state_mdqna():
    if 'mdqna_vector_store' not in st.session_state:
        st.session_state.mdqna_vector_store = None
    if 'mdqna_embedding_model' not in st.session_state:
        st.session_state.mdqna_embedding_model = None
    if 'mdqna_processed_files' not in st.session_state: # Lưu tên các file đã xử lý để tránh lặp lại
        st.session_state.mdqna_processed_files = set()
    if 'mdqna_retrieved_chunks' not in st.session_state:
        st.session_state.mdqna_retrieved_chunks = []
    if 'mdqna_llm_answer' not in st.session_state:
        st.session_state.mdqna_llm_answer = ""


def show_multi_doc_qna_ui(api_key, poppler_path_env=None):
    init_session_state_mdqna()

    st.markdown("<h1 style='text-align: center;'>📚 Hỏi đáp và Tìm kiếm Ngữ nghĩa trên Nhiều Tài liệu</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên một hoặc nhiều file PDF, sau đó đặt câu hỏi hoặc tìm kiếm thông tin trong toàn bộ các tài liệu đó.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- 1. Tải lên và Xử lý Tài liệu ---
    with st.container(border=True):
        st.subheader("📂 Bước 1: Tải lên và Xây dựng Cơ sở Tri thức")
        uploaded_files = st.file_uploader(
            "Tải lên các file PDF của bạn tại đây:",
            type="pdf",
            accept_multiple_files=True,
            key="mdqna_file_uploader",
            help="Bạn có thể chọn nhiều file PDF cùng lúc."
        )

        # Hiển thị nút xử lý chỉ khi có file mới được tải lên chưa được xử lý
        new_files_to_process = []
        if uploaded_files:
            current_file_names = {f.name for f in uploaded_files}
            if not st.session_state.mdqna_processed_files.issuperset(current_file_names) or not st.session_state.mdqna_vector_store:
                new_files_to_process = uploaded_files # Xử lý tất cả nếu có file mới hoặc chưa có vector store

        if new_files_to_process:
            if st.button("⚙️ Xây dựng Cơ sở Tri thức từ Tài liệu", type="primary", use_container_width=True, key="mdqna_process_button"):
                with st.spinner("Đang xử lý tài liệu và tạo index... Việc này có thể mất vài phút tùy số lượng và kích thước file."):
                    try:
                        # 1. Trích xuất văn bản
                        docs_data = extract_text_from_uploaded_files(new_files_to_process, poppler_path_env)
                        if not docs_data:
                            st.warning("Không thể trích xuất văn bản từ các file đã tải lên, hoặc file không có nội dung.")
                            return

                        # 2. Chia chunks
                        text_chunks_with_metadata = get_text_chunks(docs_data)
                        if not text_chunks_with_metadata:
                            st.warning("Không thể chia nhỏ văn bản thành các đoạn (chunks).")
                            return

                        # 3. Tải mô hình embedding (chỉ tải một lần)
                        if st.session_state.mdqna_embedding_model is None:
                            st.session_state.mdqna_embedding_model = get_embedding_model(
                                model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2" # Model tốt cho đa ngôn ngữ
                            )
                        
                        # 4. Tạo vector store
                        st.session_state.mdqna_vector_store = create_vector_store_from_chunks(
                            text_chunks_with_metadata,
                            st.session_state.mdqna_embedding_model
                        )
                        
                        if st.session_state.mdqna_vector_store:
                            st.session_state.mdqna_processed_files.update(current_file_names) # Đánh dấu đã xử lý
                            st.success(f"Đã xử lý {len(new_files_to_process)} tài liệu và xây dựng xong cơ sở tri thức!")
                        else:
                            st.error("Không thể tạo cơ sở tri thức từ các tài liệu.")
                    
                    except ValueError as ve: # Lỗi từ logic của chúng ta
                        st.error(f"Lỗi xử lý: {ve}")
                    except Exception as e:
                        st.error(f"Lỗi không mong muốn trong quá trình xử lý tài liệu: {e}")
        elif uploaded_files and st.session_state.mdqna_vector_store:
            st.info(f"Đã có cơ sở tri thức cho {len(st.session_state.mdqna_processed_files)} tài liệu. Sẵn sàng để hỏi đáp hoặc tìm kiếm.")


    # --- 2. Đặt Câu hỏi / Tìm kiếm ---
    if st.session_state.mdqna_vector_store:
        st.markdown("---")
        with st.container(border=True):
            st.subheader("💬 Bước 2: Đặt Câu hỏi hoặc Tìm kiếm Thông tin")
            query = st.text_input(
                "Nhập câu hỏi hoặc từ khóa tìm kiếm của bạn:",
                key="mdqna_query_input",
                placeholder="Ví dụ: Các điều khoản chính của hợp đồng A là gì? Hoặc tìm 'báo cáo tài chính quý 1'"
            )

            col_search, col_qna = st.columns(2)
            with col_search:
                if st.button("🔍 Tìm kiếm Đoạn văn bản Liên quan", use_container_width=True, key="mdqna_search_button", disabled=not query.strip()):
                    with st.spinner("Đang tìm kiếm các đoạn văn bản tương đồng..."):
                        st.session_state.mdqna_llm_answer = "" # Reset câu trả lời LLM cũ
                        try:
                            st.session_state.mdqna_retrieved_chunks = search_similar_chunks(
                                query,
                                st.session_state.mdqna_vector_store,
                                top_k=5 # Số lượng chunks trả về
                            )
                            if not st.session_state.mdqna_retrieved_chunks:
                                st.warning("Không tìm thấy đoạn văn bản nào phù hợp với truy vấn của bạn.")
                        except Exception as e_search:
                            st.error(f"Lỗi khi tìm kiếm: {e_search}")
                            st.session_state.mdqna_retrieved_chunks = []
            
            with col_qna:
                if st.button("💡 Hỏi AI (Dùng LLM để Trả lời)", type="primary", use_container_width=True, key="mdqna_qna_button", disabled=not query.strip() or not api_key):
                    if not api_key:
                        st.error("API Key chưa được cấu hình. Không thể sử dụng LLM để trả lời.")
                    else:
                        with st.spinner("AI đang suy nghĩ để trả lời câu hỏi của bạn..."):
                            st.session_state.mdqna_retrieved_chunks = [] # Reset chunks hiển thị nếu dùng Q&A
                            # Lấy context từ vector store trước
                            context_chunks_for_llm = search_similar_chunks(query, st.session_state.mdqna_vector_store, top_k=3) # Lấy ít chunk hơn cho LLM context
                            if not context_chunks_for_llm:
                                st.warning("Không tìm thấy ngữ cảnh phù hợp để AI trả lời.")
                                st.session_state.mdqna_llm_answer = "Không có đủ thông tin trong tài liệu để trả lời câu hỏi này."
                            else:
                                try:
                                    st.session_state.mdqna_llm_answer = asyncio.run(
                                        get_answer_from_llm_with_context(api_key, query, context_chunks_for_llm)
                                    )
                                except ValueError as ve: # Lỗi từ logic
                                    st.error(f"Lỗi khi tạo câu trả lời: {ve}")
                                except Exception as e_llm_ans:
                                    st.error(f"Lỗi không mong muốn khi AI trả lời: {e_llm_ans}")
                                    st.session_state.mdqna_llm_answer = "Đã có lỗi xảy ra trong quá trình AI tạo câu trả lời."

        # --- 3. Hiển thị Kết quả ---
        if st.session_state.mdqna_retrieved_chunks or st.session_state.mdqna_llm_answer:
            st.markdown("---")
            with st.container(border=True):
                st.subheader("📝 Kết quả:")
                if st.session_state.mdqna_llm_answer:
                    st.markdown("##### Câu trả lời từ AI:")
                    st.info(st.session_state.mdqna_llm_answer)
                    st.markdown("---") # Phân cách nếu có cả chunks

                if st.session_state.mdqna_retrieved_chunks:
                    st.markdown("##### Các đoạn văn bản liên quan nhất được tìm thấy:")
                    for i, chunk_info in enumerate(st.session_state.mdqna_retrieved_chunks):
                        with st.expander(f"Đoạn {i+1} (Từ: {chunk_info['metadata']['source']}, Độ tương đồng: {chunk_info['score']:.4f})", expanded= i < 2 ): # Mở 2อันดับแรก
                            st.markdown(chunk_info["text"])
            st.markdown("---")
            display_random_meme()

    elif uploaded_files and not st.session_state.mdqna_vector_store:
        st.warning("Vui lòng nhấn nút 'Xây dựng Cơ sở Tri thức từ Tài liệu' trước khi đặt câu hỏi hoặc tìm kiếm.")
    
    elif not uploaded_files:
         st.info("Vui lòng tải lên ít nhất một file PDF để bắt đầu.")