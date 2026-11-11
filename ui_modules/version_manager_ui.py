# ui_modules/version_manager_ui.py
import streamlit as st
import json
import os
from datetime import datetime

from logic.version_manager_logic import (
    save_version, list_versions, load_version, restore_version,
)
from logic.common_processing import convert_pdf_to_txt
from ui_utils.fun_meme import display_random_meme
from ui_utils.ui_components import render_page_header, render_empty_state

def show_version_manager_ui(api_key_for_analysis):
    badges = [
        {"text": "● Version Control", "type": "indigo"},
        {"text": "Local Archive", "type": "neutral"},
    ]
    render_page_header(
        title="Document Storage & Version History",
        description="Lưu trữ an toàn, theo dõi tiến trình chỉnh sửa và phục hồi các phiên bản tài liệu quan trọng.",
        breadcrumb="AI DOCUMENT / DOCUMENT STORAGE",
        badges=badges
    )

    if 'vm_doc_id' not in st.session_state: st.session_state.vm_doc_id = ""
    if 'vm_versions_list' not in st.session_state: st.session_state.vm_versions_list = []
    if 'vm_selected_version_data' not in st.session_state: st.session_state.vm_selected_version_data = None
    if 'vm_new_version_metadata' not in st.session_state: st.session_state.vm_new_version_metadata = "{}"

    # Search & Selector Card
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 14px; color: #0F172A;">🔍 Tra cứu Hồ sơ Tài liệu</span>
            <span class="badge-soft-indigo">Document Index</span>
        </div>
        """, unsafe_allow_html=True)

        c_inp, c_quick = st.columns([2, 1])
        with c_inp:
            doc_id_input = st.text_input(
                "Mã định danh tài liệu (Document ID):",
                value=st.session_state.vm_doc_id,
                placeholder="Ví dụ: hop_dong_2025, hoa_don_thue_q1",
                help="Sử dụng mã không dấu để nhóm các phiên bản của cùng một văn bản."
            )
            st.session_state.vm_doc_id = doc_id_input.strip()

        with c_quick:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.caption("Các phiên bản được mã hóa và đánh số tự động theo tem thời gian.")

    if not st.session_state.vm_doc_id:
        render_empty_state(
            icon="🗂️",
            title="Chưa chọn mã tài liệu",
            description="Hãy nhập mã tài liệu (Document ID) ở trên để xem lịch sử phiên bản hoặc lưu trữ bản ghi mới."
        )
        return

    try:
        st.session_state.vm_versions_list = list_versions(st.session_state.vm_doc_id)
    except Exception as e_list:
        st.error(f"Lỗi tải danh sách phiên bản: {e_list}")
        st.session_state.vm_versions_list = []

    tab_view, tab_new = st.tabs(["📜 Lịch sử & Phục hồi Phiên bản", "➕ Lưu trữ Phiên bản Mới"])

    # TAB 1: VIEW & RESTORE
    with tab_view:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">Hồ sơ: <code>{st.session_state.vm_doc_id}</code></span>
                <span class="badge-soft-neutral">{len(st.session_state.vm_versions_list)} phiên bản đã lưu</span>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.vm_versions_list:
                selected_version_id = st.selectbox(
                    "Chọn phiên bản cần kiểm tra:",
                    options=st.session_state.vm_versions_list,
                    key="vm_select_version_dropdown"
                )

                if selected_version_id:
                    if st.button("🔍 Mở Bản ghi Phiên bản", key="vm_load_btn", type="primary", use_container_width=True):
                        try:
                            st.session_state.vm_selected_version_data = load_version(st.session_state.vm_doc_id, selected_version_id)
                        except Exception as e:
                            st.error(f"Lỗi đọc phiên bản: {e}")
                            st.session_state.vm_selected_version_data = None

                    if st.session_state.vm_selected_version_data:
                        v_data = st.session_state.vm_selected_version_data
                        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                        with st.container(border=True):
                            st.markdown(f"#### Chi tiết Phiên bản: `{selected_version_id}`")

                            c_v1, c_v2 = st.columns(2)
                            with c_v1:
                                st.markdown("**Metadata Hồ sơ:**")
                                meta = v_data.get("metadata", {})
                                clean_meta = {k: v for k, v in meta.items() if not str(k).startswith("_")}
                                st.json(clean_meta if clean_meta else {"info": "Không có metadata mở rộng."})

                            with c_v2:
                                if v_data.get("analysis"):
                                    st.markdown("**Kết quả Phân tích AI đính kèm:**")
                                    st.json(v_data["analysis"])

                            pdf_path = v_data.get("pdf_path")
                            if pdf_path and os.path.exists(pdf_path):
                                col_dl, col_res = st.columns(2)
                                with col_dl:
                                    with open(pdf_path, "rb") as fp:
                                        st.download_button(
                                            "📥 Tải PDF Phiên bản Này",
                                            fp,
                                            file_name=f"{st.session_state.vm_doc_id}_{selected_version_id}.pdf",
                                            mime="application/pdf",
                                            type="primary",
                                            use_container_width=True
                                        )
                                with col_res:
                                    if st.button("🔄 Phục hồi (Restore) Phiên bản Này", use_container_width=True):
                                        try:
                                            restored_file = restore_version(st.session_state.vm_doc_id, selected_version_id)
                                            st.success(f"✓ Đã phục hồi thành công tại: `{restored_file}`")
                                        except Exception as e_res:
                                            st.error(f"Lỗi phục hồi: {e_res}")
            else:
                st.info("Chưa có phiên bản nào được lưu trữ cho ID tài liệu này.")

    # TAB 2: SAVE NEW VERSION
    with tab_new:
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 14px; color: #0F172A;">Tải lên và Lưu phiên bản Mới</span>
                <span class="badge-soft-indigo">New Version</span>
            </div>
            """, unsafe_allow_html=True)

            up_file = st.file_uploader("Tập tin PDF phiên bản mới:", type=["pdf"], key="vm_new_pdf_file")
            cmt = st.text_input("Ghi chú thay đổi (Commit note):", placeholder="Ví dụ: Đã ký phụ lục hợp đồng, Sửa điều khoản thanh toán...")
            meta_json_str = st.text_area("Thuộc tính bổ sung (JSON Metadata):", value='{\n  "tac_gia": "Ke_toan",\n  "trang_thai": "Da_duyet"\n}', height=100)

            if up_file and st.button("💾 Lưu Trữ Phiên Bản Mới", type="primary", use_container_width=True):
                with st.spinner("Đang đóng gói và đánh chỉ mục phiên bản mới..."):
                    try:
                        meta_dict = json.loads(meta_json_str) if meta_json_str.strip() else {}
                        meta_dict["ghi_chu"] = cmt
                        meta_dict["thoi_gian"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        pdf_bytes = up_file.read()
                        new_ver_id = save_version(
                            doc_id=st.session_state.vm_doc_id,
                            pdf_bytes=pdf_bytes,
                            metadata=meta_dict
                        )
                        st.success(f"✓ Đã tạo thành công phiên bản mới: `{new_ver_id}`")
                        st.rerun()
                    except Exception as e_save:
                        st.error(f"Lỗi khi lưu phiên bản: {e_save}")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    display_random_meme()
