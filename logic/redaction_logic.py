# # logic/redaction_logic.py
# import fitz  # PyMuPDF
# import re
# import os

# def redact_pdf(input_path, output_path, items_to_redact):
#     """
#     Che thông tin nhạy cảm trong PDF.
#     items_to_redact: List các loại cần che ['email', 'phone', 'id_card']
#     """
#     doc = fitz.open(input_path)
    
#     # Định nghĩa các Regex Pattern (Mẫu nhận diện) cho Việt Nam
#     patterns = {
#         "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
#         # SĐT Việt Nam: Bắt đầu bằng 0, theo sau là 9 chữ số (tổng 10 số), chấp nhận dấu cách hoặc chấm
#         "phone": r'(?:\+84|0)[3|5|7|8|9][0-9]{8}\b', 
#         # CCCD/CMND: 9 hoặc 12 chữ số liên tiếp
#         "id_card": r'\b\d{9}\b|\b\d{12}\b' 
#     }

#     count = 0 # Đếm số lượng chỗ đã che

#     for page in doc:
#         # Lấy toàn bộ text trên trang để quét regex
#         text = page.get_text("text")
        
#         for item_type in items_to_redact:
#             if item_type in patterns:
#                 # 1. Tìm tất cả các chuỗi khớp với pattern (VD: tìm ra "0901234567")
#                 matches = re.findall(patterns[item_type], text)
                
#                 for match in matches:
#                     # 2. Tìm tọa độ (Bounding Box) của chuỗi đó trên trang PDF
#                     # quad là hình tứ giác bao quanh chữ
#                     quads = page.search_for(match)
                    
#                     for quad in quads:
#                         # 3. Thêm annotation (chú thích) loại Redaction
#                         # Fill màu đen (0, 0, 0)
#                         annot = page.add_redact_annot(quad)
#                         annot.set_colors(stroke=(0, 0, 0), fill=(0, 0, 0)) 
#                         annot.update()
#                         count += 1

#         # 4. Áp dụng che (Thực sự xóa text bên dưới lớp đen để không copy được)
#         page.apply_redactions()

#     doc.save(output_path)
#     doc.close()
#     return count

# logic/redaction_logic.py

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import fitz  # PyMuPDF


# ==========================
# REGEX PATTERNS
# ==========================

PII_PATTERNS = {
    "email": {
        "label": "Email",
        "pattern": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    },
    "phone": {
        "label": "Số điện thoại Việt Nam",
        # Bắt: 0912345678, +84912345678, 091 234 5678, 091.234.5678
        "pattern": r"\b(?:\+84|0)(?:3|5|7|8|9)(?:[\s.\-]?\d){8}\b",
    },
    "id_card": {
        "label": "CCCD/CMND",
        # CMND 9 số hoặc CCCD 12 số
        "pattern": r"\b(?:\d{9}|\d{12})\b",
    },
    "tax_code": {
        "label": "Mã số thuế",
        # MST 10 số hoặc 10-3
        "pattern": r"\b\d{10}(?:-\d{3})?\b",
    },
    "bank_account": {
        "label": "Số tài khoản ngân hàng",
        # Tương đối: chuỗi 8-16 chữ số
        "pattern": r"\b\d{8,16}\b",
    },
    "date_of_birth": {
        "label": "Ngày sinh/ngày tháng",
        "pattern": r"\b(?:0?[1-9]|[12]\d|3[01])[/\-](?:0?[1-9]|1[0-2])[/\-](?:19|20)\d{2}\b",
    },
}


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def get_selected_patterns(items_to_redact: List[str]) -> Dict[str, Dict[str, str]]:
    return {
        key: val
        for key, val in PII_PATTERNS.items()
        if key in items_to_redact
    }


# ==========================
# DETECT PII
# ==========================

def detect_pii_in_pdf(input_path: str, items_to_redact: List[str]) -> Dict[str, Any]:
    """
    Quét PDF và trả về danh sách PII tìm thấy.
    Chưa redact, chỉ detect để preview/report.
    """
    selected_patterns = get_selected_patterns(items_to_redact)

    doc = fitz.open(input_path)

    findings = []
    summary = {
        key: 0
        for key in selected_patterns.keys()
    }

    for page_index, page in enumerate(doc):
        text = page.get_text("text")

        if not text.strip():
            continue

        for pii_type, config in selected_patterns.items():
            pattern = config["pattern"]

            matches = re.finditer(pattern, text, flags=re.IGNORECASE)

            for match in matches:
                raw_value = match.group(0).strip()
                clean_value = normalize_spaces(raw_value)

                if not clean_value:
                    continue

                findings.append({
                    "page": page_index + 1,
                    "type": pii_type,
                    "label": config["label"],
                    "value": clean_value,
                })

                summary[pii_type] += 1

    doc.close()

    return {
        "total": len(findings),
        "summary": summary,
        "findings": findings,
    }


# ==========================
# REDACT PDF
# ==========================

def add_redaction_for_match(page, match_text: str, fill_color=(0, 0, 0)) -> int:
    """
    Tìm vị trí match_text trên page và thêm redaction annotation.
    Return số vị trí đã add.
    """
    count = 0

    variants = list(dict.fromkeys([
        match_text,
        normalize_spaces(match_text),
        match_text.replace(" ", ""),
        match_text.replace(".", ""),
        match_text.replace("-", ""),
    ]))

    for value in variants:
        if not value:
            continue

        rects = page.search_for(value)

        for rect in rects:
            annot = page.add_redact_annot(
                rect,
                fill=fill_color
            )
            annot.update()
            count += 1

        if count > 0:
            break

    return count


def redact_pdf(
    input_path: str,
    output_path: str,
    items_to_redact: List[str],
    fill_color=(0, 0, 0),
    replacement_text: str = "",
) -> Dict[str, Any]:
    """
    Redact thông tin nhạy cảm trong PDF có text layer.
    Return report dict thay vì chỉ return count.
    """
    selected_patterns = get_selected_patterns(items_to_redact)

    doc = fitz.open(input_path)

    report = {
        "total_redacted": 0,
        "pages": {},
        "items": [],
        "warnings": [],
    }

    for page_index, page in enumerate(doc):
        page_number = page_index + 1
        text = page.get_text("text")

        if not text.strip():
            report["warnings"].append(
                f"Trang {page_number} không có text layer. Nếu đây là PDF scan, cần OCR trước."
            )
            continue

        page_count = 0

        for pii_type, config in selected_patterns.items():
            pattern = config["pattern"]

            matches = re.finditer(pattern, text, flags=re.IGNORECASE)

            for match in matches:
                match_text = match.group(0).strip()

                if not match_text:
                    continue

                added = add_redaction_for_match(
                    page=page,
                    match_text=match_text,
                    fill_color=fill_color
                )

                if added > 0:
                    page_count += added
                    report["total_redacted"] += added

                    report["items"].append({
                        "page": page_number,
                        "type": pii_type,
                        "label": config["label"],
                        "value_masked": mask_value(match_text),
                        "positions": added,
                    })

        if page_count > 0:
            page.apply_redactions()

        report["pages"][str(page_number)] = page_count

    # Garbage + deflate giúp xóa object cũ và giảm dung lượng
    doc.save(
        output_path,
        garbage=4,
        deflate=True,
        clean=True
    )
    doc.close()

    return report


def mask_value(value: str) -> str:
    """
    Mask giá trị nhạy cảm trong report, không lưu full PII.
    """
    value = str(value)

    if len(value) <= 4:
        return "*" * len(value)

    return value[:2] + "*" * max(3, len(value) - 4) + value[-2:]


def save_redaction_report(report: Dict[str, Any], output_json_path: str):
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=4)


# ==========================
# PREVIEW
# ==========================

def render_pdf_page_to_png_bytes(pdf_path: str, page_number: int = 1, zoom: float = 1.5) -> bytes:
    """
    Render một trang PDF sang PNG bytes để preview Streamlit.
    """
    doc = fitz.open(pdf_path)

    page_index = max(0, page_number - 1)
    page_index = min(page_index, len(doc) - 1)

    page = doc.load_page(page_index)

    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    img_bytes = pix.tobytes("png")

    doc.close()

    return img_bytes