# ui_modules/version_manager_ui.py
import streamlit as st
import json
from datetime import datetime
import os # Cần cho os.path.exists

# Import các hàm logic từ thư mục logic
from logic.version_manager_logic import (
    save_version, list_versions, load_version, restore_version,
    get_doc_versions_path # Có thể cần để kiểm tra
)
# Các hàm xử lý chung nếu cần phân tích khi lưu version
from logic.common_processing import convert_pdf_to_txt, process_document_for_main_smartdoc
import asyncio # Cho process_document_for_main_smartdoc
from ui_utils.fun_meme import display_random_meme


def show_version_manager_ui(api_key_for_analysis):
    st.markdown("<h1 style='text-align: center;'>🗂️ Quản lý Phiên bản Tài liệu</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Lưu trữ, theo dõi, xem lại và phục hồi các phiên bản khác nhau của tài liệu quan trọng.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Session state cho module này
    if 'vm_doc_id' not in st.session_state: st.session_state.vm_doc_id = ""
    if 'vm_versions_list' not in st.session_state: st.session_state.vm_versions_list = []
    if 'vm_selected_version_data' not in st.session_state: st.session_state.vm_selected_version_data = None
    if 'vm_new_version_metadata' not in st.session_state: st.session_state.vm_new_version_metadata = "{}" # Default là JSON rỗng


    st.subheader("📁 Chọn hoặc Nhập ID Tài liệu")
    doc_id_input = st.text_input(
        "ID Tài liệu:",
        value=st.session_state.vm_doc_id,
        key="vm_doc_id_input",
        placeholder="Ví dụ: hop_dong_abc, bao_cao_q1_2025",
        help="ID này dùng để nhóm các phiên bản. Nên đặt tên không dấu, không khoảng trắng."
    )
    st.session_state.vm_doc_id = doc_id_input.strip()


    if st.session_state.vm_doc_id:
        # Cập nhật danh sách phiên bản khi doc_id thay đổi hoặc có hành động lưu/xóa
        # (Hiện chưa có xóa, chỉ có lưu sẽ làm thay đổi)
        try:
            st.session_state.vm_versions_list = list_versions(st.session_state.vm_doc_id)
        except Exception as e_list:
            st.error(f"Lỗi khi tải danh sách phiên bản: {e_list}")
            st.session_state.vm_versions_list = []


        tab_view, tab_new = st.tabs(["📜 Xem & Phục hồi Phiên bản", "➕ Lưu Phiên bản Mới"])

        with tab_view:
            st.subheader(f"Các Phiên bản của Tài liệu: `{st.session_state.vm_doc_id}`")
            if st.session_state.vm_versions_list:
                selected_version_id = st.selectbox(
                    "Chọn phiên bản:",
                    options=st.session_state.vm_versions_list,
                    key="vm_select_version_dropdown",
                    help="Các phiên bản được sắp xếp từ mới nhất đến cũ nhất."
                )

                if selected_version_id:
                    if st.button("🔍 Xem Chi tiết Phiên bản", key="vm_load_version_button", use_container_width=True):
                        with st.spinner(f"Đang tải chi tiết phiên bản {selected_version_id}..."):
                            try:
                                st.session_state.vm_selected_version_data = load_version(st.session_state.vm_doc_id, selected_version_id)
                            except FileNotFoundError:
                                st.error(f"Không tìm thấy dữ liệu cho phiên bản {selected_version_id}.")
                                st.session_state.vm_selected_version_data = None
                            except Exception as e_load:
                                st.error(f"Lỗi khi tải phiên bản: {e_load}")
                                st.session_state.vm_selected_version_data = None
                    
                    if st.session_state.vm_selected_version_data and st.session_state.vm_selected_version_data.get("metadata"):
                        data = st.session_state.vm_selected_version_data
                        with st.container(border=True):
                            st.markdown(f"#### Chi tiết Phiên bản: `{selected_version_id}`")
                            
                            # Hiển thị metadata
                            st.write("**Thông tin Metadata:**")
                            meta_display = data.get("metadata", {})
                            # Bỏ các key nội bộ khỏi hiển thị trực tiếp
                            meta_to_show = {k: v for k, v in meta_display.items() if not k.startswith('_')}
                            st.json(meta_to_show if meta_to_show else {"message": "Không có metadata tùy chỉnh."})

                            # Hiển thị thông tin phân tích nếu có
                            if data.get("analysis"):
                                with st.expander("Kết quả Phân tích AI (nếu có)"):
                                    st.json(data["analysis"])
                            
                            # Nút tải và phục hồi
                            col_dl, col_restore = st.columns(2)
                            pdf_path_for_dl = data.get("pdf_path")

                            if pdf_path_for_dl and os.path.exists(pdf_path_for_dl):
                                with col_dl:
                                    with open(pdf_path_for_dl, "rb") as fp:
                                        st.download_button(
                                            label=f"📥 Tải PDF Phiên bản này",
                                            data=fp,
                                            file_name=data.get("metadata",{}).get("_pdf_filename", f"{st.session_state.vm_doc_id}_{selected_version_id}.pdf"),
                                            mime="application/pdf",
                                            key=f"vm_download_{selected_version_id}",
                                            use_container_width=True
                                        )
                                with col_restore:
                                    if st.button(f"🔄 Phục hồi Phiên bản này", key=f"vm_restore_btn_{selected_version_id}", type="primary", use_container_width=True):
                                        restore_base = os.path.join(".", "restored_documents") # Lưu vào thư mục con của thư mục hiện tại
                                        try:
                                            restored_file_path = restore_version(st.session_state.vm_doc_id, selected_version_id, restore_base_path=restore_base)
                                            st.success(f"Đã phục hồi phiên bản thành công! File được lưu tại: `{restored_file_path}`")
                                        except FileNotFoundError:
                                            st.error("Lỗi: Không tìm thấy file PDF gốc của phiên bản để phục hồi.")
                                        except IOError as ioe:
                                            st.error(f"Lỗi I/O khi phục hồi: {ioe}")
                                        except Exception as e_restore:
                                            st.error(f"Lỗi không mong muốn khi phục hồi: {e_restore}")
                            else:
                                st.warning(f"Không tìm thấy file PDF cho phiên bản này ({pdf_path_for_dl}). Không thể tải hoặc phục hồi.")
            else:
                st.info("Chưa có phiên bản nào được lưu cho ID tài liệu này. Hãy chuyển qua tab 'Lưu Phiên bản Mới'.")

        with tab_new:
            st.subheader("➕ Lưu một Phiên bản Mới cho Tài liệu")
            st.caption(f"Sẽ được lưu cho ID Tài liệu: `{st.session_state.vm_doc_id}`")

            uploaded_file_for_new_version = st.file_uploader(
                "Tải lên file PDF cho phiên bản mới:",
                type="pdf",
                key="vm_new_version_file_uploader",
                help="File PDF này sẽ được lưu làm một phiên bản mới."
            )
            
            st.session_state.vm_new_version_metadata = st.text_area(
                "Thông tin Metadata (định dạng JSON):",
                value=st.session_state.vm_new_version_metadata,
                key="vm_metadata_text_area",
                height=150,
                placeholder='Ví dụ: {"ghi_chu": "Bản đệ trình lần cuối", "nguoi_cap_nhat": "user_xyz"}'
            )

            run_ai_analysis_for_new_version = False
            if api_key_for_analysis: # Chỉ hiện checkbox nếu có API key
                run_ai_analysis_for_new_version = st.checkbox(
                    "Chạy phân tích AI cơ bản cho phiên bản này?",
                    value=False,
                    key="vm_run_ai_checkbox",
                    help="Nếu chọn, hệ thống sẽ trích xuất entities, summary, classification cho phiên bản này."
                )

            if st.button("💾 Lưu Phiên bản Mới", type="primary", use_container_width=True, key="vm_save_new_version_button", disabled=not uploaded_file_for_new_version):
                if not uploaded_file_for_new_version:
                    st.warning("Vui lòng tải lên file PDF cho phiên bản mới.")
                else:
                    file_data_new_vm = uploaded_file_for_new_version.read()
                    analysis_res_new_vm = {}
                    
                    try:
                        metadata_input_dict = json.loads(st.session_state.vm_new_version_metadata)
                        if not isinstance(metadata_input_dict, dict):
                            st.error("Metadata phải là một đối tượng JSON hợp lệ.")
                            return # Dừng nếu metadata không phải dict
                    except json.JSONDecodeError:
                        st.error("Metadata không phải là JSON hợp lệ. Vui lòng kiểm tra lại.")
                        return # Dừng nếu metadata lỗi
                    
                    # Thêm thông tin file tự động vào metadata
                    metadata_input_dict["original_filename"] = uploaded_file_for_new_version.name
                    metadata_input_dict["file_size_bytes"] = uploaded_file_for_new_version.size
                    metadata_input_dict["saved_by_user_at"] = str(datetime.now())


                    if run_ai_analysis_for_new_version and api_key_for_analysis:
                        with st.spinner("Đang phân tích AI cho phiên bản mới (có thể mất vài phút)..."):
                            try:
                                text_for_ai_new_vm = convert_pdf_to_txt(file_data_new_vm)
                                if text_for_ai_new_vm.strip():
                                    entities, relationships, summary, classification = asyncio.run(
                                        process_document_for_main_smartdoc(api_key_for_analysis, text_for_ai_new_vm)
                                    )
                                    analysis_res_new_vm = {
                                        "entities": entities, "relationships": relationships,
                                        "summary": summary, "classification": classification,
                                        "analysis_run_at": str(datetime.now())
                                    }
                                    st.success("Phân tích AI cho phiên bản mới hoàn tất.")
                                else:
                                    st.warning("Không trích xuất được văn bản từ PDF mới để phân tích AI.")
                            except ValueError as ve_ai: # Lỗi từ logic AI (vd API key)
                                st.error(f"Lỗi cấu hình AI khi phân tích phiên bản mới: {ve_ai}")
                            except Exception as e_ai_vm:
                                st.error(f"Lỗi không mong muốn khi AI phân tích phiên bản mới: {e_ai_vm}")
                    elif run_ai_analysis_for_new_version and not api_key_for_analysis:
                        st.warning("API Key chưa được cấu hình. Không thể chạy phân tích AI cho phiên bản mới.")

                    try:
                        saved_version_path = save_version(
                            st.session_state.vm_doc_id,
                            file_data_new_vm,
                            metadata_input_dict,
                            analysis_res_new_vm if analysis_res_new_vm else None
                        )
                        st.success(f"Đã lưu phiên bản mới thành công! Chi tiết tại: `{saved_version_path}`")
                        st.info("Danh sách phiên bản sẽ được cập nhật sau khi bạn chọn lại ID Tài liệu hoặc làm mới trang.")
                        # Cập nhật lại danh sách version để người dùng thấy ngay
                        st.session_state.vm_versions_list = list_versions(st.session_state.vm_doc_id)
                        st.session_state.vm_new_version_metadata = "{}" # Reset metadata input
                        # Cân nhắc st.rerun() để làm mới hoàn toàn tab
                    except ValueError as ve_save: # Lỗi từ logic save (vd doc_id trống)
                        st.error(f"Lỗi khi lưu phiên bản: {ve_save}")
                    except Exception as e_save:
                        st.error(f"Lỗi không mong muốn khi lưu phiên bản mới: {e_save}")
            st.markdown("---")
            if uploaded_file_for_new_version: #Chỉ hiện meme sau khi có hành động với file
                 display_random_meme()
    else:
        st.info("Vui lòng nhập một ID Tài liệu ở trên để bắt đầu quản lý các phiên bản của nó.")