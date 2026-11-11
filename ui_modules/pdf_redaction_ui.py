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

def mask_for_ui(value):
    value = str(value)
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * max(3, len(value) - 4) + value[-2:]

def show_detection_report(report):
    if not report:
        return

    total = report.get("total", 0)
    summary = report.get("summary", {})
    findings = report.get("findings", [])

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: 700; font-size: 15px; color: #0F172A;">2. Kết quả Quét Thông tin Nhạy cảm (PII)</span>
            <span class="badge-soft-indigo">Scan Report</span>
        </div>
        """, unsafe_allow_html=True)

        if total == 0:
            st.info("Không phát hiện thông tin nhạy cảm nào theo các tiêu chí đã chọn.")
            return

        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span class="badge-soft-danger" style="font-size: 13px;">● Phát hiện {total} vị trí chứa thông tin cá nhân cần che</span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(min(4, max(1, len(summary))))
        for idx, (key, count) in enumerate(summary.items()):
            label = PII_PATTERNS.get(key, {}).get("label", key)
            with cols[idx % len(cols)]:
                st.metric(label, f"{count} mục")

        with st.expander("📋 Chi tiết danh sách thông tin nhạy cảm phát hiện", expanded=False):
            display_rows = []
            for item in findings:
                display_rows.append({
                    "Trang PDF": item.get("page", 1),
                    "Phân loại": item.get("label", "N/A"),
                    "Giá trị (Đã ẩn)": mask_for_ui(item.get("value", "")),
                })
            df = pd.DataFrame(display_rows)
            st.dataframe(df, use_container_width=True)

def show_final_report(report):
    if not report:
        return

    total = report.get("total_redacted", 0)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-weight: 700; font-size: 15px; color: #0F172A;">3. Kết quả Bảo mật (Redaction Summary)</span>
            <span class="badge-soft-success">Redacted</span>
        </div>
        """, unsafe_allow_html=True)

        if total == 0:
            st.warning("Không có vị trí nào được che. Có thể PDF là ảnh scan chưa có text layer hoặc pattern không khớp.")
        else:
            st.markdown(f"""
            <div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 10px 14px; font-size: 13.5px; color: #047857; margin-bottom: 8px;">
                ✓ <b>Thành công:</b> Đã loại bỏ hoàn toàn text nhị phân và che đen <b>{total}</b> vị trí nhạy cảm.
            </div>
            """, unsafe_allow_html=True)

def show_pdf_redaction_ui():
    init_redaction_state()

    # SaaS Header
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
        <div>
            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                <span class="badge-soft-indigo">Privacy & Security</span>
                <span class="badge-soft-success">Deep Redaction Engine</span>
            </div>
            <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em; color: #0F172A;">Redaction AI - Che Thông tin Nhạy cảm</h2>
            <p style="color: #475569; font-size: 14px; margin: 4px 0 0 0;">
                Tự động dò quét và xóa bỏ vĩnh viễn dữ liệu định danh cá nhân (Email, SĐT, CCCD, MST, Tài khoản) khỏi luồng nhị phân PDF.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Tải lên tập tin PDF cần bảo vệ:",
        type=["pdf"],
        key="redaction_pdf_uploader",
        help="Hỗ trợ các tài liệu hợp đồng, hồ sơ nhân sự, hóa đơn cần ẩn thông tin trước khi chia sẻ."
    )

    if not uploaded_file:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 2.5rem 1.5rem; text-align: center; margin-top: 1rem;">
            <div style="font-size: 32px; margin-bottom: 8px;">🛡️</div>
            <div style="font-weight: 700; color: #0F172A; font-size: 15px;">Chưa có tài liệu PDF nào được tải lên</div>
            <div style="color: #64748B; font-size: 13.5px; max-width: 460px; margin: 4px auto 0 auto;">
                Tải lên tập tin PDF để hệ thống tự động nhận diện các mẫu thông tin bảo mật và bôi đen an toàn tuyệt đối.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if uploaded_file.name != st.session_state.redaction_last_filename:
        reset_redaction_state(uploaded_file.name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(uploaded_file.read())
            st.session_state.redaction_input_path = tmp_in.name

    input_path = st.session_state.redaction_input_path
    if not input_path or not os.path.exists(input_path):
        st.error("Lỗi phiên làm việc với tệp PDF. Vui lòng tải lại.")
        return

    # Khung tùy chọn che
    with st.container(border=True):
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: 700; font-size: 14px; color: #0F172A;">1. Lựa chọn Thông tin cần Bảo mật</span>
            <span class="badge-soft-neutral">Filter Criteria</span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            redact_email = st.checkbox("📧 Địa chỉ Email", value=True)
            redact_phone = st.checkbox("📞 Số điện thoại (VN)", value=True)
        with col2:
            redact_id = st.checkbox("🆔 CCCD / CMND", value=True)
            redact_tax = st.checkbox("💼 Mã số thuế (MST)", value=True)
        with col3:
            redact_bank = st.checkbox("💳 Số tài khoản ngân hàng", value=False)
            redact_dob = st.checkbox("📅 Ngày sinh / Ngày tháng", value=False)

        items = []
        if redact_email: items.append("email")
        if redact_phone: items.append("phone")
        if redact_id: items.append("id_card")
        if redact_tax: items.append("tax_code")
        if redact_bank: items.append("bank_account")
        if redact_dob: items.append("date_of_birth")

        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            fill_option = st.selectbox("Màu sắc vùng che:", ["Đen", "Trắng", "Xám"], index=0)
        with c_opt2:
            preview_page = st.number_input("Trang hiển thị xem trước:", min_value=1, value=1, step=1)

        color_map = {
            "Đen": (0, 0, 0),
            "Trắng": (1, 1, 1),
            "Xám": (0.5, 0.5, 0.5),
        }
        fill_color = color_map[fill_option]

        col_detect, col_redact = st.columns(2)
        with col_detect:
            detect_clicked = st.button("🔍 Quét Thử Thông Tin Nhạy Cảm", use_container_width=True)
        with col_redact:
            redact_clicked = st.button("🚀 Thực hiện Che & Tạo PDF Bảo mật", type="primary", use_container_width=True)

    if not items:
        st.warning("Vui lòng chọn ít nhất một loại thông tin để tiến hành xử lý.")
        return

    if detect_clicked:
        with st.spinner("Đang quét các biểu thức PII trong văn bản PDF..."):
            try:
                report = detect_pii_in_pdf(input_path, items)
                st.session_state.redaction_detect_report = report
            except Exception as e:
                st.error(f"Lỗi khi quét PDF: {e}")

    show_detection_report(st.session_state.redaction_detect_report)

    if redact_clicked:
        with st.status("Đang thực hiện che dữ liệu vĩnh viễn (Redaction)...", expanded=True) as status:
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
                status.update(label="✓ Đã hoàn tất bảo mật tài liệu!", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Lỗi xử lý redaction: {e}")

    show_final_report(st.session_state.redaction_final_report)

    # Hiển thị Tải Về & Đối Chiếu Trước / Sau
    if st.session_state.redaction_output_path and os.path.exists(st.session_state.redaction_output_path):
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 700; font-size: 15px; color: #0F172A;">4. Tải xuống Tập tin & Xem trước Đối chiếu</span>
                <span class="badge-soft-success">● Đã sẵn sàng</span>
            </div>
            """, unsafe_allow_html=True)

            col_pdf, col_json = st.columns(2)
            with col_pdf:
                with open(st.session_state.redaction_output_path, "rb") as f:
                    st.download_button(
                        "📥 Tải xuống PDF Đã Bảo Mật",
                        f,
                        file_name=f"redacted_{uploaded_file.name}",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
            with col_json:
                if st.session_state.redaction_report_path and os.path.exists(st.session_state.redaction_report_path):
                    with open(st.session_state.redaction_report_path, "rb") as f:
                        st.download_button(
                            "🧾 Tải Báo cáo Kiểm toán JSON",
                            f,
                            file_name=f"audit_redaction_{Path(uploaded_file.name).stem}.json",
                            mime="application/json",
                            use_container_width=True
                        )

            # Bản xem trước đối chiếu 2 cột Trước / Sau
            try:
                before_img = render_pdf_page_to_png_bytes(input_path, page_number=int(preview_page))
                after_img = render_pdf_page_to_png_bytes(st.session_state.redaction_output_path, page_number=int(preview_page))

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                col_b, col_a = st.columns(2, gap="medium")
                with col_b:
                    st.markdown(f"**Bản gốc (Trang {preview_page}):**")
                    st.image(before_img, use_container_width=True)
                with col_a:
                    st.markdown(f"**Sau khi che mật (Trang {preview_page}):**")
                    st.image(after_img, use_container_width=True)
            except Exception as e:
                st.caption(f"Xem trước không khả dụng: {e}")
