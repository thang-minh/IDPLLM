# # ui_modules/pdf_redaction_ui.py
# import streamlit as st
# import tempfile
# import os
# from logic.redaction_logic import redact_pdf
# import fitz # Để render ảnh preview

# def show_pdf_redaction_ui():
#     st.header("🛡️ Redaction AI - Che Thông tin Nhạy cảm")
#     st.markdown("Tự động phát hiện và che (bôi đen) các thông tin cá nhân (PII) như Email, SĐT, CCCD.")

#     uploaded_file = st.file_uploader("Tải file PDF cần xử lý", type=['pdf'])

#     if uploaded_file:
#         # Lưu file tạm
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
#             tmp_in.write(uploaded_file.read())
#             input_path = tmp_in.name

#         st.markdown("### ⚙️ Chọn thông tin cần che:")
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             redact_email = st.checkbox("📧 Email", value=True)
#         with col2:
#             redact_phone = st.checkbox("📞 Số điện thoại (VN)", value=True)
#         with col3:
#             redact_id = st.checkbox("🆔 CCCD / CMND", value=False)

#         if st.button("🚀 Thực hiện Bảo mật (Redact)", type="primary"):
#             # Tạo list các mục cần che
#             items = []
#             if redact_email: items.append("email")
#             if redact_phone: items.append("phone")
#             if redact_id: items.append("id_card")

#             if not items:
#                 st.warning("Vui lòng chọn ít nhất một loại thông tin để che.")
#             else:
#                 output_path = input_path.replace(".pdf", "_redacted.pdf")
                
#                 with st.spinner("Đang quét và xử lý bảo mật..."):
#                     try:
#                         # Gọi logic xử lý
#                         count = redact_pdf(input_path, output_path, items)
                        
#                         st.success(f"✅ Hoàn tất! Đã che **{count}** vị trí nhạy cảm.")
                        
#                         # Hiển thị nút tải về
#                         with open(output_path, "rb") as f:
#                             st.download_button(
#                                 "⬇️ Tải file đã bảo mật",
#                                 f,
#                                 file_name="secure_document.pdf",
#                                 mime="application/pdf"
#                             )
                        
#                         # --- PREVIEW (Xem trước trang đầu) ---
#                         st.markdown("---")
#                         st.markdown("### 👀 Xem trước kết quả (Trang 1)")
#                         doc = fitz.open(output_path)
#                         page = doc.load_page(0)
#                         pix = page.get_pixmap()
#                         st.image(pix.tobytes(), caption="Trang 1 sau khi che mật", use_column_width=True)
#                         doc.close()

#                     except Exception as e:
#                         st.error(f"Lỗi xử lý: {e}")

# ui_modules/pdf_redaction_ui.py

import os
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from logic.redaction_logic import (
    detect_pii_in_pdf,
    redact_pdf,
    save_redaction_report,
    render_pdf_page_to_png_bytes,
    PII_PATTERNS,
)


def init_redaction_state():
    defaults = {
        "redaction_detect_report": None,
        "redaction_final_report": None,
        "redaction_output_path": None,
        "redaction_report_path": None,
        "redaction_input_path": None,
        "redaction_last_filename": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_redaction_state(filename=None):
    st.session_state.redaction_detect_report = None
    st.session_state.redaction_final_report = None
    st.session_state.redaction_output_path = None
    st.session_state.redaction_report_path = None
    st.session_state.redaction_input_path = None
    st.session_state.redaction_last_filename = filename


def show_detection_report(report):
    if not report:
        return

    total = report.get("total", 0)
    summary = report.get("summary", {})
    findings = report.get("findings", [])

    st.subheader("2. Kết quả phát hiện thông tin nhạy cảm")

    if total == 0:
        st.info("Chưa phát hiện thông tin nhạy cảm theo các loại đã chọn.")
        return

    st.success(f"Phát hiện **{total}** thông tin nhạy cảm.")

    cols = st.columns(min(4, max(1, len(summary))))

    for idx, (key, count) in enumerate(summary.items()):
        label = PII_PATTERNS.get(key, {}).get("label", key)
        with cols[idx % len(cols)]:
            st.metric(label, count)

    with st.expander("Xem chi tiết thông tin phát hiện", expanded=False):
        display_rows = []

        for item in findings:
            display_rows.append({
                "Trang": item["page"],
                "Loại": item["label"],
                "Giá trị": mask_for_ui(item["value"]),
            })

        df = pd.DataFrame(display_rows)
        st.dataframe(df, use_container_width=True)


def mask_for_ui(value):
    value = str(value)

    if len(value) <= 4:
        return "*" * len(value)

    return value[:2] + "*" * max(3, len(value) - 4) + value[-2:]


def show_final_report(report):
    if not report:
        return

    st.subheader("3. Kết quả redaction")

    total = report.get("total_redacted", 0)

    if total == 0:
        st.warning("Không có vị trí nào được che. Có thể PDF không có text layer hoặc pattern không khớp.")
    else:
        st.success(f"Hoàn tất. Đã che **{total}** vị trí nhạy cảm.")

    warnings = report.get("warnings", [])

    if warnings:
        with st.expander("Cảnh báo", expanded=True):
            for warning in warnings:
                st.warning(warning)

    items = report.get("items", [])

    if items:
        with st.expander("Chi tiết vị trí đã che", expanded=False):
            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True)


def show_pdf_redaction_ui():
    init_redaction_state()

    st.header("Redaction AI - Che thông tin nhạy cảm")

    st.markdown(
        """
        Công cụ này giúp phát hiện và che thông tin nhạy cảm trong PDF như email, số điện thoại,
        CCCD/CMND, mã số thuế, số tài khoản và ngày sinh.  
        Redaction sẽ xóa text bên dưới vùng che, không chỉ vẽ một lớp màu đen lên trên.
        """
    )

    st.info(
        "Lưu ý: Chức năng này hoạt động tốt nhất với PDF có text layer. "
        "Nếu PDF là ảnh scan, cần OCR trước rồi mới xử lý chính xác hơn."
    )

    uploaded_file = st.file_uploader(
        "Tải file PDF cần bảo mật",
        type=["pdf"],
        key="redaction_pdf_uploader"
    )

    if not uploaded_file:
        st.info("Vui lòng tải lên một file PDF để bắt đầu.")
        return

    if uploaded_file.name != st.session_state.redaction_last_filename:
        reset_redaction_state(uploaded_file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(uploaded_file.read())
            st.session_state.redaction_input_path = tmp_in.name

    input_path = st.session_state.redaction_input_path

    if not input_path or not os.path.exists(input_path):
        st.error("Không tìm thấy file PDF tạm. Vui lòng upload lại.")
        return

    st.markdown("---")
    st.subheader("1. Chọn loại thông tin cần che")

    col1, col2, col3 = st.columns(3)

    with col1:
        redact_email = st.checkbox("Email", value=True)
        redact_phone = st.checkbox("Số điện thoại Việt Nam", value=True)

    with col2:
        redact_id = st.checkbox("CCCD / CMND", value=True)
        redact_tax = st.checkbox("Mã số thuế", value=False)

    with col3:
        redact_bank = st.checkbox("Số tài khoản ngân hàng", value=False)
        redact_dob = st.checkbox("Ngày sinh / ngày tháng", value=False)

    items = []

    if redact_email:
        items.append("email")
    if redact_phone:
        items.append("phone")
    if redact_id:
        items.append("id_card")
    if redact_tax:
        items.append("tax_code")
    if redact_bank:
        items.append("bank_account")
    if redact_dob:
        items.append("date_of_birth")

    st.markdown("### Tùy chọn che")

    col_color, col_preview = st.columns([1, 1])

    with col_color:
        fill_option = st.selectbox(
            "Màu che",
            ["Đen", "Trắng", "Xám"],
            index=0
        )

    color_map = {
        "Đen": (0, 0, 0),
        "Trắng": (1, 1, 1),
        "Xám": (0.5, 0.5, 0.5),
    }

    fill_color = color_map[fill_option]

    with col_preview:
        preview_page = st.number_input(
            "Trang preview",
            min_value=1,
            value=1,
            step=1
        )

    col_detect, col_redact = st.columns(2)

    with col_detect:
        detect_clicked = st.button(
            "Quét thông tin nhạy cảm",
            use_container_width=True
        )

    with col_redact:
        redact_clicked = st.button(
            "Che thông tin và tạo PDF bảo mật",
            type="primary",
            use_container_width=True
        )

    if not items:
        st.warning("Vui lòng chọn ít nhất một loại thông tin cần che.")
        return

    if detect_clicked:
        with st.spinner("Đang quét thông tin nhạy cảm trong PDF..."):
            try:
                report = detect_pii_in_pdf(input_path, items)
                st.session_state.redaction_detect_report = report
            except Exception as e:
                st.error(f"Lỗi khi quét PDF: {e}")

    show_detection_report(st.session_state.redaction_detect_report)

    if redact_clicked:
        with st.spinner("Đang thực hiện redaction..."):
            try:
                output_path = input_path.replace(".pdf", "_redacted.pdf")
                report_path = input_path.replace(".pdf", "_redaction_report.json")

                final_report = redact_pdf(
                    input_path=input_path,
                    output_path=output_path,
                    items_to_redact=items,
                    fill_color=fill_color,
                )

                save_redaction_report(final_report, report_path)

                st.session_state.redaction_output_path = output_path
                st.session_state.redaction_report_path = report_path
                st.session_state.redaction_final_report = final_report

            except Exception as e:
                st.error(f"Lỗi xử lý redaction: {e}")

    show_final_report(st.session_state.redaction_final_report)

    if st.session_state.redaction_output_path and os.path.exists(st.session_state.redaction_output_path):
        st.markdown("---")
        st.subheader("4. Tải kết quả")

        col_pdf, col_json = st.columns(2)

        with col_pdf:
            with open(st.session_state.redaction_output_path, "rb") as f:
                st.download_button(
                    "Tải PDF đã bảo mật",
                    f,
                    file_name=f"redacted_{uploaded_file.name}",
                    mime="application/pdf",
                    use_container_width=True
                )

        with col_json:
            if st.session_state.redaction_report_path and os.path.exists(st.session_state.redaction_report_path):
                with open(st.session_state.redaction_report_path, "rb") as f:
                    st.download_button(
                        "Tải báo cáo JSON",
                        f,
                        file_name=f"redaction_report_{Path(uploaded_file.name).stem}.json",
                        mime="application/json",
                        use_container_width=True
                    )

        st.markdown("---")
        st.subheader("5. Xem trước kết quả")

        try:
            before_img = render_pdf_page_to_png_bytes(
                input_path,
                page_number=int(preview_page)
            )

            after_img = render_pdf_page_to_png_bytes(
                st.session_state.redaction_output_path,
                page_number=int(preview_page)
            )

            col_before, col_after = st.columns(2)

            with col_before:
                st.image(
                    before_img,
                    caption=f"Trước redaction - Trang {preview_page}",
                    use_container_width=True
                )

            with col_after:
                st.image(
                    after_img,
                    caption=f"Sau redaction - Trang {preview_page}",
                    use_container_width=True
                )

        except Exception as e:
            st.warning(f"Không thể render preview: {e}")