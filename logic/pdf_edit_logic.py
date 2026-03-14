# Trong logic/pdf_utils.py (hoặc logic/pdf_edit_logic.py)
import fitz # PyMuPDF
import io
from PIL import Image, ImageDraw, ImageFont # Cho việc thêm text watermark/overlay
import math

# ... (các hàm merge_pdfs, split_pdf, parse_page_ranges, create_zip_from_files_data đã có) ...
# ... (các hàm add_text_watermark_to_pdf, add_image_watermark_to_pdf đã có) ...

def manipulate_pdf_pages(
    pdf_bytes: bytes,
    pages_to_delete: list[int] = None, # list các số trang 0-indexed để xóa
    page_rotations: dict[int, int] = None, # dict {page_num_0_idx: angle (0, 90, 180, 270)}
    new_page_order: list[int] = None, # list 0-indexed của thứ tự trang mới
    insert_blank_after: dict[int, tuple] = None # dict {page_num_0_idx_to_insert_after: (width, height)}
                                                # page_num -1 để chèn vào đầu, len(doc) để chèn vào cuối
) -> bytes:
    """
    Thực hiện các thao tác xóa, xoay, sắp xếp lại trang, chèn trang trắng.
    LƯU Ý: Các thao tác được thực hiện theo thứ tự: delete, rotate, reorder, insert blank.
    """
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")

        # 1. Xóa trang (thực hiện từ chỉ số cao đến thấp để tránh lỗi index)
        if pages_to_delete:
            # Sắp xếp các trang cần xóa theo thứ tự giảm dần
            for page_num_0_idx in sorted(list(set(pages_to_delete)), reverse=True):
                if 0 <= page_num_0_idx < len(doc):
                    doc.delete_page(page_num_0_idx)
                else:
                    print(f"Cảnh báo: Số trang {page_num_0_idx + 1} không hợp lệ để xóa.")
        
        # Cập nhật lại số trang sau khi xóa
        current_num_pages = len(doc)
        if current_num_pages == 0 and (page_rotations or new_page_order or insert_blank_after):
             # Nếu xóa hết trang mà vẫn còn thao tác khác thì có thể là lỗi logic người dùng
             print("Cảnh báo: PDF không còn trang nào sau khi xóa, không thể thực hiện các thao tác khác.")
             # Hoặc raise ValueError("PDF không còn trang sau khi xóa.")
             # Trong trường hợp này, các thao tác sau sẽ tự động không làm gì hoặc lỗi nếu doc rỗng.

        # 2. Xoay trang
        if page_rotations:
            for page_num_0_idx, angle in page_rotations.items():
                if 0 <= page_num_0_idx < len(doc) and angle in [0, 90, 180, 270]:
                    doc[page_num_0_idx].rotate(angle)
                else:
                    print(f"Cảnh báo: Số trang {page_num_0_idx + 1} hoặc góc xoay {angle} không hợp lệ.")
        
        # 3. Sắp xếp lại trang (tạo tài liệu mới)
        if new_page_order:
            # Validate new_page_order: phải chứa đủ các trang còn lại và không có trang thừa/trùng
            if len(new_page_order) == len(doc) and all(0 <= p < len(doc) for p in new_page_order) and len(set(new_page_order)) == len(doc):
                temp_doc = fitz.open()
                # new_page_order là list các chỉ số 0-indexed của trang gốc theo thứ tự mới
                temp_doc.insert_pdf(doc, from_page=0, to_page=len(doc)-1, pages=new_page_order) # Nếu PyMuPDF mới
                # Nếu PyMuPDF cũ không có tham số 'pages':
                # for original_page_idx in new_page_order:
                #    temp_doc.insert_page(doc.load_page(original_page_idx))
                doc.close() # Đóng doc cũ
                doc = temp_doc # doc giờ là tài liệu đã sắp xếp lại
            else:
                print(f"Cảnh báo: Thứ tự trang mới không hợp lệ. Số trang: {len(doc)}, thứ tự yêu cầu: {new_page_order}")


        # 4. Chèn trang trắng
        if insert_blank_after:
            # Sắp xếp các vị trí chèn để xử lý đúng (nếu chèn từ cuối lên đầu thì index không bị ảnh hưởng)
            # Hoặc chèn và cập nhật lại số trang. Cách đơn giản là xử lý theo thứ tự tăng dần của vị trí chèn.
            # Khi chèn, các trang sau sẽ bị đẩy xuống, nên cần cẩn thận với chỉ số.
            # Để an toàn hơn, có thể tạo doc mới khi có nhiều thao tác chèn.
            # Tuy nhiên, để đơn giản, chèn trực tiếp.
            # Ví dụ: insert_blank_after = {-1: (w,h), 2: (w,h)}
            # -1 nghĩa là chèn ở đầu, 0 là sau trang 1 (index 0), len(doc) là chèn ở cuối.
            
            # Thực hiện chèn theo thứ tự tăng dần của page_num_0_idx_to_insert_after
            # Điều này sẽ làm thay đổi chỉ số các trang sau đó, nhưng PyMuPDF insert_page xử lý việc này.
            for page_idx_after, (width, height) in sorted(insert_blank_after.items()):
                # PyMuPDF: new_page(pno=-1, width=width, height=height)
                # pno – where to insert the page. Values -1, doc.page_count mean append. pno=0 means insert as first page.
                insert_at_pno = page_idx_after + 1 # Nếu page_idx_after là 0-index, chèn sau nó là ở vị trí pno = index + 1
                if page_idx_after == -1: # Chèn ở đầu
                    insert_at_pno = 0
                # Nếu page_idx_after là vị trí cuối cùng, nó sẽ append
                
                if 0 <= insert_at_pno <= len(doc): # Đảm bảo pno hợp lệ
                     doc.new_page(pno=insert_at_pno, width=width, height=height)
                elif insert_at_pno > len(doc): # Append
                     doc.new_page(pno=-1, width=width, height=height)
                else:
                     print(f"Cảnh báo: Vị trí chèn trang trắng không hợp lệ: sau trang index {page_idx_after}")


        edited_pdf_bytes = doc.tobytes(garbage=4, deflate=True) # Bỏ linear=True
        return edited_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi biên tập trang PDF: {e}")
    finally:
        if doc:
            doc.close()

# Hàm add_text_to_page (tương tự như add_text_watermark nhưng có thể đơn giản hơn cho chú thích)
# Bạn có thể tái sử dụng hoặc tùy biến hàm add_text_watermark_to_pdf cho việc này.
# Để đơn giản, chúng ta có thể dùng lại add_text_watermark_to_pdf, coi việc thêm text là một dạng watermark.
# Hoặc tạo hàm mới nếu muốn các tùy chọn khác biệt rõ rệt.
# Ví dụ, hàm thêm text chú thích đơn giản:
def add_text_overlay_to_page(pdf_bytes: bytes, page_num_0_idx: int, text: str, 
                             rect_tuple: tuple, # (x0, y0, x1, y1)
                             fontname: str = "helv", fontsize: int = 11, 
                             color_tuple: tuple = (0,0,0), # đen
                             rotate: int = 0) -> bytes:
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        if not (0 <= page_num_0_idx < len(doc)):
            raise ValueError("Số trang không hợp lệ để thêm text.")
        
        page = doc.load_page(page_num_0_idx)
        rect = fitz.Rect(rect_tuple)
        # insert_textbox hỗ trợ xoay và nhiều tùy chọn hơn
        page.insert_textbox(rect, text, fontname=fontname, fontsize=fontsize, 
                            color=color_tuple, rotate=rotate, align=fitz.TEXT_ALIGN_LEFT)
        
        overlayed_pdf_bytes = doc.tobytes(garbage=4, deflate=True)
        return overlayed_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi thêm text overlay: {e}")
    finally:
        if doc:
            doc.close()