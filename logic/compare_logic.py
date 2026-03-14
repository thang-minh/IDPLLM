# logic/compare_logic.py
from PIL import Image
import pytesseract # Sẽ sử dụng pytesseract đã cấu hình ở app.py
import difflib
# Không cần import streamlit ở đây

def extract_text_from_image_for_compare(uploaded_file_bytes, lang='vie+eng'):
    """Extracts text from an uploaded image file (bytes) for comparison."""
    try:
        image = Image.open(uploaded_file_bytes)
        # Có thể thêm tiền xử lý ở đây nếu muốn, tương tự common_processing.preprocess_image_ocr
        return pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        raise ValueError(f"Lỗi OCR ảnh cho so sánh: {e}")


def compare_texts_to_html(text1: str, text2: str) -> str:
    """Compares two texts and returns an HTML table of differences."""
    if not isinstance(text1, str) or not isinstance(text2, str):
        return "<p>Lỗi: Đầu vào phải là chuỗi văn bản.</p>"
    
    # Thay thế ký tự xuống dòng thành list các dòng
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()
    
    differ = difflib.HtmlDiff(wrapcolumn=70) # wrapcolumn để dễ đọc hơn
    return differ.make_table(text1_lines, text2_lines, fromdesc='Tài liệu 1', todesc='Tài liệu 2')