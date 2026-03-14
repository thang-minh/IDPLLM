# ui_modules/table_extractor_ui.py
import streamlit as st
import pandas as pd # Cần cho việc tạo DataFrame rỗng nếu có lỗi

# Import các hàm logic từ thư mục logic
from logic.table_extractor import extract_tables_from_pdf, dataframe_to_excel_bytes
from ui_utils.fun_meme import display_random_meme

def show_table_extractor_ui():
    st.markdown("<h1 style='text-align: center;'>📊 Trích xuất Bảng từ PDF</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Tải lên file PDF để tự động phát hiện và trích xuất các bảng dữ liệu sang định dạng có thể chỉnh sửa.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if 'te_extracted_tables' not in st.session_state: st.session_state.te_extracted_tables = []
    if 'te_last_filename' not in st.session_state: st.session_state.te_last_filename = None

    uploaded_pdf_file = st.file_uploader(
        "📤 Tải lên file PDF chứa bảng:",
        type=["pdf"],
        key="te_pdf_uploader",
        help="Hệ thống sẽ sử dụng pdfplumber để tìm và trích xuất bảng."
    )

    if uploaded_pdf_file:
        if uploaded_pdf_file.name != st.session_state.te_last_filename:
            st.session_state.te_extracted_tables = [] # Reset khi có file mới
            st.session_state.te_last_filename = uploaded_pdf_file.name

        if not st.session_state.te_extracted_tables: # Chỉ xử lý nếu chưa có kết quả cho file này
            with st.spinner("🔄 Đang tìm và trích xuất bảng từ PDF..."):
                pdf_bytes = uploaded_pdf_file.read()
                try:
                    st.session_state.te_extracted_tables = extract_tables_from_pdf(pdf_bytes)
                except ValueError as ve:
                    st.error(f"Lỗi xử lý PDF: {ve}")
                    st.session_state.te_extracted_tables = [] # Đảm bảo là list rỗng nếu lỗi
                except Exception as e_table:
                    st.error(f"Lỗi không mong muốn khi trích xuất bảng: {e_table}")
                    st.session_state.te_extracted_tables = []


        if st.session_state.te_extracted_tables:
            st.success(f"🎉 Tìm thấy tổng cộng {len(st.session_state.te_extracted_tables)} bảng trong tài liệu!")
            st.markdown("---")
            for idx, (page_num, df) in enumerate(st.session_state.te_extracted_tables, start=1):
                with st.container(border=True):
                    st.subheader(f"📄 Bảng {idx} (từ Trang PDF số {page_num})")
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        st.dataframe(df, use_container_width=True)
                        
                        col_dl_csv, col_dl_excel = st.columns(2)
                        with col_dl_csv:
                            try:
                                csv_bytes = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label=f"📥 Tải Bảng {idx} (CSV)",
                                    data=csv_bytes,
                                    file_name=f"table_p{page_num}_idx{idx}.csv",
                                    mime="text/csv",
                                    key=f"te_csv_dl_{page_num}_{idx}",
                                    use_container_width=True
                                )
                            except Exception as e_csv:
                                st.error(f"Lỗi tạo file CSV cho bảng {idx}: {e_csv}")
                        
                        with col_dl_excel:
                            try:
                                excel_bytes = dataframe_to_excel_bytes(df)
                                st.download_button(
                                    label=f"📥 Tải Bảng {idx} (Excel)",
                                    data=excel_bytes,
                                    file_name=f"table_p{page_num}_idx{idx}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"te_excel_dl_{page_num}_{idx}",
                                    use_container_width=True
                                )
                            except ValueError as ve: # Lỗi từ logic của chúng ta
                                st.error(f"Lỗi tạo file Excel cho bảng {idx}: {ve}")
                            except Exception as e_excel:
                                st.error(f"Lỗi không mong muốn khi tạo file Excel cho bảng {idx}: {e_excel}")
                    else:
                        st.warning(f"Bảng {idx} không có dữ liệu hoặc không phải là DataFrame hợp lệ.")
                st.markdown("---")
            display_random_meme()
        elif uploaded_pdf_file: # Đã upload file nhưng không có bảng (và không có lỗi trước đó)
             if not st.session_state.get("_te_error_shown", False): # Để tránh lặp lại warning nếu có lỗi trước
                st.warning("⚠️ Không phát hiện bảng nào trong file PDF này, hoặc các bảng tìm thấy không có dữ liệu.")

    else:
        st.info("Vui lòng tải lên một file PDF để bắt đầu trích xuất bảng.")
        st.session_state.te_extracted_tables = [] # Reset khi không có file
        st.session_state.te_last_filename = None