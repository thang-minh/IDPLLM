# logic/multi_doc_qna_logic.py
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS # Langchain có tích hợp sẵn FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings # Để dùng Sentence Transformers
# Hoặc dùng OpenAI embeddings nếu muốn:
# from langchain_openai import OpenAIEmbeddings

# Import các hàm xử lý PDF đã có của bạn
from .common_processing import convert_pdf_to_txt, convert_pdf_to_images, extract_text_from_list_of_images, generate_groq_response

# --- 1. Xử lý tài liệu và trích xuất văn bản ---
def extract_text_from_uploaded_files(uploaded_files, poppler_path_env=None):
    """
    Trích xuất văn bản từ danh sách các file PDF được tải lên.
    Mỗi phần tử trả về là một tuple (tên_file, nội_dung_văn_bản).
    """
    docs_content = []
    for uploaded_file in uploaded_files:
        try:
            file_bytes = uploaded_file.getvalue()
            text = convert_pdf_to_txt(io.BytesIO(file_bytes)) # Thử trích xuất text trực tiếp

            # Nếu text trích xuất trực tiếp ít, có thể thử OCR (khá chậm cho nhiều file)
            if len(text.strip()) < 100: # Ngưỡng tùy chọn để quyết định OCR
                try:
                    images = convert_pdf_to_images(io.BytesIO(file_bytes), poppler_path=poppler_path_env)
                    ocr_text = extract_text_from_list_of_images(images, lang='vie+eng', preprocess=True)
                    text += "\n" + ocr_text # Nối thêm text từ OCR
                except Exception as e_ocr:
                    print(f"Lỗi OCR file {uploaded_file.name}: {e_ocr}")
                    # Nếu OCR lỗi, vẫn giữ lại text đã trích xuất (nếu có)

            if text.strip():
                docs_content.append({"name": uploaded_file.name, "text": text})
        except Exception as e:
            print(f"Lỗi xử lý file {uploaded_file.name}: {e}")
    return docs_content

# --- 2. Chia nhỏ văn bản (Chunking) ---
def get_text_chunks(documents_data):
    """
    Chia văn bản từ nhiều tài liệu thành các chunks nhỏ hơn.
    documents_data: list của dict, mỗi dict có 'name' và 'text'.
    Trả về list các documents của Langchain (mỗi document là một chunk với metadata).
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, # Số ký tự mỗi chunk
        chunk_overlap=200, # Số ký tự gối lên nhau giữa các chunk
        length_function=len
    )
    all_chunks = []
    for doc_data in documents_data:
        chunks = text_splitter.split_text(doc_data["text"])
        for i, chunk_text in enumerate(chunks):
            # Tạo đối tượng Document của Langchain hoặc dict tùy chỉnh
            # Ở đây dùng dict để dễ quản lý và tương thích với nhiều vector store hơn nếu không dùng Langchain's FAISS trực tiếp
            all_chunks.append({
                "text": chunk_text,
                "metadata": {"source": doc_data["name"], "chunk_index": i}
            })
    return all_chunks # List of dictionaries, each dict is a chunk with its text and metadata


# --- 3. Tạo Vector Embeddings và Vector Store ---
def get_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """
    Tải mô hình embedding.
    Bạn có thể đổi model_name sang mô hình hỗ trợ tiếng Việt tốt hơn như:
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    Hoặc "bkai-foundation-models/vietnamese-bi-encoder" (cần xem cách dùng với HuggingFaceEmbeddings)
    """
    # model_kwargs = {'device': 'cpu'} # Hoặc 'cuda' nếu có GPU
    # encode_kwargs = {'normalize_embeddings': False}
    # embeddings = HuggingFaceEmbeddings(
    #     model_name=model_name,
    #     model_kwargs=model_kwargs,
    #     encode_kwargs=encode_kwargs
    # )
    # return embeddings
    # Cách đơn giản hơn, để HuggingFaceEmbeddings tự quản lý device:
    return HuggingFaceEmbeddings(model_name=model_name)

def create_vector_store_from_chunks(text_chunks_with_metadata, embedding_model):
    """
    Tạo vector store (FAISS) từ các chunks và mô hình embedding.
    text_chunks_with_metadata: list các dict, mỗi dict có "text" và "metadata".
    """
    if not text_chunks_with_metadata:
        return None
    
    # Chuẩn bị list of texts và list of metadatas cho FAISS.from_texts
    texts = [chunk["text"] for chunk in text_chunks_with_metadata]
    metadatas = [chunk["metadata"] for chunk in text_chunks_with_metadata]

    try:
        vector_store = FAISS.from_texts(texts=texts, embedding=embedding_model, metadatas=metadatas)
        return vector_store
    except Exception as e:
        print(f"Lỗi khi tạo vector store: {e}")
        raise ValueError(f"Không thể tạo kho vector: {e}")


# --- 4. Tìm kiếm và Trả lời ---
def search_similar_chunks(query_text, vector_store, top_k=5):
    """
    Tìm kiếm các chunks tương đồng nhất với query trong vector store.
    vector_store: đối tượng FAISS đã được tạo.
    """
    if not vector_store:
        return []
    # Embedding của query được thực hiện ngầm bên trong similarity_search
    results_with_scores = vector_store.similarity_search_with_score(query_text, k=top_k)
    # results_with_scores là list của (Document, score)
    # Document của Langchain có page_content và metadata
    
    # Chuyển đổi sang định dạng dict dễ dùng hơn
    formatted_results = []
    for doc, score in results_with_scores:
        formatted_results.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": score # FAISS trả về L2 distance, càng nhỏ càng tốt.
        })
    return formatted_results


async def get_answer_from_llm_with_context(api_key, question, context_chunks, lang="Vietnamese"):
    """
    Sử dụng LLM để trả lời câu hỏi dựa trên ngữ cảnh từ các chunks.
    context_chunks: list các dict, mỗi dict có "text".
    """
    if not api_key:
        raise ValueError("API Key chưa được cấu hình.")
    if not context_chunks:
        return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu để trả lời câu hỏi này."

    context_str = "\n\n".join([chunk["text"] for chunk in context_chunks])
    
    # Giới hạn độ dài context để tránh vượt token limit của LLM
    max_context_len = 15000 # Khoảng 4000-5000 tokens cho Llama3 8K, để dư cho prompt và câu trả lời
    if len(context_str) > max_context_len:
        context_str = context_str[:max_context_len]

    system_message = f"Bạn là một trợ lý AI hữu ích. Chỉ sử dụng thông tin được cung cấp trong phần 'NGỮ CẢNH' dưới đây để trả lời câu hỏi. Nếu câu hỏi không thể được trả lời dựa trên ngữ cảnh, hãy nói rằng bạn không tìm thấy thông tin trong tài liệu. Trả lời bằng tiếng {lang}."
    
    prompt = f"""Dựa vào NGỮ CẢNH sau đây:
------- NGỮ CẢNH -------
{context_str}
------- KẾT THÚC NGỮ CẢNH -------

Hãy trả lời câu hỏi sau: {question}
"""
    try:
        answer = await generate_groq_response(api_key, prompt, system_message=system_message, max_tokens=1024) # Tăng max_tokens cho câu trả lời
        return answer
    except Exception as e:
        print(f"Lỗi khi gọi LLM để tạo câu trả lời: {e}")
        return f"Xin lỗi, đã có lỗi xảy ra khi cố gắng tạo câu trả lời: {e}"