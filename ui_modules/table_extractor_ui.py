# ui_modules/table_extractor_ui.py
import streamlit as st
import pandas as pd

from logic.table_extractor import extract_tables_from_pdf, dataframe_to_excel_bytes
from ui_utils.fun_meme import display_random_meme

def show_table_extractor_ui():
    # Header chuẩn SaaS
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-soft-indigo">Structured Data</span>
                <span class="badge-soft-success">PDF Table Parser</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em; color: #0F172A;">Trích xuất Bảng từ PDF</h2>
            <p style="color: #475569; font-size: 14px; margin: 4px 0 0 0;">
                Tự động nhận diện cấu trúc hàng - cột trong tài liệu PDF và xuất sang định dạng Excel / CSV.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if 'te_extracted_tables' not in st.session_state:
        st.session_state.te_extracted_tables = []
    if 'te_last_filename' not in st.session_state:
        st.session_state.te_last_filename = None

    # Vùng tải file
    uploaded_pdf_file = st.file_uploader(
        "Tải lên tập tin PDF chứa bảng biểu:",
        type=["pdf"],
        key="te_pdf_uploader",
        help="Hệ thống tự động quét và phân tích tọa độ các đường viền ô bảng trong PDF."
    )

    if not uploaded_pdf_file:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 2.5rem 1.5rem; text-align: center; margin-top: 1rem;">
            <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
            <div style="font-weight: 700; color: #0F172A; font-size: 15px;">Chưa có tài liệu PDF nào được tải lên</div>
            <div style="color: #64748B; font-size: 13.5px; max-width: 440px; margin: 4px auto 0 auto;">
                Hãy tải lên một tệp PDF chứa các bảng biểu, báo cáo tài chính hoặc hóa đơn để tiến hành bóc tách dữ liệu có cấu trúc.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.te_extracted_tables = []
        st.session_state.te_last_filename = None
        return

    # Reset khi có file mới
    if uploaded_pdf_file.name != st.session_state.te_last_filename:
        st.session_state.te_extracted_tables = []
        st.session_state.te_last_filename = uploaded_pdf_file.name

    # Xử lý trích xuất bảng
    if not st.session_state.te_extracted_tables:
        with st.status("Đang phân tích cấu trúc bảng trong PDF...", expanded=True) as status:
            try:
                pdf_bytes = uploaded_pdf_file.read()
                tables = extract_tables_from_pdf(pdf_bytes)
                st.session_state.te_extracted_tables = tables
                if tables:
                    status.update(label=f"✓ Đã phát hiện thành công {len(tables)} bảng biểu!", state="complete", expanded=False)
                else:
                    status.update(label="Không tìm thấy bảng biểu trong tài liệu.", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Lỗi khi trích xuất bảng: {e}")
                st.session_state.te_extracted_tables = []

    # Hiển thị kết quả
    if st.session_state.te_extracted_tables:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.25rem 0 0.75rem 0;">
            <h4 style="margin: 0; font-weight: 700; color: #0F172A;">
                Tổng cộng tìm thấy <span style="color: #4F46E5;">{len(st.session_state.te_extracted_tables)}</span> bảng dữ liệu:
            </h4>
            <span class="badge-soft-success">● Trích xuất thành công</span>
        </div>
        """, unsafe_allow_html=True)

        for idx, (page_num, df) in enumerate(st.session_state.te_extracted_tables, start=1):
            with st.container(border=True):
                # Header thẻ bảng
                n_rows, n_cols = (df.shape[0], df.shape[1]) if isinstance(df, pd.DataFrame) else (0, 0)
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div>
                        <span style="font-weight: 800; font-size: 15px; color: #0F172A;">Bảng #{idx}</span>
                        <span style="color: #64748B; font-size: 13px; margin-left: 8px;">(Trang PDF: {page_num})</span>
                    </div>
                    <span class="badge-soft-neutral">{n_rows} hàng × {n_cols} cột</span>
                </div>
                """, unsafe_allow_html=True)

                if isinstance(df, pd.DataFrame) and not df.empty:
                    st.dataframe(df, use_container_width=True)

                    c_csv, c_excel = st.columns(2)
                    with c_csv:
                        try:
                            csv_bytes = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"📥 Tải Bảng #{idx} (CSV)",
                                data=csv_bytes,
                                file_name=f"table_page{page_num}_{idx}.csv",
                                mime="text/csv",
                                key=f"te_csv_dl_{page_num}_{idx}",
                                use_container_width=True
                            )
                        except Exception as e_csv:
                            st.error(f"Lỗi tạo CSV: {e_csv}")

                    with c_excel:
                        try:
                            excel_bytes = dataframe_to_excel_bytes(df)
                            st.download_button(
                                label=f"📊 Tải Bảng #{idx} (Excel .xlsx)",
                                data=excel_bytes,
                                file_name=f"table_page{page_num}_{idx}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"te_excel_dl_{page_num}_{idx}",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e_excel:
                            st.error(f"Lỗi tạo Excel: {e_excel}")
                else:
                    st.warning(f"Bảng #{idx} không có dữ liệu hợp lệ.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        display_random_meme()

    elif uploaded_pdf_file:
        st.markdown("""
        <div style="background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 1rem 1.25rem; margin-top: 1rem;">
            <div style="font-weight: 700; color: #B45309; font-size: 14px;">Không tìm thấy bảng biểu</div>
            <div style="color: #92400E; font-size: 13px; margin-top: 2px;">
                Tài liệu PDF này không chứa bảng biểu có khung viền rõ ràng hoặc tài liệu là dạng ảnh scan chưa được kẻ bảng vector.
            </div>
        </div>
        """, unsafe_allow_html=True)
