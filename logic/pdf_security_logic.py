# logic/pdf_security_logic.py
import fitz  # PyMuPDF
import io

# Giá trị số nguyên cho các quyền PDF tiêu chuẩn (dùng làm fallback nếu hằng số fitz không có)
# Các giá trị này dựa trên đặc tả PDF.
PERM_PRINT = 4
PERM_MODIFY = 8        # Sửa nội dung (khác với chú thích/form)
PERM_COPY = 16         # Sao chép text/hình ảnh
PERM_ANNOTATE = 32     # Sửa chú thích
PERM_FILL_FORM = 256   # Điền form tương tác
PERM_ACCESSIBILITY = 512 # Sao chép cho mục đích hỗ trợ tiếp cận
PERM_ASSEMBLE = 1024   # Lắp ráp tài liệu (thêm, xóa, xoay trang)
PERM_PRINT_HQ = 2048   # In chất lượng cao

def unlock_pdf(pdf_bytes: bytes, password: str = "") -> bytes:
    """
    Mở khóa PDF. Nếu có mật khẩu người dùng, nó phải được cung cấp.
    Hàm này sẽ cố gắng loại bỏ cả mật khẩu người dùng và mật khẩu chủ sở hữu (hạn chế).
    """
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        
        if doc.is_encrypted:
            authenticated = doc.authenticate(password)
            if not authenticated:
                if password:
                    raise ValueError("Mật khẩu không đúng. Không thể mở khóa PDF.")
                else:
                    raise ValueError("PDF này được bảo vệ bằng mật khẩu mở file. Vui lòng cung cấp mật khẩu.")
            # print("DEBUG: PDF unlock - PDF đã xác thực.")
        # else:
            # print("DEBUG: PDF unlock - PDF không được mã hóa ban đầu.")

        # Tạo một tài liệu mới để sao chép nội dung đã giải mã
        # Điều này đảm bảo rằng chúng ta đang làm việc với một bản sao sạch.
        unlocked_doc = fitz.open()
        unlocked_doc.insert_pdf(doc) # Sao chép tất cả các trang
        
        # Lưu tài liệu mới không mã hóa và với TẤT CẢ CÁC QUYỀN được bật
        unlocked_pdf_bytes = unlocked_doc.tobytes(
            encryption=fitz.PDF_ENCRYPT_NONE,
            permissions=-1,  # -1 có nghĩa là cấp tất cả các quyền
            garbage=4, 
            deflate=True
            # linear=True đã bị loại bỏ
        )
        unlocked_doc.close()
        return unlocked_pdf_bytes

    except Exception as e:
        if "bad password" in str(e).lower() or "encrypted pdf" in str(e).lower():
            raise ValueError("Mật khẩu không đúng hoặc file PDF được mã hóa mạnh và không thể mở khóa bằng mật khẩu này.")
        # print(f"DEBUG: Lỗi chi tiết khi mở khóa: {type(e).__name__} - {e}") # Để debug nếu cần
        raise ValueError(f"Lỗi khi mở khóa PDF: {e}")
    finally:
        if doc:
            doc.close()


def protect_pdf(
    pdf_bytes: bytes, 
    user_password: str = None, 
    owner_password: str = None, 
    allow_print: bool = True,
    allow_copy: bool = True,
    allow_modify: bool = False,
    allow_annotate_forms: bool = False,
    allow_assemble: bool = False,
    encryption_method: int = fitz.PDF_ENCRYPT_AES_256
) -> bytes:
    """
    Bảo vệ PDF bằng mật khẩu người dùng, mật khẩu chủ sở hữu và các quyền hạn chế.
    """
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")

        # Xây dựng giá trị permissions integer
        # Luôn cho phép accessibility theo khuyến nghị
        perm = getattr(fitz, 'PDF_PERM_ACCESSIBILITY', PERM_ACCESSIBILITY)
        
        if allow_print:
            perm_print = getattr(fitz, 'PDF_PERM_PRINT', PERM_PRINT)
            perm_print_hq = getattr(fitz, 'PDF_PERM_PRINT_HQ', PERM_PRINT_HQ)
            perm |= perm_print | perm_print_hq
        if allow_copy:
            perm |= getattr(fitz, 'PDF_PERM_COPY', PERM_COPY)
        if allow_modify:
            perm |= getattr(fitz, 'PDF_PERM_MODIFY', PERM_MODIFY)
        if allow_annotate_forms:
            perm_annotate = getattr(fitz, 'PDF_PERM_ANNOTATE', PERM_ANNOTATE)
            perm_fill_form = getattr(fitz, 'PDF_PERM_FILL_FORM', PERM_FILL_FORM) 
            perm |= perm_annotate | perm_fill_form
        if allow_assemble:
            perm |= getattr(fitz, 'PDF_PERM_ASSEMBLE', PERM_ASSEMBLE)

        current_encryption = encryption_method
        # Nếu không đặt mật khẩu nào và cũng không hạn chế quyền nào đáng kể (ngoài mặc định)
        # thì không cần mã hóa. Tuy nhiên, nếu có hạn chế quyền, nên có owner_password.
        # Để đơn giản, nếu không có user_password VÀ owner_password, sẽ không mã hóa.
        if not user_password and not owner_password:
            current_encryption = fitz.PDF_ENCRYPT_NONE
            # Nếu chỉ đặt quyền mà không có mật khẩu, một số trình xem có thể không tuân thủ chặt chẽ.
            # Để bảo vệ quyền hiệu quả, owner_password nên được đặt.
            # Nếu người dùng không đặt owner_password nhưng đặt user_password, 
            # PyMuPDF sẽ ngầm dùng user_password làm owner_password.

        # Tạo bản sao để áp dụng bảo vệ
        protected_doc = fitz.open()
        protected_doc.insert_pdf(doc)

        protected_pdf_bytes = protected_doc.tobytes(
            encryption=current_encryption,
            owner_pw=owner_password if owner_password else (user_password if user_password else None), # Đảm bảo owner_pw có nếu user_pw có
            user_pw=user_password if user_password else None,
            permissions=perm,
            garbage=4,
            deflate=True
            # linear=True đã bị loại bỏ
        )
        protected_doc.close()
        return protected_pdf_bytes

    except Exception as e:
        # print(f"DEBUG: Lỗi chi tiết khi bảo vệ: {type(e).__name__} - {e}") # Để debug nếu cần
        raise ValueError(f"Lỗi khi bảo vệ PDF: {e}")
    finally:
        if doc:
            doc.close()