# logic/redaction_logic.py
import fitz  # PyMuPDF
import re
import os

def redact_pdf(input_path, output_path, items_to_redact):
    """
    Che thông tin nhạy cảm trong PDF.
    items_to_redact: List các loại cần che ['email', 'phone', 'id_card']
    """
    doc = fitz.open(input_path)
    
    # Định nghĩa các Regex Pattern (Mẫu nhận diện) cho Việt Nam
    patterns = {
        "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        # SĐT Việt Nam: Bắt đầu bằng 0, theo sau là 9 chữ số (tổng 10 số), chấp nhận dấu cách hoặc chấm
        "phone": r'(?:\+84|0)[3|5|7|8|9][0-9]{8}\b', 
        # CCCD/CMND: 9 hoặc 12 chữ số liên tiếp
        "id_card": r'\b\d{9}\b|\b\d{12}\b' 
    }

    count = 0 # Đếm số lượng chỗ đã che

    for page in doc:
        # Lấy toàn bộ text trên trang để quét regex
        text = page.get_text("text")
        
        for item_type in items_to_redact:
            if item_type in patterns:
                # 1. Tìm tất cả các chuỗi khớp với pattern (VD: tìm ra "0901234567")
                matches = re.findall(patterns[item_type], text)
                
                for match in matches:
                    # 2. Tìm tọa độ (Bounding Box) của chuỗi đó trên trang PDF
                    # quad là hình tứ giác bao quanh chữ
                    quads = page.search_for(match)
                    
                    for quad in quads:
                        # 3. Thêm annotation (chú thích) loại Redaction
                        # Fill màu đen (0, 0, 0)
                        annot = page.add_redact_annot(quad)
                        annot.set_colors(stroke=(0, 0, 0), fill=(0, 0, 0)) 
                        annot.update()
                        count += 1

        # 4. Áp dụng che (Thực sự xóa text bên dưới lớp đen để không copy được)
        page.apply_redactions()

    doc.save(output_path)
    doc.close()
    return count