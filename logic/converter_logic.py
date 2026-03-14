# logic/converter_logic.py
import os
from PIL import Image
import img2pdf
from pdf2image import convert_from_path
from pdf2docx import Converter
# Lưu ý: docx2pdf cần MS Word cài trên máy Windows
try:
    from docx2pdf import convert as convert_word_to_pdf_lib
    WORD_TO_PDF_AVAILABLE = True
except:
    WORD_TO_PDF_AVAILABLE = False

# 1. ẢNH -> PDF
def images_to_pdf(image_files, output_path):
    # image_files là list các đường dẫn ảnh hoặc file object
    with open(output_path, "wb") as f:
        f.write(img2pdf.convert([i.read() for i in image_files]))
    return output_path

# 2. PDF -> ẢNH (Bạn đã có hàm này rồi, nhưng đây là wrapper để tải về)
def pdf_to_images_zip(pdf_path):
    # Hàm này sẽ trả về đường dẫn file ZIP chứa các ảnh
    # (Logic tạo ZIP bạn có thể tự viết thêm dùng thư viện zipfile)
    pass 

# 3. PDF -> WORD (Cực hay dùng)
def pdf_to_word(pdf_path, output_path):
    cv = Converter(pdf_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

# 4. WORD -> PDF
def word_to_pdf(docx_path, output_path):
    if WORD_TO_PDF_AVAILABLE:
        convert_word_to_pdf_lib(docx_path, output_path)
        return output_path
    else:
        return None