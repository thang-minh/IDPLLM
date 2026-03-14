# import streamlit as st
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_path
# import nltk
# import os
# from dotenv import load_dotenv
# import tempfile
# import cv2
# import numpy as np
# import httpx
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from datetime import datetime

# # === IMPORT MODULES (Giả định các file này tồn tại trong cùng thư mục) ===
# # (Lưu ý: Đảm bảo các module này không tự chạy UI khi import)
# from dark_mode import enable_dark_mode 
# from quotes import get_random_quote
# from form_extractor import parse_text_with_groq # Sẽ cần nếu tích hợp form_extractor
# from sentiment_analyzer import analyze_sentiment # Sẽ cần nếu tích hợp sentiment_analyzer
# from table_extractor import extract_tables_from_pdf, dataframe_to_excel_bytes # Sẽ cần nếu tích hợp table_extractor
# from compare_module import run_compare_module # Sẽ cần nếu tích hợp compare_module
# from pdf_signer import sign_pdf # Sẽ cần nếu tích hợp pdf_signer
# from version_manager import save_version, list_versions, load_version, restore_version # Sẽ cần nếu tích hợp version_manager
# from fun_meme import get_random_meme_path, get_meme_message

# # === PAGE CONFIG (PHẢI LÀ LỆNH STREAMLIT ĐẦU TIÊN) ===
# st.set_page_config(
#     page_title="SmartDoc - Trí tuệ Tài liệu",
#     page_icon="🧠",
#     layout="wide" # "centered" hoặc "wide"
# )

# # === SETUP ===
# load_dotenv()
# # Cập nhật đường dẫn Tesseract nếu cần thiết cho môi trường của bạn
# try:
#     # Ưu tiên biến môi trường nếu được đặt
#     tesseract_path = os.getenv("TESSERACT_CMD")
#     if tesseract_path:
#         pytesseract.pytesseract.tesseract_cmd = tesseract_path
#     else:
#         # Đường dẫn mặc định (điều chỉnh cho phù hợp với hệ thống của bạn)
#         if os.name == 'nt': # Windows
#              pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
#         # Thêm các trường hợp cho Linux/macOS nếu cần
#         # elif os.name == 'posix':
#         #     pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract" 
# except Exception as e:
#     st.warning(f"Lỗi cấu hình Tesseract: {e}. OCR có thể không hoạt động.")

# API_KEY = os.getenv("OPENROUTER_API_KEY") # Được sử dụng bởi Groq
# GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Đảm bảo bạn có biến này trong .env

# # Kiểm tra API keys
# if not API_KEY and not GROQ_API_KEY:
#     st.error("Lỗi: OPENROUTER_API_KEY hoặc GROQ_API_KEY không được tìm thấy. Vui lòng kiểm tra file .env của bạn.")
#     st.stop()

# # Sử dụng GROQ_API_KEY nếu có, nếu không thì dùng OPENROUTER_API_KEY như một fallback (điều chỉnh logic này nếu cần)
# EFFECTIVE_API_KEY = GROQ_API_KEY if GROQ_API_KEY else API_KEY

# nltk.download('punkt', quiet=True)
# nltk.download('wordnet', quiet=True)

# # === DARK MODE & QUOTE ===
# enable_dark_mode()
# quote = get_random_quote()
# st.markdown(f"#### 💡 _{quote}_")
# st.markdown("---")

# # === GROQ API CONFIGURATION ===
# # GROQ_API_KEY đã được lấy từ os.getenv() ở trên
# GROQ_MODEL = "llama3-70b-8192"
# GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# # === UTILITY FUNCTIONS (Giữ nguyên các hàm tiện ích của bạn) ===
# def convert_pdf_to_txt(file_data):
#     try:
#         with fitz.open(stream=file_data, filetype="pdf") as doc:
#             return "".join([page.get_text("text") for page in doc])
#     except Exception as e:
#         st.error(f"Lỗi xử lý PDF: {e}")
#         return ""

# def preprocess_image_for_ocr(img): # Đổi tên để rõ ràng hơn
#     gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
#     # Cân nhắc việc không resize hoặc resize một cách cẩn trọng hơn
#     # gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC) # Tăng kích thước có thể cải thiện OCR
#     gray = cv2.GaussianBlur(gray, (3, 3), 0) # Giảm nhiễu nhẹ
#     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # Threshholding tự động
#     return Image.fromarray(thresh)

# def extract_text_from_image(img):
#     try:
#         processed = preprocess_image_for_ocr(img)
#         return pytesseract.image_to_string(processed, lang='vie+eng')
#     except Exception as e:
#         st.warning(f"Lỗi OCR ảnh: {e}")
#         return ""

# def extract_text_from_images(images):
#     with ThreadPoolExecutor() as executor:
#         return "\n".join(executor.map(extract_text_from_image, images))

# def preprocess_text(text):
#     cleaned = ' '.join(text.split())
#     return nltk.sent_tokenize(cleaned) # Trả về danh sách câu

# def chunk_text(text, max_tokens=4000): # Nên tính theo model (ví dụ Llama3 là 8192)
#     # Tạm thời giữ nguyên logic chunking của bạn, nhưng tokenization thực tế phức tạp hơn
#     words = text.split()
#     chunks, temp, size = [], [], 0
#     for word in words:
#         word_size = len(word.encode('utf-8')) # Ước lượng token đơn giản
#         if size + word_size + 1 > max_tokens:
#             chunks.append(" ".join(temp))
#             temp, size = [word], word_size
#         else:
#             temp.append(word)
#             size += word_size + 1
#     if temp:
#         chunks.append(" ".join(temp))
#     return chunks

# async def generate_response_async(prompt, system_message="You are a helpful assistant.", max_tokens_override=None):
#     if not EFFECTIVE_API_KEY:
#         return "Lỗi: API Key chưa được cấu hình."
#     headers = {
#         "Authorization": f"Bearer {EFFECTIVE_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": GROQ_MODEL,
#         "messages": [
#             {"role": "system", "content": system_message},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.7,
#         "max_tokens": max_tokens_override if max_tokens_override else 1024, # Tăng giới hạn mặc định
#         "top_p": 1,
#         "stream": False
#     }

#     try:
#         async with httpx.AsyncClient(timeout=60.0) as client: # Tăng timeout
#             res = await client.post(GROQ_API_URL, headers=headers, json=data)
#             res.raise_for_status()
#             return res.json()["choices"][0]["message"]["content"].strip()
#     except httpx.HTTPStatusError as e:
#         return f"❌ Lỗi API ({e.response.status_code}): {e.response.text}"
#     except Exception as e:
#         return f"❌ Lỗi không xác định: {e}"

# async def process_document_ai(text_content):
#     # Giới hạn context cho mỗi tác vụ để tránh vượt quá giới hạn token của model
#     # Llama3 có context window lớn, ví dụ 8192 token.
#     # Nên chunk thông minh hơn nếu tài liệu rất lớn.
#     # Tạm thời, sử dụng một phần của văn bản cho mỗi tác vụ.
    
#     # Tính toán số ký tự tương đương với khoảng 7000 tokens (ước lượng thô)
#     # 1 token ~ 4 ký tự tiếng Anh. Tiếng Việt có thể khác.
#     # Tạm lấy một con số an toàn, ví dụ 20000 ký tự cho mỗi yêu cầu.
#     safe_char_limit = 20000 
#     shortened_text = text_content[:safe_char_limit]

#     if not shortened_text.strip():
#         return "Văn bản trống", "Văn bản trống", "Văn bản trống", "Không xác định"

#     # Các prompt có thể cần được điều chỉnh để phù hợp với tiếng Việt và Llama3
#     prompts = {
#         "entities": f"Trích xuất các thực thể quan trọng (tên người, tổ chức, địa điểm, ngày tháng, số tiền, v.v.) từ văn bản sau (trả lời bằng tiếng Việt):\n\n{shortened_text}",
#         "relationships": f"Tìm các mối quan hệ giữa các thực thể trong văn bản sau (trả lời bằng tiếng Việt):\n\n{shortened_text}",
#         "summary": f"Tóm tắt tài liệu sau trong khoảng 3-5 câu (bằng tiếng Việt):\n\n{shortened_text}",
#         "classification": f"Phân loại tài liệu sau vào một trong các loại: Cá nhân, Công việc, Pháp lý, Y tế, Hóa đơn, CV, Khác (trả lời bằng tiếng Việt, chỉ đưa ra tên loại):\n\n{shortened_text}"
#     }
    
#     tasks = [generate_response_async(prompt) for prompt in prompts.values()]
    
#     results = await asyncio.gather(*tasks)
    
#     return results[0], results[1], results[2], results[3]


# # === MAIN STREAMLIT UI ===
# st.markdown("<h1 style='text-align: center; color: #007bff;'>🧠 SmartDoc: Trí tuệ Tài liệu</h1>", unsafe_allow_html=True)
# st.markdown("---")

# # --- File Uploader ---
# uploaded_file = st.file_uploader("\U0001F4C4 Tải lên file PDF của bạn:", type="pdf", help="Tải lên tài liệu PDF để trích xuất và phân tích.")

# if 'full_text' not in st.session_state:
#     st.session_state.full_text = ""
# if 'analysis_results' not in st.session_state:
#     st.session_state.analysis_results = None
# if 'pdf_preview_images' not in st.session_state:
#     st.session_state.pdf_preview_images = []


# if uploaded_file:
#     file_data = uploaded_file.read()
    
#     # Hiển thị preview PDF (có thể giới hạn số trang)
#     st.subheader("📄 Xem trước tài liệu (tối đa 5 trang đầu):")
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
#             tmp_pdf.write(file_data)
#             pdf_path_for_preview = tmp_pdf.name
        
#         # Cấu hình Poppler path (quan trọng cho Windows)
#         poppler_path = None
#         if os.name == 'nt': # Windows
#             poppler_env_path = os.getenv("POPPLER_PATH")
#             if poppler_env_path and os.path.isdir(os.path.join(poppler_env_path, "bin")):
#                  poppler_path = os.path.join(poppler_env_path, "bin")
#             else:
#                 # Thử một đường dẫn phổ biến, nhưng tốt nhất là đặt POPPLER_PATH
#                 default_poppler_path = r"C:\\poppler-24.02.0\\Library\\bin" # Điều chỉnh phiên bản nếu cần
#                 if os.path.isdir(default_poppler_path):
#                     poppler_path = default_poppler_path
#                 else:
#                      st.warning("Không tìm thấy Poppler. Preview ảnh PDF và OCR ảnh có thể không hoạt động. Vui lòng cài đặt Poppler và/hoặc đặt biến môi trường POPPLER_PATH.")
        
#         st.session_state.pdf_preview_images = convert_from_path(pdf_path_for_preview, dpi=150, first_page=1, last_page=5, poppler_path=poppler_path)
        
#         cols = st.columns(min(len(st.session_state.pdf_preview_images), 3)) # Hiển thị tối đa 3 ảnh trên một hàng
#         for i, page_img in enumerate(st.session_state.pdf_preview_images):
#             cols[i % len(cols)].image(page_img, caption=f"Trang {i+1}", use_column_width=True)
        
#         os.unlink(pdf_path_for_preview) # Xóa file tạm

#     except Exception as e:
#         st.warning(f"⚠️ Không thể tạo preview PDF: {e}. Đảm bảo Poppler đã được cài đặt và cấu hình đúng.")
#         st.session_state.pdf_preview_images = []

#     st.markdown("---")

#     # Nút để bắt đầu xử lý
#     if st.button("🚀 Bắt đầu Xử lý Tài liệu", type="primary", help="Nhấn để trích xuất văn bản và phân tích bằng AI"):
#         st.session_state.full_text = ""
#         st.session_state.analysis_results = None

#         with st.spinner("⏳ Đang trích xuất văn bản từ PDF..."):
#             text_from_pdf = convert_pdf_to_txt(file_data)
#             st.session_state.full_text = text_from_pdf

#         if st.session_state.pdf_preview_images: # Chỉ chạy OCR ảnh nếu có preview (tức là Poppler hoạt động)
#             with st.spinner("🧠 Đang chạy OCR trên các trang ảnh (nếu có)..."):
#                 # Sử dụng lại ảnh đã convert cho preview để OCR
#                 text_from_images = extract_text_from_images(st.session_state.pdf_preview_images) # Giới hạn OCR cho các trang preview
#                 if text_from_images.strip():
#                     st.session_state.full_text += "\n\n--- OCR TEXT ---\n" + text_from_images
        
#         if not st.session_state.full_text.strip():
#             st.error("Không thể trích xuất văn bản nào từ tài liệu.")
#         else:
#             with st.spinner("🤖 AI đang phân tích tài liệu... Vui lòng đợi trong giây lát."):
#                 try:
#                     # Giới hạn độ dài văn bản gửi đến AI để tránh lỗi token
#                     max_chars_for_ai = 60000 # Điều chỉnh nếu cần
#                     text_for_ai = st.session_state.full_text[:max_chars_for_ai]

#                     entities, relationships, summary, classification = asyncio.run(process_document_ai(text_for_ai))
#                     st.session_state.analysis_results = {
#                         "entities": entities,
#                         "relationships": relationships,
#                         "summary": summary,
#                         "classification": classification
#                     }
#                     st.success("🎉 Phân tích tài liệu hoàn tất!")
#                 except Exception as e:
#                     st.error(f"Lỗi trong quá trình phân tích AI: {e}")
#                     st.session_state.analysis_results = None
#         st.markdown("---")


#     # --- Hiển thị kết quả nếu đã xử lý ---
#     if st.session_state.full_text:
#         st.header("📊 Kết quả Xử lý")
        
#         tab1, tab2, tab3, tab4 = st.tabs(["📜 Văn bản Trích xuất", "🔍 Phân tích AI", "💬 Chat với Tài liệu", "🌐 Dịch Thuật"])

#         with tab1:
#             st.subheader("Văn bản đầy đủ đã trích xuất (PDF + OCR nếu có):")
#             st.text_area("Nội dung", st.session_state.full_text, height=400, key="full_text_display")
            
#             st.subheader("Văn bản sau tiền xử lý (theo câu):")
#             preprocessed_sentences = preprocess_text(st.session_state.full_text)
#             st.text_area("Các câu đã làm sạch", "\n".join(preprocessed_sentences), height=200, key="cleaned_text_display")

#         with tab2:
#             if st.session_state.analysis_results:
#                 st.subheader("📝 Tóm tắt tài liệu:")
#                 st.markdown(st.session_state.analysis_results["summary"])

#                 st.subheader("📌 Thực thể được trích xuất:")
#                 st.text_area("Entities", st.session_state.analysis_results["entities"], height=150, key="entities_display")

#                 st.subheader("🔗 Mối quan hệ giữa các thực thể:")
#                 st.text_area("Relationships", st.session_state.analysis_results["relationships"], height=150, key="relationships_display")
                
#                 st.subheader("🏷️ Phân loại tài liệu:")
#                 st.info(f"**Loại tài liệu:** {st.session_state.analysis_results['classification']}")
#             else:
#                 st.info("Chưa có kết quả phân tích AI. Nhấn nút 'Bắt đầu Xử lý Tài liệu'.")

#         with tab3:
#             st.subheader("Đặt câu hỏi về nội dung tài liệu:")
#             user_question = st.text_input("Câu hỏi của bạn:", key="chat_question")
#             if user_question:
#                 if st.button("💬 Gửi câu hỏi", key="ask_button"):
#                     with st.spinner("🤖 AI đang tìm câu trả lời..."):
#                         # Giới hạn context cho câu hỏi để tránh quá dài
#                         context_for_qa = st.session_state.full_text[:25000] # Khoảng 6k tokens
#                         prompt = f"Dựa vào nội dung tài liệu sau đây, hãy trả lời câu hỏi. Nếu không tìm thấy thông tin, hãy nói rằng bạn không tìm thấy. Trả lời bằng tiếng Việt.\n\n--- TÀI LIỆU ---\n{context_for_qa}\n\n--- CÂU HỎI ---\n{user_question}"
#                         answer = asyncio.run(generate_response_async(prompt, system_message="Bạn là một trợ lý AI hữu ích chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp.", max_tokens_override=500))
#                         st.markdown(answer)
        
#         with tab4:
#             st.subheader("Dịch một phần văn bản:")
#             text_to_translate_sample = st.session_state.full_text[:2000] # Giới hạn mẫu văn bản
#             st.info(f"Lưu ý: Chỉ dịch một đoạn ngắn của văn bản (khoảng {len(text_to_translate_sample)} ký tự đầu tiên).")
            
#             target_lang = st.selectbox(
#                 "Chọn ngôn ngữ muốn dịch:", 
#                 ["English", "Vietnamese", "Spanish", "French", "German", "Japanese", "Chinese", "Korean"], 
#                 key="target_language"
#             )
#             if st.button("🌍 Dịch ngay", key="translate_button"):
#                 with st.spinner(f"Đang dịch sang {target_lang}..."):
#                     # Prompt cần rõ ràng về việc dịch
#                     translation_prompt = f"Dịch đoạn văn bản sau sang {target_lang}. Chỉ trả về nội dung đã dịch, không thêm bất kỳ lời giải thích nào:\n\n{text_to_translate_sample}"
#                     translation_result = asyncio.run(generate_response_async(translation_prompt, system_message="Bạn là một chuyên gia dịch thuật đa ngôn ngữ.", max_tokens_override=1000)) # Tăng token cho bản dịch
#                     st.text_area(f"Bản dịch sang {target_lang}:", translation_result, height=200, key="translation_output")
#                     st.download_button(
#                         f"📥 Tải bản dịch ({target_lang})", 
#                         translation_result, 
#                         file_name=f"translation_{target_lang}.txt"
#                     )

#         st.markdown("---")
#         st.header("\U0001F4E5 Tải xuống Kết quả")
#         col_dl1, col_dl2, col_dl3 = st.columns(3)

#         with col_dl1:
#             if st.session_state.analysis_results and st.session_state.analysis_results.get("summary"):
#                 st.download_button(
#                     label="📥 Tải Tóm tắt (.txt)",
#                     data=st.session_state.analysis_results["summary"],
#                     file_name="summary.txt",
#                     mime="text/plain"
#                 )
        
#         with col_dl2:
#             if st.session_state.analysis_results and st.session_state.analysis_results.get("entities"):
#                 extracted_info = f"THỰC THỂ:\n{st.session_state.analysis_results['entities']}\n\nMỐI QUAN HỆ:\n{st.session_state.analysis_results.get('relationships', '')}"
#                 st.download_button(
#                     label="📥 Tải Thông tin Trích xuất (.txt)",
#                     data=extracted_info,
#                     file_name="extracted_info.txt",
#                     mime="text/plain"
#                 )

#         with col_dl3:
#             st.download_button(
#                 label="📥 Tải Văn bản Đầy đủ (.txt)",
#                 data=st.session_state.full_text,
#                 file_name="full_text.txt",
#                 mime="text/plain"
#             )
        
#         st.markdown("---")
#         # --- Fun Meme ---
#         st.success(get_meme_message()) # Hiển thị thông báo vui vẻ
#         meme_path = get_random_meme_path()
#         if meme_path:
#             try:
#                 meme_image = Image.open(meme_path)
#                 st.image(meme_image, caption="Một chút thư giãn cuối cùng!", width=300)
#             except Exception as e:
#                 st.warning(f"Không thể tải meme: {e}")


# === CÁC MODULE UI KHÁC (ĐÃ BÌNH LUẬN) ===
# Nếu bạn muốn tích hợp chúng, hãy xem xét sử dụng st.sidebar để tạo điều hướng 
# và gọi các hàm UI tương ứng dựa trên lựa chọn của người dùng.

# --- Form Extractor UI (Ví dụ: CMND / Hóa đơn / Đơn xin việc) ---
# def run_form_extractor_ui():
# st.title("📄 Trích xuất thông tin từ CMND / Hóa đơn / Đơn xin việc")
#     # ... (code UI của bạn cho form extractor) ...

# --- Sentiment Analysis UI ---
# def run_sentiment_analysis_ui():
# st.title("🤖 Nhận diện cảm xúc văn bản với Groq API")
#     # ... (code UI của bạn cho sentiment analysis) ...

# --- Table Extractor UI ---
# def run_table_extractor_ui():
# st.title("📄 Trích xuất bảng từ PDF")
#     # ... (code UI của bạn cho table extractor) ...

# --- Document Comparison UI ---
# def run_document_comparison_ui():
#     # Giả sử run_compare_module() là hàm vẽ UI của bạn
#     # from compare_module import run_compare_module 
#     # run_compare_module()
#     pass

# --- PDF Signer UI ---
# def run_pdf_signer_ui():
# st.title("✍️ Ký và đóng dấu số PDF")
#     # ... (code UI của bạn cho PDF signer) ...

# --- Version Manager UI ---
# def run_version_manager_ui():
# st.title("🗂️ Quản lý Phiên bản Tài liệu")
# # Ví dụ khi người dùng upload
# uploaded_file_vm = st.file_uploader("Tải file PDF cho Version Manager", key="vm_uploader")
# if uploaded_file_vm:
# file_data_vm = uploaded_file_vm.read()
# # Giả sử đã xử lý phân tích document rồi
# analysis_results_vm = {"summary": "Tóm tắt...", "entities": "...", "classification": "Personal"}
# metadata_vm = {"user": "user123", "upload_time": str(datetime.now())}

# # Lưu phiên bản mới
# doc_id_vm = uploaded_file_vm.name # Sử dụng tên file làm ID (cần cẩn thận nếu tên trùng)
# try:
# version_dir = save_version(doc_id_vm, file_data_vm, metadata_vm, analysis_results_vm)
# st.success(f"Lưu phiên bản mới tại: {version_dir}")
# except Exception as e:
# st.error(f"Lỗi lưu phiên bản: {e}")

# # Hiển thị các phiên bản đã lưu
# try:
# versions = list_versions(doc_id_vm)
# if versions:
# selected_version = st.selectbox("Chọn phiên bản để xem", versions, key="vm_version_select")
# if selected_version:
# data = load_version(doc_id_vm, selected_version)
# st.write("Metadata:", data["metadata"])
# st.write("Phân tích:", data["analysis"])
#                                 with open(data["pdf_path"], "rb") as fp:
#                                     st.download_button("Tải PDF phiên bản này", fp, file_name=f"{selected_version}.pdf")
# # Phục hồi phiên bản cũ
# if st.button("Phục hồi phiên bản được chọn", key="vm_restore"):
# restore_target_path = f"./restored_{selected_version}.pdf"
# restore_version(doc_id_vm, selected_version, restore_target_path)
# st.success(f"Phục hồi thành công! File lưu tại {restore_target_path}")
# else:
# st.info("Chưa có phiên bản nào cho tài liệu này.")
# except Exception as e:
# st.error(f"Lỗi hiển thị phiên bản: {e}")


# === Cấu trúc điều hướng (ví dụ nếu muốn kết hợp nhiều module) ===
# st.sidebar.title("🛠️ Công cụ")
# app_mode = st.sidebar.selectbox(
# "Chọn chức năng:",
#     ["Trí tuệ Tài liệu", "Trích xuất Form", "Phân tích Cảm xúc", "Trích xuất Bảng", "So sánh Tài liệu", "Ký PDF", "Quản lý Phiên bản"]
# )

# if app_mode == "Trí tuệ Tài liệu":
# # Phần UI chính ở trên sẽ chạy ở đây
#     pass 
# elif app_mode == "Trích xuất Form":
# run_form_extractor_ui()
# elif app_mode == "Phân tích Cảm xúc":
# run_sentiment_analysis_ui()
# elif app_mode == "Trích xuất Bảng":
# run_table_extractor_ui()
# elif app_mode == "So sánh Tài liệu":
# run_document_comparison_ui()
# elif app_mode == "Ký PDF":
# run_pdf_signer_ui()
# elif app_mode == "Quản lý Phiên bản":
# run_version_manager_ui()


# # import streamlit as st
# # import fitz  # PyMuPDF
# # import pytesseract
# # from PIL import Image
# # from pdf2image import convert_from_path
# # import nltk
# # import os
# # from dotenv import load_dotenv
# # import tempfile
# # import cv2
# # import numpy as np
# # import httpx
# # import asyncio
# # from concurrent.futures import ThreadPoolExecutor
# # from datetime import datetime

# # # === IMPORT MODULES (Giả định các file này tồn tại trong cùng thư mục) ===
# # # (Lưu ý: Đảm bảo các module này không tự chạy UI khi import)
# # from dark_mode import enable_dark_mode 
# # from quotes import get_random_quote
# # from form_extractor import parse_text_with_groq # Sẽ cần nếu tích hợp form_extractor
# # from sentiment_analyzer import analyze_sentiment # Sẽ cần nếu tích hợp sentiment_analyzer
# # from table_extractor import extract_tables_from_pdf, dataframe_to_excel_bytes # Sẽ cần nếu tích hợp table_extractor
# # from compare_module import run_compare_module # Sẽ cần nếu tích hợp compare_module
# # from pdf_signer import sign_pdf # Sẽ cần nếu tích hợp pdf_signer
# # from version_manager import save_version, list_versions, load_version, restore_version # Sẽ cần nếu tích hợp version_manager
# # from fun_meme import get_random_meme_path, get_meme_message

# # # === PAGE CONFIG (PHẢI LÀ LỆNH STREAMLIT ĐẦU TIÊN) ===
# # st.set_page_config(
# #     page_title="SmartDoc - Trí tuệ Tài liệu",
# #     page_icon="🧠",
# #     layout="wide" # "centered" hoặc "wide"
# # )

# # # === SETUP ===
# # load_dotenv()
# # # Cập nhật đường dẫn Tesseract nếu cần thiết cho môi trường của bạn
# # try:
# #     # Ưu tiên biến môi trường nếu được đặt
# #     tesseract_path = os.getenv("TESSERACT_CMD")
# #     if tesseract_path:
# #         pytesseract.pytesseract.tesseract_cmd = tesseract_path
# #     else:
# #         # Đường dẫn mặc định (điều chỉnh cho phù hợp với hệ thống của bạn)
# #         if os.name == 'nt': # Windows
# #              pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# #         # Thêm các trường hợp cho Linux/macOS nếu cần
# #         # elif os.name == 'posix':
# #         #     pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract" 
# # except Exception as e:
# #     st.warning(f"Lỗi cấu hình Tesseract: {e}. OCR có thể không hoạt động.")

# # API_KEY = os.getenv("OPENROUTER_API_KEY") # Được sử dụng bởi Groq
# # GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Đảm bảo bạn có biến này trong .env

# # # Kiểm tra API keys
# # if not API_KEY and not GROQ_API_KEY:
# #     st.error("Lỗi: OPENROUTER_API_KEY hoặc GROQ_API_KEY không được tìm thấy. Vui lòng kiểm tra file .env của bạn.")
# #     st.stop()

# # # Sử dụng GROQ_API_KEY nếu có, nếu không thì dùng OPENROUTER_API_KEY như một fallback (điều chỉnh logic này nếu cần)
# # EFFECTIVE_API_KEY = GROQ_API_KEY if GROQ_API_KEY else API_KEY

# # nltk.download('punkt', quiet=True)
# # nltk.download('wordnet', quiet=True)

# # # === DARK MODE & QUOTE ===
# # enable_dark_mode()
# # quote = get_random_quote()
# # st.markdown(f"#### 💡 _{quote}_")
# # st.markdown("---")

# # # === GROQ API CONFIGURATION ===
# # # GROQ_API_KEY đã được lấy từ os.getenv() ở trên
# # GROQ_MODEL = "llama3-70b-8192"
# # GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# # # === UTILITY FUNCTIONS (Giữ nguyên các hàm tiện ích của bạn) ===
# # def convert_pdf_to_txt(file_data):
# #     try:
# #         with fitz.open(stream=file_data, filetype="pdf") as doc:
# #             return "".join([page.get_text("text") for page in doc])
# #     except Exception as e:
# #         st.error(f"Lỗi xử lý PDF: {e}")
# #         return ""

# # def preprocess_image_for_ocr(img): # Đổi tên để rõ ràng hơn
# #     gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
# #     # Cân nhắc việc không resize hoặc resize một cách cẩn trọng hơn
# #     # gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC) # Tăng kích thước có thể cải thiện OCR
# #     gray = cv2.GaussianBlur(gray, (3, 3), 0) # Giảm nhiễu nhẹ
# #     _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) # Threshholding tự động
# #     return Image.fromarray(thresh)

# # def extract_text_from_image(img):
# #     try:
# #         processed = preprocess_image_for_ocr(img)
# #         return pytesseract.image_to_string(processed, lang='vie+eng')
# #     except Exception as e:
# #         st.warning(f"Lỗi OCR ảnh: {e}")
# #         return ""

# # def extract_text_from_images(images):
# #     with ThreadPoolExecutor() as executor:
# #         return "\n".join(executor.map(extract_text_from_image, images))

# # def preprocess_text(text):
# #     cleaned = ' '.join(text.split())
# #     return nltk.sent_tokenize(cleaned) # Trả về danh sách câu

# # def chunk_text(text, max_tokens=4000): # Nên tính theo model (ví dụ Llama3 là 8192)
# #     # Tạm thời giữ nguyên logic chunking của bạn, nhưng tokenization thực tế phức tạp hơn
# #     words = text.split()
# #     chunks, temp, size = [], [], 0
# #     for word in words:
# #         word_size = len(word.encode('utf-8')) # Ước lượng token đơn giản
# #         if size + word_size + 1 > max_tokens:
# #             chunks.append(" ".join(temp))
# #             temp, size = [word], word_size
# #         else:
# #             temp.append(word)
# #             size += word_size + 1
# #     if temp:
# #         chunks.append(" ".join(temp))
# #     return chunks

# # async def generate_response_async(prompt, system_message="You are a helpful assistant.", max_tokens_override=None):
# #     if not EFFECTIVE_API_KEY:
# #         return "Lỗi: API Key chưa được cấu hình."
# #     headers = {
# #         "Authorization": f"Bearer {EFFECTIVE_API_KEY}",
# #         "Content-Type": "application/json"
# #     }
# #     data = {
# #         "model": GROQ_MODEL,
# #         "messages": [
# #             {"role": "system", "content": system_message},
# #             {"role": "user", "content": prompt}
# #         ],
# #         "temperature": 0.7,
# #         "max_tokens": max_tokens_override if max_tokens_override else 1024, # Tăng giới hạn mặc định
# #         "top_p": 1,
# #         "stream": False
# #     }

# #     try:
# #         async with httpx.AsyncClient(timeout=60.0) as client: # Tăng timeout
# #             res = await client.post(GROQ_API_URL, headers=headers, json=data)
# #             res.raise_for_status()
# #             return res.json()["choices"][0]["message"]["content"].strip()
# #     except httpx.HTTPStatusError as e:
# #         return f"❌ Lỗi API ({e.response.status_code}): {e.response.text}"
# #     except Exception as e:
# #         return f"❌ Lỗi không xác định: {e}"

# # async def process_document_ai(text_content):
# #     # Giới hạn context cho mỗi tác vụ để tránh vượt quá giới hạn token của model
# #     # Llama3 có context window lớn, ví dụ 8192 token.
# #     # Nên chunk thông minh hơn nếu tài liệu rất lớn.
# #     # Tạm thời, sử dụng một phần của văn bản cho mỗi tác vụ.
    
# #     # Tính toán số ký tự tương đương với khoảng 7000 tokens (ước lượng thô)
# #     # 1 token ~ 4 ký tự tiếng Anh. Tiếng Việt có thể khác.
# #     # Tạm lấy một con số an toàn, ví dụ 20000 ký tự cho mỗi yêu cầu.
# #     safe_char_limit = 20000 
# #     shortened_text = text_content[:safe_char_limit]

# #     if not shortened_text.strip():
# #         return "Văn bản trống", "Văn bản trống", "Văn bản trống", "Không xác định"

# #     # Các prompt có thể cần được điều chỉnh để phù hợp với tiếng Việt và Llama3
# #     prompts = {
# #         "entities": f"Trích xuất các thực thể quan trọng (tên người, tổ chức, địa điểm, ngày tháng, số tiền, v.v.) từ văn bản sau (trả lời bằng tiếng Việt):\n\n{shortened_text}",
# #         "relationships": f"Tìm các mối quan hệ giữa các thực thể trong văn bản sau (trả lời bằng tiếng Việt):\n\n{shortened_text}",
# #         "summary": f"Tóm tắt tài liệu sau trong khoảng 3-5 câu (bằng tiếng Việt):\n\n{shortened_text}",
# #         "classification": f"Phân loại tài liệu sau vào một trong các loại: Cá nhân, Công việc, Pháp lý, Y tế, Hóa đơn, CV, Khác (trả lời bằng tiếng Việt, chỉ đưa ra tên loại):\n\n{shortened_text}"
# #     }
    
# #     tasks = [generate_response_async(prompt) for prompt in prompts.values()]
    
# #     results = await asyncio.gather(*tasks)
    
# #     return results[0], results[1], results[2], results[3]


# # # === MAIN STREAMLIT UI ===
# # st.markdown("<h1 style='text-align: center; color: #007bff;'>🧠 SmartDoc: Trí tuệ Tài liệu</h1>", unsafe_allow_html=True)
# # st.markdown("---")

# # # --- File Uploader ---
# # uploaded_file = st.file_uploader("\U0001F4C4 Tải lên file PDF của bạn:", type="pdf", help="Tải lên tài liệu PDF để trích xuất và phân tích.")

# # if 'full_text' not in st.session_state:
# #     st.session_state.full_text = ""
# # if 'analysis_results' not in st.session_state:
# #     st.session_state.analysis_results = None
# # if 'pdf_preview_images' not in st.session_state:
# #     st.session_state.pdf_preview_images = []


# # if uploaded_file:
# #     file_data = uploaded_file.read()
    
# #     # Hiển thị preview PDF (có thể giới hạn số trang)
# #     st.subheader("📄 Xem trước tài liệu (tối đa 5 trang đầu):")
# #     try:
# #         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
# #             tmp_pdf.write(file_data)
# #             pdf_path_for_preview = tmp_pdf.name
        
# #         # Cấu hình Poppler path (quan trọng cho Windows)
# #         poppler_path = None
# #         if os.name == 'nt': # Windows
# #             poppler_env_path = os.getenv("POPPLER_PATH")
# #             if poppler_env_path and os.path.isdir(os.path.join(poppler_env_path, "bin")):
# #                  poppler_path = os.path.join(poppler_env_path, "bin")
# #             else:
# #                 # Thử một đường dẫn phổ biến, nhưng tốt nhất là đặt POPPLER_PATH
# #                 default_poppler_path = r"C:\\poppler-24.02.0\\Library\\bin" # Điều chỉnh phiên bản nếu cần
# #                 if os.path.isdir(default_poppler_path):
# #                     poppler_path = default_poppler_path
# #                 else:
# #                      st.warning("Không tìm thấy Poppler. Preview ảnh PDF và OCR ảnh có thể không hoạt động. Vui lòng cài đặt Poppler và/hoặc đặt biến môi trường POPPLER_PATH.")
        
# #         st.session_state.pdf_preview_images = convert_from_path(pdf_path_for_preview, dpi=150, first_page=1, last_page=5, poppler_path=poppler_path)
        
# #         cols = st.columns(min(len(st.session_state.pdf_preview_images), 3)) # Hiển thị tối đa 3 ảnh trên một hàng
# #         for i, page_img in enumerate(st.session_state.pdf_preview_images):
# #             cols[i % len(cols)].image(page_img, caption=f"Trang {i+1}", use_column_width=True)
        
# #         os.unlink(pdf_path_for_preview) # Xóa file tạm

# #     except Exception as e:
# #         st.warning(f"⚠️ Không thể tạo preview PDF: {e}. Đảm bảo Poppler đã được cài đặt và cấu hình đúng.")
# #         st.session_state.pdf_preview_images = []

# #     st.markdown("---")

# #     # Nút để bắt đầu xử lý
# #     if st.button("🚀 Bắt đầu Xử lý Tài liệu", type="primary", help="Nhấn để trích xuất văn bản và phân tích bằng AI"):
# #         st.session_state.full_text = ""
# #         st.session_state.analysis_results = None

# #         with st.spinner("⏳ Đang trích xuất văn bản từ PDF..."):
# #             text_from_pdf = convert_pdf_to_txt(file_data)
# #             st.session_state.full_text = text_from_pdf

# #         if st.session_state.pdf_preview_images: # Chỉ chạy OCR ảnh nếu có preview (tức là Poppler hoạt động)
# #             with st.spinner("🧠 Đang chạy OCR trên các trang ảnh (nếu có)..."):
# #                 # Sử dụng lại ảnh đã convert cho preview để OCR
# #                 text_from_images = extract_text_from_images(st.session_state.pdf_preview_images) # Giới hạn OCR cho các trang preview
# #                 if text_from_images.strip():
# #                     st.session_state.full_text += "\n\n--- OCR TEXT ---\n" + text_from_images
        
# #         if not st.session_state.full_text.strip():
# #             st.error("Không thể trích xuất văn bản nào từ tài liệu.")
# #         else:
# #             with st.spinner("🤖 AI đang phân tích tài liệu... Vui lòng đợi trong giây lát."):
# #                 try:
# #                     # Giới hạn độ dài văn bản gửi đến AI để tránh lỗi token
# #                     max_chars_for_ai = 60000 # Điều chỉnh nếu cần
# #                     text_for_ai = st.session_state.full_text[:max_chars_for_ai]

# #                     entities, relationships, summary, classification = asyncio.run(process_document_ai(text_for_ai))
# #                     st.session_state.analysis_results = {
# #                         "entities": entities,
# #                         "relationships": relationships,
# #                         "summary": summary,
# #                         "classification": classification
# #                     }
# #                     st.success("🎉 Phân tích tài liệu hoàn tất!")
# #                 except Exception as e:
# #                     st.error(f"Lỗi trong quá trình phân tích AI: {e}")
# #                     st.session_state.analysis_results = None
# #         st.markdown("---")


# #     # --- Hiển thị kết quả nếu đã xử lý ---
# #     if st.session_state.full_text:
# #         st.header("📊 Kết quả Xử lý")
        
# #         tab1, tab2, tab3, tab4 = st.tabs(["📜 Văn bản Trích xuất", "🔍 Phân tích AI", "💬 Chat với Tài liệu", "🌐 Dịch Thuật"])

# #         with tab1:
# #             st.subheader("Văn bản đầy đủ đã trích xuất (PDF + OCR nếu có):")
# #             st.text_area("Nội dung", st.session_state.full_text, height=400, key="full_text_display")
            
# #             st.subheader("Văn bản sau tiền xử lý (theo câu):")
# #             preprocessed_sentences = preprocess_text(st.session_state.full_text)
# #             st.text_area("Các câu đã làm sạch", "\n".join(preprocessed_sentences), height=200, key="cleaned_text_display")

# #         with tab2:
# #             if st.session_state.analysis_results:
# #                 st.subheader("📝 Tóm tắt tài liệu:")
# #                 st.markdown(st.session_state.analysis_results["summary"])

# #                 st.subheader("📌 Thực thể được trích xuất:")
# #                 st.text_area("Entities", st.session_state.analysis_results["entities"], height=150, key="entities_display")

# #                 st.subheader("🔗 Mối quan hệ giữa các thực thể:")
# #                 st.text_area("Relationships", st.session_state.analysis_results["relationships"], height=150, key="relationships_display")
                
# #                 st.subheader("🏷️ Phân loại tài liệu:")
# #                 st.info(f"**Loại tài liệu:** {st.session_state.analysis_results['classification']}")
# #             else:
# #                 st.info("Chưa có kết quả phân tích AI. Nhấn nút 'Bắt đầu Xử lý Tài liệu'.")

# #         with tab3:
# #             st.subheader("Đặt câu hỏi về nội dung tài liệu:")
# #             user_question = st.text_input("Câu hỏi của bạn:", key="chat_question")
# #             if user_question:
# #                 if st.button("💬 Gửi câu hỏi", key="ask_button"):
# #                     with st.spinner("🤖 AI đang tìm câu trả lời..."):
# #                         # Giới hạn context cho câu hỏi để tránh quá dài
# #                         context_for_qa = st.session_state.full_text[:25000] # Khoảng 6k tokens
# #                         prompt = f"Dựa vào nội dung tài liệu sau đây, hãy trả lời câu hỏi. Nếu không tìm thấy thông tin, hãy nói rằng bạn không tìm thấy. Trả lời bằng tiếng Việt.\n\n--- TÀI LIỆU ---\n{context_for_qa}\n\n--- CÂU HỎI ---\n{user_question}"
# #                         answer = asyncio.run(generate_response_async(prompt, system_message="Bạn là một trợ lý AI hữu ích chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp.", max_tokens_override=500))
# #                         st.markdown(answer)
        
# #         with tab4:
# #             st.subheader("Dịch một phần văn bản:")
# #             text_to_translate_sample = st.session_state.full_text[:2000] # Giới hạn mẫu văn bản
# #             st.info(f"Lưu ý: Chỉ dịch một đoạn ngắn của văn bản (khoảng {len(text_to_translate_sample)} ký tự đầu tiên).")
            
# #             target_lang = st.selectbox(
# #                 "Chọn ngôn ngữ muốn dịch:", 
# #                 ["English", "Vietnamese", "Spanish", "French", "German", "Japanese", "Chinese", "Korean"], 
# #                 key="target_language"
# #             )
# #             if st.button("🌍 Dịch ngay", key="translate_button"):
# #                 with st.spinner(f"Đang dịch sang {target_lang}..."):
# #                     # Prompt cần rõ ràng về việc dịch
# #                     translation_prompt = f"Dịch đoạn văn bản sau sang {target_lang}. Chỉ trả về nội dung đã dịch, không thêm bất kỳ lời giải thích nào:\n\n{text_to_translate_sample}"
# #                     translation_result = asyncio.run(generate_response_async(translation_prompt, system_message="Bạn là một chuyên gia dịch thuật đa ngôn ngữ.", max_tokens_override=1000)) # Tăng token cho bản dịch
# #                     st.text_area(f"Bản dịch sang {target_lang}:", translation_result, height=200, key="translation_output")
# #                     st.download_button(
# #                         f"📥 Tải bản dịch ({target_lang})", 
# #                         translation_result, 
# #                         file_name=f"translation_{target_lang}.txt"
# #                     )

# #         st.markdown("---")
# #         st.header("\U0001F4E5 Tải xuống Kết quả")
# #         col_dl1, col_dl2, col_dl3 = st.columns(3)

# #         with col_dl1:
# #             if st.session_state.analysis_results and st.session_state.analysis_results.get("summary"):
# #                 st.download_button(
# #                     label="📥 Tải Tóm tắt (.txt)",
# #                     data=st.session_state.analysis_results["summary"],
# #                     file_name="summary.txt",
# #                     mime="text/plain"
# #                 )
        
# #         with col_dl2:
# #             if st.session_state.analysis_results and st.session_state.analysis_results.get("entities"):
# #                 extracted_info = f"THỰC THỂ:\n{st.session_state.analysis_results['entities']}\n\nMỐI QUAN HỆ:\n{st.session_state.analysis_results.get('relationships', '')}"
# #                 st.download_button(
# #                     label="📥 Tải Thông tin Trích xuất (.txt)",
# #                     data=extracted_info,
# #                     file_name="extracted_info.txt",
# #                     mime="text/plain"
# #                 )

# #         with col_dl3:
# #             st.download_button(
# #                 label="📥 Tải Văn bản Đầy đủ (.txt)",
# #                 data=st.session_state.full_text,
# #                 file_name="full_text.txt",
# #                 mime="text/plain"
# #             )
        
# #         st.markdown("---")
# #         # --- Fun Meme ---
# #         st.success(get_meme_message()) # Hiển thị thông báo vui vẻ
# #         meme_path = get_random_meme_path()
# #         if meme_path:
# #             try:
# #                 meme_image = Image.open(meme_path)
# #                 st.image(meme_image, caption="Một chút thư giãn cuối cùng!", width=300)
# #             except Exception as e:
# #                 st.warning(f"Không thể tải meme: {e}")


# # # === CÁC MODULE UI KHÁC (ĐÃ BÌNH LUẬN) ===
# # # Nếu bạn muốn tích hợp chúng, hãy xem xét sử dụng st.sidebar để tạo điều hướng 
# # # và gọi các hàm UI tương ứng dựa trên lựa chọn của người dùng.

# # # --- Form Extractor UI (Ví dụ: CMND / Hóa đơn / Đơn xin việc) ---
# # # def run_form_extractor_ui():
# # # st.title("📄 Trích xuất thông tin từ CMND / Hóa đơn / Đơn xin việc")
# # #     # ... (code UI của bạn cho form extractor) ...

# # # --- Sentiment Analysis UI ---
# # # def run_sentiment_analysis_ui():
# # # st.title("🤖 Nhận diện cảm xúc văn bản với Groq API")
# # #     # ... (code UI của bạn cho sentiment analysis) ...

# # # --- Table Extractor UI ---
# # # def run_table_extractor_ui():
# # # st.title("📄 Trích xuất bảng từ PDF")
# # #     # ... (code UI của bạn cho table extractor) ...

# # # --- Document Comparison UI ---
# # # def run_document_comparison_ui():
# # #     # Giả sử run_compare_module() là hàm vẽ UI của bạn
# # #     # from compare_module import run_compare_module 
# # #     # run_compare_module()
# # #     pass

# # # --- PDF Signer UI ---
# # # def run_pdf_signer_ui():
# # # st.title("✍️ Ký và đóng dấu số PDF")
# # #     # ... (code UI của bạn cho PDF signer) ...

# # # --- Version Manager UI ---
# # # def run_version_manager_ui():
# # # st.title("🗂️ Quản lý Phiên bản Tài liệu")
# # # # Ví dụ khi người dùng upload
# # # uploaded_file_vm = st.file_uploader("Tải file PDF cho Version Manager", key="vm_uploader")
# # # if uploaded_file_vm:
# # # file_data_vm = uploaded_file_vm.read()
# # # # Giả sử đã xử lý phân tích document rồi
# # # analysis_results_vm = {"summary": "Tóm tắt...", "entities": "...", "classification": "Personal"}
# # # metadata_vm = {"user": "user123", "upload_time": str(datetime.now())}

# # # # Lưu phiên bản mới
# # # doc_id_vm = uploaded_file_vm.name # Sử dụng tên file làm ID (cần cẩn thận nếu tên trùng)
# # # try:
# # # version_dir = save_version(doc_id_vm, file_data_vm, metadata_vm, analysis_results_vm)
# # # st.success(f"Lưu phiên bản mới tại: {version_dir}")
# # # except Exception as e:
# # # st.error(f"Lỗi lưu phiên bản: {e}")

# # # # Hiển thị các phiên bản đã lưu
# # # try:
# # # versions = list_versions(doc_id_vm)
# # # if versions:
# # # selected_version = st.selectbox("Chọn phiên bản để xem", versions, key="vm_version_select")
# # # if selected_version:
# # # data = load_version(doc_id_vm, selected_version)
# # # st.write("Metadata:", data["metadata"])
# # # st.write("Phân tích:", data["analysis"])
# # #                                 with open(data["pdf_path"], "rb") as fp:
# # #                                     st.download_button("Tải PDF phiên bản này", fp, file_name=f"{selected_version}.pdf")
# # # # Phục hồi phiên bản cũ
# # # if st.button("Phục hồi phiên bản được chọn", key="vm_restore"):
# # # restore_target_path = f"./restored_{selected_version}.pdf"
# # # restore_version(doc_id_vm, selected_version, restore_target_path)
# # # st.success(f"Phục hồi thành công! File lưu tại {restore_target_path}")
# # # else:
# # # st.info("Chưa có phiên bản nào cho tài liệu này.")
# # # except Exception as e:
# # # st.error(f"Lỗi hiển thị phiên bản: {e}")


# # # === Cấu trúc điều hướng (ví dụ nếu muốn kết hợp nhiều module) ===
# # # st.sidebar.title("🛠️ Công cụ")
# # # app_mode = st.sidebar.selectbox(
# # # "Chọn chức năng:",
# # #     ["Trí tuệ Tài liệu", "Trích xuất Form", "Phân tích Cảm xúc", "Trích xuất Bảng", "So sánh Tài liệu", "Ký PDF", "Quản lý Phiên bản"]
# # # )

# # # if app_mode == "Trí tuệ Tài liệu":
# # # # Phần UI chính ở trên sẽ chạy ở đây
# # #     pass 
# # # elif app_mode == "Trích xuất Form":
# # # run_form_extractor_ui()
# # # elif app_mode == "Phân tích Cảm xúc":
# # # run_sentiment_analysis_ui()
# # # elif app_mode == "Trích xuất Bảng":
# # # run_table_extractor_ui()
# # # elif app_mode == "So sánh Tài liệu":
# # # run_document_comparison_ui()
# # # elif app_mode == "Ký PDF":
# # # run_pdf_signer_ui()
# # # elif app_mode == "Quản lý Phiên bản":
# # # run_version_manager_ui()