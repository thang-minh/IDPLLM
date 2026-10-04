# # ui_modules/main_smartdoc_ui.py
# import streamlit as st
# import tempfile
# import os
# import asyncio
# from PIL import Image # Cần cho display_random_meme

# # Import các hàm logic từ thư mục logic
# from logic.common_processing import (
#     convert_pdf_to_txt,
#     convert_pdf_to_images,
#     extract_text_from_list_of_images,
#     preprocess_text_nlp,
#     process_document_for_main_smartdoc, # Đổi tên từ process_document
#     generate_groq_response # Cho Q&A và Translate
# )
# from ui_utils.fun_meme import display_random_meme # Import hàm hiển thị meme

# def show_main_smartdoc_ui(api_key, poppler_path_env):
#     st.markdown("<h1 style='text-align: center;'>🧠 Trí tuệ Tài liệu (Xử lý PDF)</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Tải lên tài liệu PDF để trích xuất, phân tích, tóm tắt, hỏi đáp và dịch thuật nội dung.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     # Khởi tạo session state cho module này (dùng key có prefix để tránh trùng)
#     if 'msd_full_text' not in st.session_state: st.session_state.msd_full_text = ""
#     if 'msd_preview_images' not in st.session_state: st.session_state.msd_preview_images = []
#     if 'msd_ai_results' not in st.session_state: st.session_state.msd_ai_results = None
#     if 'msd_processing_done' not in st.session_state: st.session_state.msd_processing_done = False
#     if 'msd_last_filename' not in st.session_state: st.session_state.msd_last_filename = None


#     uploaded_file = st.file_uploader(
#         "\U0001F4C4 Tải lên file PDF của bạn:",
#         type="pdf",
#         key="msd_pdf_uploader",
#         help="Tải lên tài liệu PDF để trích xuất và phân tích."
#     )

#     if uploaded_file:
#         # Reset state nếu file mới được tải lên
#         if uploaded_file.name != st.session_state.msd_last_filename:
#             st.session_state.msd_full_text = ""
#             st.session_state.msd_preview_images = []
#             st.session_state.msd_ai_results = None
#             st.session_state.msd_processing_done = False
#             st.session_state.msd_last_filename = uploaded_file.name
#             # st.experimental_rerun() # Cân nhắc rerun để clear UI cũ ngay lập tức

#         file_data = uploaded_file.read()

#         # --- HIỂN THỊ PREVIEW PDF ---
#         if not st.session_state.msd_preview_images: # Chỉ tạo preview nếu chưa có
#             with st.spinner("⏳ Đang tạo preview PDF (tối đa 5 trang đầu)..."):
#                 temp_pdf_path = None
#                 try:
#                     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                         tmp.write(file_data)
#                         temp_pdf_path = tmp.name
                    
#                     # Xử lý Poppler path trong hàm logic
#                     # poppler_bin_path sẽ được suy ra từ poppler_path_env trong hàm convert_pdf_to_images
#                     st.session_state.msd_preview_images = convert_pdf_to_images(
#                         temp_pdf_path, 
#                         first_page=1, last_page=5, 
#                         poppler_path=poppler_path_env # Truyền env path, logic sẽ tìm 'bin'
#                     )
#                 except ValueError as ve: # Lỗi từ logic của chúng ta
#                     st.warning(f"{ve}")
#                     st.session_state.msd_preview_images = []
#                 except Exception as e:
#                     st.warning(f"⚠️ Lỗi không xác định khi tạo preview PDF: {e}")
#                     st.session_state.msd_preview_images = []
#                 finally:
#                     if temp_pdf_path and os.path.exists(temp_pdf_path):
#                         os.unlink(temp_pdf_path)
        
#         if st.session_state.msd_preview_images:
#             with st.container(border=True):
#                 st.subheader("\U0001F5BC Xem trước tài liệu:")
#                 cols = st.columns(min(len(st.session_state.msd_preview_images), 3))
#                 for i, page_img in enumerate(st.session_state.msd_preview_images):
#                     cols[i % len(cols)].image(page_img, caption=f"Trang {i+1}", use_column_width=True)
#         st.markdown("---")

#         # --- NÚT XỬ LÝ ---
#         if not st.session_state.msd_processing_done:
#             if st.button("🚀 Bắt đầu Xử lý Tài liệu", type="primary", key="msd_process_button", use_container_width=True):
#                 st.session_state.msd_full_text = ""
#                 st.session_state.msd_ai_results = None

#                 ocr_errors = []
#                 with st.spinner("⏳ Đang trích xuất văn bản từ PDF (PyMuPDF)..."):
#                     try:
#                         text_from_pdf_direct = convert_pdf_to_txt(file_data)
#                         st.session_state.msd_full_text = text_from_pdf_direct
#                     except ValueError as ve:
#                         st.error(f"Lỗi trích xuất PDF: {ve}")
#                         st.session_state.msd_processing_done = True # Dừng xử lý
#                         st.rerun()


#                 if st.session_state.msd_preview_images: # Chỉ chạy OCR nếu có ảnh preview
#                     with st.spinner("🧠 Đang chạy OCR trên ảnh preview (Tesseract)..."):
#                         try:
#                             # Giới hạn OCR cho các trang preview để tiết kiệm thời gian
#                             text_from_ocr = extract_text_from_list_of_images(st.session_state.msd_preview_images, lang='vie+eng', preprocess=True)
#                             if text_from_ocr.strip():
#                                 st.session_state.msd_full_text += "\n\n--- VĂN BẢN TỪ OCR (TRANG PREVIEW) ---\n" + text_from_ocr
#                         except ValueError as ve:
#                              ocr_errors.append(f"Lỗi OCR: {ve}")
#                         except Exception as e_ocr:
#                              ocr_errors.append(f"Lỗi OCR không xác định: {e_ocr}")
                
#                 if ocr_errors:
#                     for err in ocr_errors: st.warning(err)

#                 if not st.session_state.msd_full_text.strip():
#                     st.error("Không thể trích xuất văn bản nào từ tài liệu.")
#                     st.session_state.msd_processing_done = True # Dừng nếu không có text
#                 else:
#                     if api_key:
#                         with st.spinner("🤖 AI đang phân tích tài liệu... Việc này có thể mất một lúc."):
#                             try:
#                                 entities, relationships, summary, classification = asyncio.run(
#                                     process_document_for_main_smartdoc(api_key, st.session_state.msd_full_text)
#                                 )
#                                 st.session_state.msd_ai_results = {
#                                     "entities": entities, "relationships": relationships,
#                                     "summary": summary, "classification": classification
#                                 }
#                                 if any("[Lỗi AI:" in str(res) for res in st.session_state.msd_ai_results.values()):
#                                     st.warning("Một số tác vụ AI gặp lỗi. Xem chi tiết trong các tab kết quả.")
#                                 else:
#                                     st.success("🎉 Phân tích tài liệu hoàn tất!")
#                             except ValueError as ve: # Lỗi từ logic của chúng ta (vd: API key)
#                                 st.error(f"Lỗi cấu hình AI: {ve}")
#                                 st.session_state.msd_ai_results = None
#                             except Exception as e_ai:
#                                 st.error(f"Lỗi không mong muốn trong quá trình phân tích AI: {e_ai}")
#                                 st.session_state.msd_ai_results = None
#                     else:
#                         st.warning("API Key chưa được cấu hình. Bỏ qua bước phân tích AI.")
#                     st.session_state.msd_processing_done = True
#                 st.rerun() # Chạy lại để hiển thị kết quả trong tabs

#         # --- HIỂN THỊ KẾT QUẢ SAU KHI XỬ LÝ ---
#         if st.session_state.msd_processing_done and st.session_state.msd_full_text:
#             st.header("📊 Kết quả Xử lý")
            
#             tab_titles = ["📜 Văn bản", "🤖 Phân tích AI", "💬 Hỏi đáp", "🌐 Dịch thuật"]
#             tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

#             with tab1: # Văn bản Trích xuất
#                 st.subheader("📝 Văn bản đầy đủ đã trích xuất:")
#                 st.text_area("Nội dung đầy đủ (PDF + OCR nếu có):", st.session_state.msd_full_text, height=350, key="msd_full_text_display_area", help="Bao gồm văn bản trích xuất trực tiếp từ PDF và văn bản từ OCR (nếu có).")
                
#                 with st.expander("🧐 Văn bản sau tiền xử lý (chia theo câu)"):
#                     preprocessed_sentences = preprocess_text_nlp(st.session_state.msd_full_text)
#                     st.text_area("Các câu đã làm sạch:", "\n".join(preprocessed_sentences), height=200, key="msd_cleaned_text_display_area")

#             with tab2: # Phân tích AI
#                 if st.session_state.msd_ai_results:
#                     res = st.session_state.msd_ai_results
#                     st.subheader("📄 Tóm tắt Tài liệu:")
#                     st.markdown(f"<div style='background-color:#FFFFFF; padding:10px; border-radius:5px;'>{res.get('summary', 'N/A')}</div>", unsafe_allow_html=True)
                    
#                     st.subheader("\U0001F5C2 Phân loại Tài liệu:")
#                     st.info(f"**Loại tài liệu dự đoán:** {res.get('classification', 'N/A')}")

#                     with st.expander("📌 Thực thể (Entities) được trích xuất"):
#                         st.text_area("Entities:", res.get('entities', 'N/A'), height=150, key="msd_entities_display_area")
                    
#                     with st.expander("🔗 Mối quan hệ (Relationships) giữa các thực thể"):
#                         st.text_area("Relationships:", res.get('relationships', 'N/A'), height=150, key="msd_relationships_display_area")
#                 elif api_key:
#                     st.info("Chưa có kết quả phân tích AI hoặc quá trình AI gặp lỗi.")
#                 else:
#                     st.warning("Phân tích AI không được thực hiện do thiếu API Key.")

#             with tab3: # Hỏi đáp
#                 st.subheader("\U0001F4AC Chat với Tài liệu của bạn:")
#                 if api_key:
#                     user_question = st.text_input("Câu hỏi của bạn về nội dung tài liệu:", key="msd_chat_question_input", placeholder="Ví dụ: Hợp đồng này có hiệu lực khi nào?")
#                     if user_question:
#                         if st.button("💬 Gửi câu hỏi", key="msd_ask_doc_button", type="primary"):
#                             with st.spinner("🤖 AI đang tìm câu trả lời..."):
#                                 context_for_qa = st.session_state.msd_full_text[:30000] # Giới hạn context
#                                 qa_prompt = f"Dựa vào nội dung tài liệu sau đây, hãy trả lời câu hỏi một cách chính xác và ngắn gọn. Nếu không tìm thấy thông tin trong tài liệu, hãy trả lời là 'Tôi không tìm thấy thông tin này trong tài liệu.'. Trả lời bằng tiếng Việt.\n\n--- TÀI LIỆU ---\n{context_for_qa}\n\n--- CÂU HỎI ---\n{user_question}"
#                                 try:
#                                     answer = asyncio.run(generate_groq_response(api_key, qa_prompt, system_message="Bạn là một trợ lý AI chuyên trả lời câu hỏi dựa trên tài liệu được cung cấp.", max_tokens=500))
#                                     st.success("Câu trả lời từ AI:")
#                                     st.markdown(f"<div style='background-color:#FFFFFF; padding:10px; border-radius:5px;'>{answer}</div>", unsafe_allow_html=True)
#                                 except ValueError as ve:
#                                     st.error(f"Lỗi khi hỏi đáp: {ve}")
#                                 except Exception as e_qa:
#                                     st.error(f"Lỗi không mong muốn khi hỏi đáp: {e_qa}")
#                 else:
#                     st.warning("Tính năng Chat với Tài liệu yêu cầu API Key.")

#             with tab4: # Dịch thuật
#                 st.subheader("\U0001F310 Dịch một phần Văn bản:")
#                 if api_key:
#                     text_to_translate_sample = st.session_state.msd_full_text[:5000] # Dịch 4000 ký tự đầu
#                     st.info(f"Lưu ý: Chỉ dịch khoảng {len(text_to_translate_sample)} ký tự đầu tiên của văn bản để demo.")
                    
#                     target_lang_options = {"English": "Tiếng Anh", "Vietnamese": "Tiếng Việt", "Spanish": "Tiếng Tây Ban Nha", "French": "Tiếng Pháp", "German": "Tiếng Đức", "Japanese": "Tiếng Nhật", "Chinese (Simplified)": "Tiếng Trung (Giản thể)", "Korean": "Tiếng Hàn"}
#                     selected_lang_display = st.selectbox(
#                         "Chọn ngôn ngữ muốn dịch:",
#                         options=list(target_lang_options.keys()),
#                         format_func=lambda x: target_lang_options[x], # Hiển thị tên tiếng Việt
#                         index=0, 
#                         key="msd_target_language_select"
#                     )
#                     if st.button("🌍 Dịch ngay", key="msd_translate_doc_button", type="primary"):
#                         with st.spinner(f"Đang dịch sang {target_lang_options[selected_lang_display]}..."):
#                             translation_prompt = f"Translate the following text accurately to {selected_lang_display}. Provide only the translated text, without any additional explanations or conversational phrases:\n\n{text_to_translate_sample}"
#                             try:
#                                 translation_result = asyncio.run(generate_groq_response(api_key, translation_prompt, system_message="You are a highly skilled multilingual translator.", max_tokens=1500))
#                                 st.text_area(f"Bản dịch sang {target_lang_options[selected_lang_display]}:", translation_result, height=200, key="msd_translation_output_area")
#                                 st.download_button(
#                                     f"📥 Tải bản dịch ({target_lang_options[selected_lang_display]})",
#                                     translation_result,
#                                     file_name=f"translation_{selected_lang_display.replace(' ','_')}.txt",
#                                     mime="text/plain",
#                                     key="msd_download_translation_button"
#                                 )
#                             except ValueError as ve:
#                                 st.error(f"Lỗi khi dịch: {ve}")
#                             except Exception as e_trans:
#                                 st.error(f"Lỗi không mong muốn khi dịch: {e_trans}")
#                 else:
#                     st.warning("Tính năng Dịch thuật yêu cầu API Key.")
            
#             # --- TẢI KẾT QUẢ ---
#             st.markdown("---")
#             with st.container(border=True):
#                 st.header("\U0001F4E5 Tải xuống Kết quả Xử lý")
#                 col_dl1, col_dl2, col_dl3 = st.columns(3)

#                 with col_dl1:
#                     if st.session_state.msd_ai_results and st.session_state.msd_ai_results.get("summary") and not "[Lỗi AI:" in st.session_state.msd_ai_results.get("summary"):
#                         st.download_button(label="📥 Tải Tóm tắt (.txt)", data=st.session_state.msd_ai_results["summary"], file_name="summary.txt", mime="text/plain", key="msd_download_summary", use_container_width=True)
#                     else: st.button("📥 Tải Tóm tắt (.txt)", disabled=True, use_container_width=True)
                
#                 with col_dl2:
#                     if st.session_state.msd_ai_results and st.session_state.msd_ai_results.get("entities") and not "[Lỗi AI:" in st.session_state.msd_ai_results.get("entities"):
#                         info_to_download = f"THỰC THỂ (ENTITIES):\n{st.session_state.msd_ai_results['entities']}\n\nMỐI QUAN HỆ (RELATIONSHIPS):\n{st.session_state.msd_ai_results.get('relationships', 'N/A')}"
#                         st.download_button(label="📥 Tải Thông tin Trích xuất (.txt)", data=info_to_download, file_name="extracted_information.txt", mime="text/plain", key="msd_download_info", use_container_width=True)
#                     else: st.button("📥 Tải Thông tin Trích xuất (.txt)", disabled=True, use_container_width=True)

#                 with col_dl3:
#                     st.download_button(label="📥 Tải Văn bản Đầy đủ (.txt)", data=st.session_state.msd_full_text, file_name="full_document_text.txt", mime="text/plain", key="msd_download_full_text", use_container_width=True)
            
#             st.markdown("---")
#             display_random_meme() # Hiển thị meme

#     elif not uploaded_file and not st.session_state.msd_processing_done: # Chỉ hiển thị khi chưa có file và chưa xử lý gì
#         st.info("Chào mừng! Vui lòng tải lên một file PDF để bắt đầu với module 'Trí tuệ Tài liệu'.")

# # ui_modules/main_smartdoc_ui.py
# import streamlit as st
# import tempfile
# import os
# import asyncio
# from PIL import Image

# # Import logic
# from logic.common_processing import (
#     convert_pdf_to_txt,
#     convert_pdf_to_images,
#     extract_text_from_list_of_images,
#     preprocess_text_nlp,
#     process_document_for_main_smartdoc,
#     generate_groq_response
# )
# from ui_utils.fun_meme import display_random_meme

# # === IMPORT MÔ HÌNH TỰ HUẤN LUYỆN ===
# from logic.document_classifier_logic import classify_document_phobert  # <<<< ĐÃ THÊM

# def show_main_smartdoc_ui(api_key, poppler_path_env):
#     st.markdown("<h1 style='text-align: center;'>Trí tuệ Tài liệu (Xử lý PDF)</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Tải lên tài liệu PDF để trích xuất, phân tích, tóm tắt, hỏi đáp và dịch thuật nội dung.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     # Session state
#     for key in ['msd_full_text', 'msd_preview_images', 'msd_ai_results', 'msd_processing_done', 'msd_last_filename', 'msd_phobert_result']:
#         if key not in st.session_state:
#             st.session_state[key] = "" if "text" in key or "result" in key else [] if "images" in key else None if "results" in key else False

#     uploaded_file = st.file_uploader("Tải lên file PDF:", type="pdf", key="msd_pdf_uploader")

#     if uploaded_file:
#         # Reset nếu file mới
#         if uploaded_file.name != st.session_state.msd_last_filename:
#             for k in ['msd_full_text', 'msd_preview_images', 'msd_ai_results', 'msd_phobert_result']:
#                 st.session_state[k] = "" if 'text' in k or 'result' in k else []
#             st.session_state.msd_processing_done = False
#             st.session_state.msd_last_filename = uploaded_file.name

#         file_data = uploaded_file.read()

#         # --- PREVIEW (TỰ ĐỘNG BỎ QUA NẾU LỖI POPPLER) ---
#         if poppler_path_env and not st.session_state.msd_preview_images:
#             with st.spinner("Tạo preview..."):
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                     tmp.write(file_data)
#                     temp_path = tmp.name
#                 try:
#                     st.session_state.msd_preview_images = convert_pdf_to_images(temp_path, 1, 5, poppler_path_env)
#                 except Exception as e:
#                     st.warning(f"Không tạo được preview: {e} → Bỏ qua.")
#                 finally:
#                     if os.path.exists(temp_path): os.unlink(temp_path)

#         if st.session_state.msd_preview_images:
#             with st.container(border=True):
#                 st.subheader("Xem trước:")
#                 cols = st.columns(min(3, len(st.session_state.msd_preview_images)))
#                 for i, img in enumerate(st.session_state.msd_preview_images):
#                     cols[i % 3].image(img, f"Trang {i+1}", use_column_width=True)
#         st.markdown("---")

#         # --- XỬ LÝ ---
#         if not st.session_state.msd_processing_done:
#             if st.button("Bắt đầu Xử lý", type="primary", use_container_width=True):
#                 with st.spinner("Trích xuất văn bản..."):
#                     try:
#                         st.session_state.msd_full_text = convert_pdf_to_txt(file_data)
#                     except Exception as e:
#                         st.error(f"Lỗi: {e}")
#                         st.stop()

#                     if st.session_state.msd_preview_images:
#                         try:
#                             ocr = extract_text_from_list_of_images(st.session_state.msd_preview_images, 'vie+eng', True)
#                             if ocr.strip():
#                                 st.session_state.msd_full_text += "\n\n--- OCR ---\n" + ocr
#                         except: pass

#                     if not st.session_state.msd_full_text.strip():
#                         st.error("Không có văn bản.")
#                     else:
#                         if api_key:
#                             with st.spinner("AI phân tích..."):
#                                 try:
#                                     e, r, s, c = asyncio.run(process_document_for_main_smartdoc(api_key, st.session_state.msd_full_text))
#                                     st.session_state.msd_ai_results = {"entities": e, "relationships": r, "summary": s, "classification": c}
#                                     st.success("Hoàn tất!")
#                                 except Exception as e:
#                                     st.error(f"Lỗi AI: {e}")
#                         st.session_state.msd_processing_done = True
#                 st.rerun()

#         # --- KẾT QUẢ ---
#         if st.session_state.msd_processing_done and st.session_state.msd_full_text:
#             st.header("Kết quả Xử lý")
#             tab1, tab2, tab3, tab4 = st.tabs(["Văn bản", "Phân tích AI", "Hỏi đáp", "Dịch thuật"])

#             with tab1:
#                 st.subheader("Văn bản đầy đủ:")
#                 st.text_area("", st.session_state.msd_full_text, height=350, key="txt_full")
#                 with st.expander("Đã làm sạch"):
#                     st.text_area("", "\n".join(preprocess_text_nlp(st.session_state.msd_full_text)), height=200, key="txt_clean")

#             with tab2:
#                 res = st.session_state.msd_ai_results or {}

#                 # === PHẦN CHỌN MÔ HÌNH TỰ HUẤN LUYỆN ===
#                 st.markdown("### Chọn Mô hình Phân loại")
#                 model_choice = st.radio(
#                     "Bạn muốn dùng mô hình nào?",
#                     ["LLM (Groq)", "PhoBERT (Tự huấn luyện)"],
#                     index=1,  # Mặc định chọn PhoBERT
#                     key="model_radio",
#                     horizontal=True
#                 )

#                 col1, col2 = st.columns(2)

#                 with col1:
#                     st.markdown("**LLM (Groq):**")
#                     st.info(res.get("classification", "Chưa có"))

#                 with col2:
#                     st.markdown("**PhoBERT (Tự huấn luyện):**")
#                     if model_choice == "PhoBERT (Tự huấn luyện)":
#                         if not st.session_state.msd_phobert_result:
#                             with st.spinner("PhoBERT đang phân loại..."):
#                                 try:
#                                     st.session_state.msd_phobert_result = classify_document_phobert(st.session_state.msd_full_text)
#                                 except Exception as e:
#                                     st.session_state.msd_phobert_result = f"Lỗi: {e}"
#                         st.success(st.session_state.msd_phobert_result)
#                     else:
#                         st.info("Chưa chạy")

#                 st.markdown("---")
#                 st.subheader("Tóm tắt:")
#                 st.markdown(f"<div style='background:#1e1e1e; color:#fff; padding:12px; border-radius:8px;'>{res.get('summary', 'N/A')}</div>", unsafe_allow_html=True)

#                 with st.expander("Thực thể"):
#                     st.text_area("", res.get('entities', 'N/A'), height=120, key="ent_text")
#                 with st.expander("Mối quan hệ"):
#                     st.text_area("", res.get('relationships', 'N/A'), height=120, key="rel_text")

#             with tab3:
#                 st.subheader("Hỏi đáp")
#                 if api_key:
#                     q = st.text_input("Câu hỏi:", key="qa_in")
#                     if q and st.button("Gửi", key="qa_btn"):
#                         with st.spinner("Đang trả lời..."):
#                             ans = asyncio.run(generate_groq_response(api_key, f"Trả lời ngắn gọn:\n{st.session_state.msd_full_text[:15000]}\n\nCâu hỏi: {q}", max_tokens=400))
#                             st.success(ans)
#                 else:
#                     st.warning("Cần API Key")

#             with tab4:
#                 st.subheader("Dịch thuật")
#                 if api_key:
#                     lang = st.selectbox("Dịch sang:", ["English", "French", "Chinese (Simplified)"], key="trans_lang")
#                     if st.button("Dịch", key="trans_btn"):
#                         with st.spinner("Đang dịch..."):
#                             trans = asyncio.run(generate_groq_response(api_key, f"Translate to {lang}:\n{st.session_state.msd_full_text[:3000]}", max_tokens=1000))
#                             st.text_area("Kết quả:", trans, height=150, key="trans_out")
#                             st.download_button("Tải", trans, f"trans_{lang}.txt", key="dl_trans")
#                 else:
#                     st.warning("Cần API Key")

#             # === TẢI XUỐNG ===
#             st.markdown("---")
#             st.subheader("Tải kết quả")
#             c1, c2, c3 = st.columns(3)
#             with c1: st.download_button("Tóm tắt", res.get("summary",""), "summary.txt", key="dl1")
#             with c2: st.download_button("Thông tin", f"Entities:\n{res.get('entities','')}\n\nRelationships:\n{res.get('relationships','')}", "info.txt", key="dl2")
#             with c3: st.download_button("Văn bản", st.session_state.msd_full_text, "full.txt", key="dl3")

#             st.markdown("---")
#             display_random_meme()

#     else:
#         st.info("Vui lòng tải lên PDF để bắt đầu.")


# import streamlit as st
# import tempfile
# import os
# import asyncio
# from PIL import Image

# # Import logic
# from logic.common_processing import (
#     convert_pdf_to_txt,
#     convert_pdf_to_images,
#     extract_text_from_list_of_images,
#     preprocess_text_nlp,
#     process_document_for_main_smartdoc,
#     generate_groq_response
# )
# from ui_utils.fun_meme import display_random_meme

# # Import Model Local
# from logic.document_classifier_logic import classify_document_phobert

# def show_main_smartdoc_ui(api_key, poppler_path_env):
#     st.markdown("<h1 style='text-align: center;'>Trí tuệ Tài liệu (Xử lý PDF)</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>Quy trình Hybrid: <b>Phân loại nhanh (Local)</b> &rarr; <b>Phân tích sâu (Cloud API)</b>.</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     # --- KHỞI TẠO SESSION STATE ---
#     # Thêm 2 cờ trạng thái mới: msd_local_done (xong bước 1) và msd_api_done (xong bước 2)
#     defaults = {
#         'msd_full_text': "", 
#         'msd_preview_images': [], 
#         'msd_ai_results': None, 
#         'msd_last_filename': None, 
#         'msd_phobert_result': None,
#         'msd_local_done': False, # Đã chạy xong model local chưa
#         'msd_api_done': False    # Đã chạy xong API chưa
#     }
#     for key, val in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = val

#     uploaded_file = st.file_uploader("Tải lên file PDF:", type="pdf", key="msd_pdf_uploader")

#     if uploaded_file:
#         # Reset trạng thái khi có file mới hoàn toàn
#         if uploaded_file.name != st.session_state.msd_last_filename:
#             for key in defaults.keys():
#                 st.session_state[key] = defaults[key]
#             # Giữ lại filename mới
#             st.session_state.msd_last_filename = uploaded_file.name

#         file_data = uploaded_file.read()

#         # --- 1. PREVIEW PDF (Tự động chạy khi up file) ---
#         if poppler_path_env and not st.session_state.msd_preview_images:
#             with st.spinner("Đang tạo bản xem trước..."):
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                     tmp.write(file_data)
#                     temp_path = tmp.name
#                 try:
#                     st.session_state.msd_preview_images = convert_pdf_to_images(temp_path, 1, 3, poppler_path_env)
#                 except Exception: pass
#                 finally:
#                     if os.path.exists(temp_path): os.unlink(temp_path)

#         if st.session_state.msd_preview_images:
#             with st.expander("👁️ Xem trước tài liệu (Trang đầu)", expanded=False):
#                 cols = st.columns(len(st.session_state.msd_preview_images))
#                 for i, img in enumerate(st.session_state.msd_preview_images):
#                     cols[i].image(img, f"Trang {i+1}", use_column_width=True)
        
#         st.markdown("---")

#         # =========================================================
#         # GIAI ĐOẠN 1: CHẠY LOCAL (Trích xuất Text + Model PhoBERT)
#         # =========================================================
        
#         # Nút bấm chạy Giai đoạn 1 (Chỉ hiện khi chưa chạy xong)
#         if not st.session_state.msd_local_done:
#             if st.button("🚀 Bước 1: Trích xuất & Phân loại nhanh (Local)", type="primary", use_container_width=True):
                
#                 with st.status("Đang xử lý nội bộ...", expanded=True) as status:
#                     # A. Trích xuất Text
#                     st.write("📄 Đang đọc văn bản từ PDF...")
#                     try:
#                         st.session_state.msd_full_text = convert_pdf_to_txt(file_data)
#                         # Fallback OCR nếu file scan
#                         if len(st.session_state.msd_full_text) < 100 and st.session_state.msd_preview_images:
#                             st.write("🔍 Text gốc ít, đang chạy OCR bổ sung...")
#                             ocr_text = extract_text_from_list_of_images(st.session_state.msd_preview_images, 'vie', True)
#                             st.session_state.msd_full_text += "\n" + ocr_text
#                     except Exception as e:
#                         st.error(f"Lỗi đọc file: {e}")
#                         st.stop()

#                     if not st.session_state.msd_full_text.strip():
#                         st.error("Không tìm thấy văn bản nào.")
#                         st.stop()

#                     # B. Chạy Model Local
#                     st.write("⚡ Đang chạy Model PhoBERT...")
#                     try:
#                         st.session_state.msd_phobert_result = classify_document_phobert(st.session_state.msd_full_text)
#                     except Exception as e:
#                         st.session_state.msd_phobert_result = f"Lỗi: {e}"
                    
#                     # Đánh dấu đã xong bước 1
#                     st.session_state.msd_local_done = True
#                     status.update(label="Đã phân loại xong!", state="complete", expanded=False)
                
#                 st.rerun()

#         # HIỂN THỊ KẾT QUẢ GIAI ĐOẠN 1
#         if st.session_state.msd_local_done:
#             with st.container(border=True):
#                 col_local_1, col_local_2 = st.columns([2, 1])
#                 with col_local_1:
#                     st.subheader("🏷️ Kết quả Phân loại (Local)")
#                     res_local = st.session_state.msd_phobert_result
                    
#                     if "Lỗi" in str(res_local):
#                         st.error(res_local)
#                     else:
#                         st.success(f"Dự đoán: **{res_local}**")
#                         st.caption("Mô hình PhoBERT tự huấn luyện (Chạy offline)")
                
#                 with col_local_2:
#                     # Xem nhanh văn bản trích xuất
#                     with st.popover("Xem văn bản thô"):
#                         st.text_area("Nội dung:", st.session_state.msd_full_text, height=300)

#         # =========================================================
#         # GIAI ĐOẠN 2: CHẠY API (Tùy chọn)
#         # =========================================================
        
#         # Chỉ hiện nút API khi đã xong Local
#         if st.session_state.msd_local_done:
#             st.markdown("---")
            
#             # Nếu chưa chạy API thì hiện nút
#             if not st.session_state.msd_api_done:
#                 st.info("Bạn muốn phân tích chi tiết? (Tóm tắt, Trích xuất thông tin, Dịch thuật...)")
#                 if st.button("🧠 Bước 2: Phân tích sâu với AI (Call API)", type="secondary", use_container_width=True):
#                     if not api_key:
#                         st.error("Thiếu API Key!")
#                     else:
#                         with st.spinner("Đang gửi dữ liệu lên đám mây..."):
#                             try:
#                                 e, r, s, c = asyncio.run(process_document_for_main_smartdoc(api_key, st.session_state.msd_full_text))
#                                 st.session_state.msd_ai_results = {
#                                     "entities": e, 
#                                     "relationships": r, 
#                                     "summary": s, 
#                                     "classification": c 
#                                 }
#                                 st.session_state.msd_api_done = True # Đánh dấu xong bước 2
#                                 st.rerun()
#                             except Exception as e:
#                                 st.error(f"Lỗi API: {e}")

#             # HIỂN THỊ KẾT QUẢ GIAI ĐOẠN 2 (Nếu đã chạy xong)
#             if st.session_state.msd_api_done:
#                 st.success("✅ Đã hoàn tất phân tích sâu!")
                
#                 # So sánh nhẹ
#                 api_class = st.session_state.msd_ai_results.get("classification", "N/A")
#                 st.caption(f"🤖 AI API cũng nhận định đây là: **{api_class}**")

#                 # Tabs hiển thị chi tiết
#                 tab1, tab2, tab3 = st.tabs(["📝 Tóm tắt & TT", "💬 Hỏi đáp", "🌍 Dịch thuật"])

#                 with tab1:
#                     res = st.session_state.msd_ai_results or {}
#                     st.subheader("Tóm tắt nội dung:")
#                     st.markdown(f"<div style='background: #f8f8f8; padding:15px; border-radius:10px;'>{res.get('summary', 'Chưa có dữ liệu')}</div>", unsafe_allow_html=True)
                    
#                     c1, c2 = st.columns(2)
#                     with c1:
#                         st.markdown("**Thực thể:**")
#                         st.info(res.get('entities', 'N/A'))
#                     with c2:
#                         st.markdown("**Quan hệ:**")
#                         st.info(res.get('relationships', 'N/A'))

#                 with tab2:
#                     st.subheader("Chat với tài liệu")
#                     user_q = st.text_input("Đặt câu hỏi:", key="chat_q")
#                     if user_q and st.button("Gửi"):
#                          with st.spinner("Thinking..."):
#                             ans = asyncio.run(generate_groq_response(api_key, f"Context:\n{st.session_state.msd_full_text[:10000]}\n\nQuestion: {user_q}"))
#                             st.write(ans)

#                 with tab3:
#                     st.subheader("Dịch thuật")
#                     lang = st.selectbox("Ngôn ngữ:", ["English", "Chinese", "Japanese"])
#                     if st.button("Dịch ngay"):
#                          with st.spinner("Translating..."):
#                             trans = asyncio.run(generate_groq_response(api_key, f"Translate to {lang}:\n{st.session_state.msd_full_text[:3000]}"))
#                             st.text_area("Kết quả:", trans)
                
#                 st.markdown("---")
#                 display_random_meme()

#     else:
#         st.info("👈 Vui lòng tải lên file PDF để bắt đầu.")

# ui/main_smartdoc_ui.py

import streamlit as st
import tempfile
import os
import asyncio

from logic.common_processing import (
    convert_pdf_to_txt,
    convert_pdf_to_images,
    extract_text_from_list_of_images,
    process_document_for_main_smartdoc,
    generate_groq_response
)

from logic.document_classifier_logic import classify_document_phobert
from ui_utils.fun_meme import display_random_meme


def show_main_smartdoc_ui(api_key, poppler_path_env):
    st.markdown(
        "<h1 style='text-align: center;'>SmartDoc AI - Phân loại & Phân tích tài liệu</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align: center;'>
        Quy trình xử lý: <b>PDF/Text</b> → <b>Trích xuất văn bản/OCR</b> → 
        <b>PhoBERT phân loại local</b> → <b>LLM phân tích sâu</b>
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    defaults = {
        "msd_input_mode": "Upload PDF",
        "msd_full_text": "",
        "msd_preview_images": [],
        "msd_phobert_result": None,
        "msd_ai_results": None,
        "msd_last_filename": None,
        "msd_local_done": False,
        "msd_llm_done": False,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ==========================
    # 1. CHỌN NGUỒN ĐẦU VÀO
    # ==========================

    st.subheader("1. Chọn nguồn tài liệu")

    input_mode = st.radio(
        "Nguồn đầu vào:",
        ["Upload PDF", "Nhập văn bản trực tiếp"],
        horizontal=True,
        key="msd_input_mode_radio"
    )

    if input_mode != st.session_state.msd_input_mode:
        for key, val in defaults.items():
            st.session_state[key] = val
        st.session_state.msd_input_mode = input_mode
        st.rerun()

    uploaded_file = None
    manual_text = ""

    if input_mode == "Upload PDF":
        uploaded_file = st.file_uploader(
            "Tải lên file PDF:",
            type="pdf",
            key="msd_pdf_uploader"
        )

    else:
        manual_text = st.text_area(
            "Nhập hoặc dán nội dung văn bản cần phân loại:",
            height=300,
            placeholder=(
                "Ví dụ:\n"
                "HÓA ĐƠN GIÁ TRỊ GIA TĂNG...\n"
                "hoặc\n"
                "HỢP ĐỒNG LAO ĐỘNG...\n"
                "hoặc\n"
                "BIÊN BẢN HỌP..."
            )
        )

    st.markdown("---")

    # ==========================
    # 2. XỬ LÝ PDF PREVIEW
    # ==========================

    file_data = None

    if input_mode == "Upload PDF" and uploaded_file is not None:
        if uploaded_file.name != st.session_state.msd_last_filename:
            for key, val in defaults.items():
                st.session_state[key] = val
            st.session_state.msd_input_mode = input_mode
            st.session_state.msd_last_filename = uploaded_file.name

        file_data = uploaded_file.read()

        if poppler_path_env and not st.session_state.msd_preview_images:
            with st.spinner("Đang tạo ảnh xem trước PDF..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(file_data)
                    temp_path = tmp.name

                try:
                    st.session_state.msd_preview_images = convert_pdf_to_images(
                        temp_path,
                        1,
                        3,
                        poppler_path_env
                    )
                except Exception as e:
                    st.warning(f"Không tạo được preview PDF: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

        if st.session_state.msd_preview_images:
            with st.expander("Xem trước tài liệu PDF", expanded=False):
                cols = st.columns(len(st.session_state.msd_preview_images))
                for i, img in enumerate(st.session_state.msd_preview_images):
                    cols[i].image(
                        img,
                        caption=f"Trang {i + 1}",
                        use_container_width=True
                    )

    # ==========================
    # 3. BƯỚC 1: LẤY TEXT + PHÂN LOẠI LOCAL
    # ==========================

    st.subheader("2. Trích xuất văn bản và phân loại local")

    can_run_local = False

    if input_mode == "Upload PDF" and uploaded_file is not None:
        can_run_local = True

    if input_mode == "Nhập văn bản trực tiếp" and manual_text.strip():
        can_run_local = True

    if not can_run_local:
        st.info("Vui lòng upload PDF hoặc nhập văn bản để bắt đầu.")
        return

    if not st.session_state.msd_local_done:
        if st.button(
            "Chạy phân loại bằng PhoBERT",
            type="primary",
            use_container_width=True
        ):
            with st.status("Đang xử lý tài liệu...", expanded=True) as status:
                try:
                    if input_mode == "Upload PDF":
                        st.write("Đang trích xuất text từ PDF...")

                        extracted_text = convert_pdf_to_txt(file_data)

                        if len(extracted_text.strip()) < 100 and st.session_state.msd_preview_images:
                            st.write("Text PDF ít, đang chạy OCR bổ sung...")
                            ocr_text = extract_text_from_list_of_images(
                                st.session_state.msd_preview_images,
                                "vie",
                                True
                            )
                            extracted_text = extracted_text + "\n" + ocr_text

                        st.session_state.msd_full_text = extracted_text.strip()

                    else:
                        st.write("Đang lấy văn bản người dùng nhập...")
                        st.session_state.msd_full_text = manual_text.strip()

                    if not st.session_state.msd_full_text:
                        st.error("Không tìm thấy nội dung văn bản.")
                        st.stop()

                    st.write("Đang chạy mô hình PhoBERT local...")
                    result = classify_document_phobert(st.session_state.msd_full_text)

                    st.session_state.msd_phobert_result = result
                    st.session_state.msd_local_done = True

                    status.update(
                        label="Hoàn tất phân loại local.",
                        state="complete",
                        expanded=False
                    )

                except Exception as e:
                    st.error(f"Lỗi xử lý local: {e}")
                    st.stop()

            st.rerun()

    # ==========================
    # 4. HIỂN THỊ KẾT QUẢ PHOBERT
    # ==========================

    if st.session_state.msd_local_done:
        result = st.session_state.msd_phobert_result

        with st.container(border=True):
            st.subheader("Kết quả phân loại bằng PhoBERT")

            if not result or "error" in result:
                st.error(result.get("error", "Có lỗi khi phân loại."))
            else:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.success(f"Loại tài liệu dự đoán: **{result['display_label']}**")
                    st.caption("Mô hình sử dụng: PhoBERT fine-tune, chạy local/offline.")

                with col2:
                    confidence_percent = result["confidence"] * 100
                    st.metric("Độ tin cậy", f"{confidence_percent:.2f}%")

                st.markdown("**Xác suất từng lớp:**")

                probabilities = result.get("probabilities", {})

                for label, prob in probabilities.items():
                    st.progress(
                        prob,
                        text=f"{label.replace('_', ' ')}: {prob * 100:.2f}%"
                    )

        with st.expander("Xem nội dung văn bản đã trích xuất / đã nhập", expanded=False):
            st.text_area(
                "Nội dung văn bản:",
                st.session_state.msd_full_text,
                height=350
            )

    # ==========================
    # 5. BƯỚC 2: LLM PHÂN TÍCH SÂU
    # ==========================

    if st.session_state.msd_local_done:
        st.markdown("---")
        st.subheader("3. Phân tích sâu bằng LLM")

        st.info(
            "Bước này dùng LLM để đọc nội dung văn bản, tóm tắt, trích xuất thông tin "
            "và kiểm tra lại loại tài liệu. PhoBERT dùng để phân loại nhanh local, "
            "LLM dùng để giải thích và phân tích sâu."
        )

        if not st.session_state.msd_llm_done:
            if st.button(
                "Chạy phân tích sâu bằng LLM",
                type="secondary",
                use_container_width=True
            ):
                if not api_key:
                    st.error("Thiếu API key để gọi LLM.")
                else:
                    with st.spinner("Đang gọi LLM phân tích tài liệu..."):
                        try:
                            prompt = build_llm_document_analysis_prompt(
                                text=st.session_state.msd_full_text,
                                phobert_result=st.session_state.msd_phobert_result
                            )

                            llm_response = asyncio.run(
                                generate_groq_response(api_key, prompt)
                            )

                            st.session_state.msd_ai_results = {
                                "analysis": llm_response
                            }

                            st.session_state.msd_llm_done = True
                            st.rerun()

                        except Exception as e:
                            st.error(f"Lỗi khi gọi LLM: {e}")

        if st.session_state.msd_llm_done:
            st.success("Đã hoàn tất phân tích sâu bằng LLM.")

            tab1, tab2, tab3 = st.tabs([
                "Phân tích tài liệu",
                "Hỏi đáp tài liệu",
                "Dịch thuật"
            ])

            with tab1:
                st.markdown(st.session_state.msd_ai_results.get("analysis", ""))

            with tab2:
                st.subheader("Chat với nội dung tài liệu")

                user_question = st.text_input(
                    "Nhập câu hỏi về tài liệu:",
                    key="msd_chat_question"
                )

                if st.button("Gửi câu hỏi", key="msd_send_question"):
                    if not user_question.strip():
                        st.warning("Vui lòng nhập câu hỏi.")
                    elif not api_key:
                        st.error("Thiếu API key.")
                    else:
                        with st.spinner("Đang trả lời..."):
                            context = st.session_state.msd_full_text[:12000]

                            qa_prompt = f"""
Bạn là trợ lý phân tích tài liệu.

Dựa trên nội dung tài liệu sau, hãy trả lời câu hỏi của người dùng.
Chỉ trả lời dựa trên nội dung được cung cấp. Nếu không có thông tin, hãy nói rõ là không tìm thấy trong tài liệu.

NỘI DUNG TÀI LIỆU:
{context}

CÂU HỎI:
{user_question}

TRẢ LỜI:
"""

                            answer = asyncio.run(
                                generate_groq_response(api_key, qa_prompt)
                            )

                            st.markdown(answer)

            with tab3:
                st.subheader("Dịch nội dung tài liệu")

                target_lang = st.selectbox(
                    "Chọn ngôn ngữ:",
                    ["English", "Japanese", "Chinese", "Korean"]
                )

                if st.button("Dịch tài liệu", key="msd_translate_btn"):
                    if not api_key:
                        st.error("Thiếu API key.")
                    else:
                        with st.spinner("Đang dịch..."):
                            translate_prompt = f"""
Hãy dịch nội dung tài liệu sau sang {target_lang}.
Giữ nguyên cấu trúc chính của tài liệu.

NỘI DUNG:
{st.session_state.msd_full_text[:6000]}
"""

                            translation = asyncio.run(
                                generate_groq_response(api_key, translate_prompt)
                            )

                            st.text_area(
                                "Bản dịch:",
                                translation,
                                height=400
                            )

            st.markdown("---")
            display_random_meme()


def build_llm_document_analysis_prompt(text: str, phobert_result: dict):
    label = "Không xác định"
    confidence = 0.0

    if phobert_result and "error" not in phobert_result:
        label = phobert_result.get("display_label", "Không xác định")
        confidence = phobert_result.get("confidence", 0.0) * 100

    text_for_llm = text[:12000]

    prompt = f"""
Bạn là chuyên gia phân tích tài liệu số.

Thông tin từ mô hình phân loại local:
- Mô hình: PhoBERT fine-tune
- Loại tài liệu dự đoán: {label}
- Độ tin cậy: {confidence:.2f}%

Nhiệm vụ:
Hãy phân tích nội dung tài liệu bên dưới và trình bày theo cấu trúc sau:

## 1. Loại tài liệu
- Nhận định loại tài liệu.
- So sánh ngắn với kết quả PhoBERT.
- Nếu nội dung không khớp với dự đoán PhoBERT, hãy nêu rõ.

## 2. Tóm tắt nội dung chính
Tóm tắt ngắn gọn trong 5-8 dòng.

## 3. Thông tin quan trọng được trích xuất
Tùy theo loại tài liệu, hãy trích xuất các thông tin phù hợp:

Nếu là hóa đơn:
- Tên bên bán
- Tên bên mua
- Mã số thuế
- Số hóa đơn
- Ngày lập
- Tổng tiền
- Thuế GTGT
- Hàng hóa/dịch vụ chính

Nếu là hợp đồng lao động:
- Tên người lao động
- Tên công ty
- Chức vụ/vị trí
- Mức lương
- Thời hạn hợp đồng
- Ngày ký
- Các điều khoản quan trọng

Nếu là biên bản họp:
- Tên cuộc họp
- Thời gian
- Địa điểm
- Thành phần tham dự
- Nội dung chính
- Kết luận/quyết định

## 4. Chất lượng văn bản/OCR
Đánh giá văn bản có rõ ràng không, có dấu hiệu lỗi OCR không, có thiếu thông tin không.

## 5. Gợi ý xử lý tiếp theo
Đưa ra 3-5 gợi ý ngắn gọn để người dùng xử lý tài liệu tốt hơn.

NỘI DUNG TÀI LIỆU:
{text_for_llm}
"""

    return prompt