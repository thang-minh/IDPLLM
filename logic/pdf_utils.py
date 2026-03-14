# logic/pdf_utils.py
import fitz  # PyMuPDF
import io
import zipfile # Để nén các file PDF đã tách thành một file ZIP
import re # Để phân tích chuỗi khoảng trang
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageDraw, ImageFont # Thêm ImageDraw, ImageFont
import io
import math # Cho xoay

# ... (các hàm merge_pdfs và parse_page_ranges giữ nguyên) ...
def merge_pdfs(list_of_pdf_bytes: list) -> bytes:
    """
    Hợp nhất một danh sách các file PDF (dưới dạng bytes) thành một file PDF duy nhất.
    """
    if not list_of_pdf_bytes:
        raise ValueError("Danh sách file PDF đầu vào không được rỗng.")

    merged_pdf = fitz.open()  # Tạo một tài liệu PDF mới, rỗng

    for pdf_bytes in list_of_pdf_bytes:
        try:
            pdf_doc_stream = io.BytesIO(pdf_bytes)
            input_pdf = fitz.open(stream=pdf_doc_stream, filetype="pdf")
            merged_pdf.insert_pdf(input_pdf) 
            input_pdf.close()
        except Exception as e:
            merged_pdf.close() 
            raise ValueError(f"Lỗi khi xử lý một trong các file PDF đầu vào: {e}")

    # Lưu tài liệu đã hợp nhất vào bytes
    merged_pdf_bytes = merged_pdf.tobytes(
        garbage=4, 
        deflate=True
        # linear=True # <<<----- XÓA THAM SỐ NÀY
    )
    merged_pdf.close()
    return merged_pdf_bytes

def parse_page_ranges(ranges_str: str, max_pages: int) -> list:
    """
    Phân tích chuỗi khoảng trang (ví dụ: "1-3, 5, 7-10") thành danh sách các nhóm trang.
    Mỗi nhóm trang sẽ tạo thành một file PDF đầu ra.
    Trang là 1-indexed cho người dùng, chuyển thành 0-indexed cho PyMuPDF.
    Trả về list các list trang (0-indexed). Ví dụ: [[0,1,2], [4], [6,7,8,9]]
    """
    if not ranges_str.strip():
        raise ValueError("Chuỗi khoảng trang không được để trống.")

    output_page_groups = []
    parts = ranges_str.split(',')
    for part in parts:
        part = part.strip()
        current_group_pages = []
        if '-' in part: 
            try:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= max_pages):
                    raise ValueError(f"Khoảng trang '{part}' không hợp lệ. Trang phải từ 1 đến {max_pages}.")
                current_group_pages.extend(list(range(start - 1, end))) 
            except ValueError: 
                 raise ValueError(f"Định dạng khoảng trang '{part}' không hợp lệ.")
        else: 
            try:
                page_num = int(part)
                if not (1 <= page_num <= max_pages):
                    raise ValueError(f"Số trang '{part}' không hợp lệ. Trang phải từ 1 đến {max_pages}.")
                current_group_pages.append(page_num - 1) 
            except ValueError:
                raise ValueError(f"Số trang '{part}' không hợp lệ.")
        
        if current_group_pages: 
            output_page_groups.append(current_group_pages)
            
    if not output_page_groups: 
        raise ValueError("Không có trang hợp lệ nào được chỉ định để tách.")
        
    return output_page_groups


# logic/pdf_utils.py
# ... (các import và các hàm khác giữ nguyên) ...

def split_pdf(pdf_bytes: bytes, mode: str, ranges_str: str = None, n_pages_per_split: int = 1) -> list:
    output_files_data = []
    input_pdf = None
    try:
        input_pdf = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        total_pages = len(input_pdf)
        if total_pages == 0:
            raise ValueError("File PDF đầu vào không có trang nào.")

        if mode == "ranges":
            if not ranges_str:
                raise ValueError("Cần cung cấp chuỗi khoảng trang cho chế độ tách theo khoảng.")
            page_groups_to_extract = parse_page_ranges(ranges_str, total_pages)
            
            for i, page_group in enumerate(page_groups_to_extract):
                new_doc_for_group = fitz.open() 
                sorted_unique_pages_0_indexed = sorted(list(set(page_group)))
                
                for page_idx_0_indexed in sorted_unique_pages_0_indexed:
                    new_doc_for_group.insert_pdf(input_pdf, 
                                                 from_page=page_idx_0_indexed, 
                                                 to_page=page_idx_0_indexed, 
                                                 start_at=-1) 
                
                if len(new_doc_for_group) > 0:
                    # XÓA linear=True (NẾU CÓ) Ở ĐÂY
                    output_bytes = new_doc_for_group.tobytes(garbage=4, deflate=True) 
                    
                    page_desc_parts = [str(p + 1) for p in sorted_unique_pages_0_indexed]
                    # ... (logic tạo page_desc_str) ...
                    page_desc_str = ""
                    if page_desc_parts:
                        if len(page_desc_parts) > 2 and all(int(page_desc_parts[j]) == int(page_desc_parts[0]) + j for j in range(len(page_desc_parts))):
                            page_desc_str = f"{page_desc_parts[0]}-{page_desc_parts[-1]}"
                        else:
                            page_desc_str = "_".join(page_desc_parts)

                    output_files_data.append((f"part_{i+1}_pages_{page_desc_str}.pdf", output_bytes))
                new_doc_for_group.close()

        elif mode == "every_n_pages":
            if not (isinstance(n_pages_per_split, int) and n_pages_per_split > 0):
                raise ValueError("Số trang mỗi file (N) phải là một số nguyên dương.")
            for i_loop in range(0, total_pages, n_pages_per_split):
                new_doc = fitz.open()
                start_page = i_loop
                end_page = min(i_loop + n_pages_per_split - 1, total_pages - 1)
                new_doc.insert_pdf(input_pdf, from_page=start_page, to_page=end_page)
                if len(new_doc) > 0:
                    # XÓA linear=True (NẾU CÓ) Ở ĐÂY
                    output_bytes = new_doc.tobytes(garbage=4, deflate=True)
                    output_files_data.append((f"split_part_{start_page+1}-{end_page+1}.pdf", output_bytes))
                new_doc.close()

        elif mode == "single_pages":
            for i_loop in range(total_pages):
                new_doc = fitz.open()
                new_doc.insert_pdf(input_pdf, from_page=i_loop, to_page=i_loop)
                if len(new_doc) > 0:
                    # XÓA linear=True (NẾU CÓ) Ở ĐÂY
                    output_bytes = new_doc.tobytes(garbage=4, deflate=True)
                    output_files_data.append((f"page_{i_loop+1}.pdf", output_bytes))
                new_doc.close()
        else:
            raise ValueError(f"Chế độ tách '{mode}' không được hỗ trợ.")

    except Exception as e:
        raise ValueError(f"Lỗi khi tách PDF: {e}")
    finally:
        if input_pdf:
            input_pdf.close()
            
    if not output_files_data and total_pages > 0 :
         pass 
    elif not output_files_data and total_pages > 0 :
         raise ValueError("Không có file PDF nào được tạo ra từ quá trình tách. Kiểm tra lại các tham số.")

    return output_files_data

# ... (hàm create_zip_from_files_data giữ nguyên) ...
# ... (hàm create_zip_from_files_data giữ nguyên) ...
def create_zip_from_files_data(files_data: list) -> bytes:
    """
    Tạo một file ZIP trong bộ nhớ từ một danh sách các (tên file, nội dung bytes).
    """
    if not files_data:
        raise ValueError("Không có file nào để nén ZIP.")
        
    zip_buffer = io.BytesIO()
    # Sửa lỗi mode "a" có thể gây lỗi nếu buffer đã có dữ liệu, dùng "w" cho buffer mới
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, data_bytes in files_data:
            zip_file.writestr(filename, data_bytes)
    
    # Không cần zip_file.close() vì đã dùng with statement
    # zip_buffer.seek(0) # Không cần thiết nếu getvalue() được gọi sau khi đóng ZipFile
    return zip_buffer.getvalue()


    # logic/pdf_utils.py (Thêm các hàm sau vào file đã có)
# Hoặc tạo file mới logic/pdf_watermark_logic.py và import fitz, io, PIL, math



# ... (các hàm merge_pdfs, split_pdf, parse_page_ranges, create_zip_from_files_data đã có) ...

def get_page_list(total_pages: int, page_spec: str) -> list[int]:
    """
    Chuyển đổi đặc tả trang (ví dụ: "all", "1,3-5", "even", "odd")
    thành danh sách các chỉ số trang (0-indexed).
    """
    if not page_spec or page_spec.lower() == "all":
        return list(range(total_pages))
    
    pages_to_process_0_indexed = set()
    if page_spec.lower() == "even":
        return [p for p in range(total_pages) if (p + 1) % 2 == 0]
    if page_spec.lower() == "odd":
        return [p for p in range(total_pages) if (p + 1) % 2 != 0]
    
    # Xử lý dạng "1,3-5"
    try:
        parts = page_spec.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= total_pages):
                    raise ValueError(f"Khoảng trang '{part}' không hợp lệ.")
                for i in range(start - 1, end): # 0-indexed
                    if 0 <= i < total_pages:
                        pages_to_process_0_indexed.add(i)
            else:
                page_num = int(part)
                if not (1 <= page_num <= total_pages):
                    raise ValueError(f"Số trang '{part}' không hợp lệ.")
                if 0 <= (page_num - 1) < total_pages:
                    pages_to_process_0_indexed.add(page_num - 1) # 0-indexed
        
        if not pages_to_process_0_indexed:
            raise ValueError("Không có trang hợp lệ nào được chỉ định.")
        return sorted(list(pages_to_process_0_indexed))
    except Exception as e:
        raise ValueError(f"Định dạng chỉ định trang không hợp lệ ('{page_spec}'): {e}")


def add_text_watermark_to_pdf(
    pdf_bytes: bytes, 
    text: str, 
    page_spec: str = "all", # "all", "1,3-5", "even", "odd"
    font_path: str = None, # Đường dẫn đến file .ttf nếu có, nếu không dùng font chuẩn
    font_name_pdf: str = "helv", # Font chuẩn PDF (helv, cour, timas). Sẽ bị ghi đè nếu font_path được dùng
    font_size: int = 48, 
    color: tuple = (0.5, 0.5, 0.5), # (R,G,B) - giá trị từ 0.0 đến 1.0
    opacity: float = 0.5, 
    position: str = "center", # "center", "diagonal_topleft_bottomright", "custom"
    custom_pos: tuple = (0,0), # (x,y) nếu position là "custom"
    angle: int = 0
) -> bytes:
    """Thêm watermark dạng văn bản vào PDF."""
    if not text.strip():
        raise ValueError("Nội dung watermark không được để trống.")
    
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        pages_to_process = get_page_list(len(doc), page_spec)

        for page_num in pages_to_process:
            page = doc.load_page(page_num)
            page_rect = page.rect
            
            # Sử dụng page.insert_textbox cho phép xoay và các tùy chọn khác
            # Để tính toán vị trí, chúng ta cần kích thước của text.
            # PyMuPDF không dễ dàng lấy kích thước text đã xoay với font tùy chỉnh trước khi vẽ.
            # Một cách là vẽ lên một ảnh tạm với PIL rồi chèn ảnh đó.
            
            # Tạo ảnh watermark bằng PIL để dễ kiểm soát xoay và độ mờ
            # Ước lượng kích thước ảnh watermark (khá lớn để chứa text xoay)
            diag = int(math.sqrt(page_rect.width**2 + page_rect.height**2))
            img_pil = Image.new("RGBA", (diag * 2, diag * 2), (255, 255, 255, 0)) # Ảnh trong suốt
            draw = ImageDraw.Draw(img_pil)
            
            try:
                # Nếu có font_path, sử dụng nó, nếu không thì dùng font mặc định (có thể không đẹp cho TV)
                pil_font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default(font_size)
            except IOError: # Không tải được font path, dùng font mặc định
                print(f"Cảnh báo: Không thể tải font từ {font_path}. Sử dụng font mặc định.")
                pil_font = ImageFont.load_default(font_size)

            # Lấy kích thước text (bounding box) với PIL
            # text_bbox = draw.textbbox((0,0), text, font=pil_font, anchor="lt") # Cho PIL mới
            # text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
            # Cách cũ hơn cho textsize (ít chính xác hơn textbbox)
            try: # Thử textbbox nếu Pillow >= 9.2.0
                text_bbox = pil_font.getbbox(text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except AttributeError: # Fallback cho Pillow cũ hơn
                text_width, text_height = draw.textsize(text, font=pil_font)


            # Vẽ text lên giữa ảnh PIL tạm
            img_center_x, img_center_y = diag, diag
            
            # Chuyển đổi màu PyMuPDF (0-1) sang màu PIL (0-255)
            pil_color_r = int(color[0] * 255)
            pil_color_g = int(color[1] * 255)
            pil_color_b = int(color[2] * 255)
            pil_alpha = int(opacity * 255)
            
            draw.text((img_center_x, img_center_y), text, font=pil_font, 
                      fill=(pil_color_r, pil_color_g, pil_color_b, pil_alpha), anchor="mm") # anchor middle-middle

            # Xoay ảnh PIL
            img_pil_rotated = img_pil.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # Xác định vị trí chèn ảnh watermark đã xoay vào trang PDF
            wm_width, wm_height = img_pil_rotated.size
            if position == "center":
                x = (page_rect.width - wm_width) / 2
                y = (page_rect.height - wm_height) / 2
            elif position == "diagonal_topleft_bottomright": # Sẽ giống center nếu angle=0
                 # Với cách vẽ lên ảnh lớn rồi xoay, góc xoay đã được xử lý, chỉ cần đặt vào giữa
                x = (page_rect.width - wm_width) / 2
                y = (page_rect.height - wm_height) / 2
            elif position == "custom":
                x, y = custom_pos
            else: # Mặc định là center
                x = (page_rect.width - wm_width) / 2
                y = (page_rect.height - wm_height) / 2

            wm_rect = fitz.Rect(x, y, x + wm_width, y + wm_height)

            # Chuyển ảnh PIL sang bytes để chèn vào PDF
            img_bytes = io.BytesIO()
            img_pil_rotated.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            page.insert_image(wm_rect, stream=img_bytes.read(), overlay=True)

        watermarked_pdf_bytes = doc.tobytes(garbage=4, deflate=True,)
        return watermarked_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi thêm text watermark: {e}")
    finally:
        if doc:
            doc.close()


def add_image_watermark_to_pdf(
    pdf_bytes: bytes, 
    watermark_image_bytes: bytes,
    page_spec: str = "all",
    opacity: float = 0.5,
    position: str = "center", # "center", "tile", "custom"
    custom_pos: tuple = (0,0), # (x,y) if position is "custom"
    scale: float = 1.0 # Tỷ lệ so với kích thước gốc của ảnh watermark
) -> bytes:
    """Thêm watermark dạng hình ảnh vào PDF."""
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        pages_to_process = get_page_list(len(doc), page_spec)

        # Xử lý ảnh watermark (độ mờ, resize) bằng PIL
        img_pil = Image.open(io.BytesIO(watermark_image_bytes))
        if img_pil.mode != 'RGBA':
            img_pil = img_pil.convert('RGBA')
        
        # Điều chỉnh độ mờ
        if opacity < 1.0:
            alpha = img_pil.split()[3] # Lấy kênh alpha
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity) # opacity là factor từ 0.0 đến 1.0
            img_pil.putalpha(alpha)

        # Resize ảnh theo scale
        original_w, original_h = img_pil.size
        new_w = int(original_w * scale)
        new_h = int(original_h * scale)
        if new_w == 0 or new_h == 0:
            raise ValueError("Kích thước ảnh watermark sau khi scale không hợp lệ (quá nhỏ hoặc scale bằng 0).")
        img_pil_resized = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Chuyển ảnh PIL đã xử lý sang bytes
        final_wm_image_bytes_io = io.BytesIO()
        img_pil_resized.save(final_wm_image_bytes_io, format="PNG") # PNG để giữ độ trong suốt
        final_wm_image_bytes = final_wm_image_bytes_io.getvalue()


        for page_num in pages_to_process:
            page = doc.load_page(page_num)
            page_rect = page.rect
            
            wm_w, wm_h = img_pil_resized.size

            if position == "tile":
                # Lát gạch watermark trên toàn trang
                for x_start in range(0, int(page_rect.width), wm_w):
                    for y_start in range(0, int(page_rect.height), wm_h):
                        wm_rect = fitz.Rect(x_start, y_start, x_start + wm_w, y_start + wm_h)
                        # Giới hạn rect trong trang
                        wm_rect.intersect(page_rect) 
                        if not wm_rect.is_empty:
                             page.insert_image(wm_rect, stream=final_wm_image_bytes, overlay=True)
            else: # center, custom
                if position == "center":
                    x = (page_rect.width - wm_w) / 2
                    y = (page_rect.height - wm_h) / 2
                elif position == "custom":
                    x, y = custom_pos
                else: # Mặc định center
                    x = (page_rect.width - wm_w) / 2
                    y = (page_rect.height - wm_h) / 2
                
                wm_rect = fitz.Rect(x, y, x + wm_w, y + wm_h)
                wm_rect.intersect(page_rect)
                if not wm_rect.is_empty:
                    page.insert_image(wm_rect, stream=final_wm_image_bytes, overlay=True)

        watermarked_pdf_bytes = doc.tobytes(garbage=4, deflate=True,)
        return watermarked_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi thêm image watermark: {e}")
    finally:
        if doc:
            doc.close()


# logic/pdf_utils.py
import fitz  # PyMuPDF
import io
from PIL import Image, ImageDraw, ImageFont # Cần cho add_text_overlay_to_page
import math # Cần cho add_text_overlay_to_page (nếu dùng lại logic watermark)

# ... (các hàm merge_pdfs, split_pdf, parse_page_ranges, create_zip_from_files_data đã có) ...
# ... (các hàm add_text_watermark_to_pdf, add_image_watermark_to_pdf đã có, nếu bạn để chung) ...

# HÀM MỚI CẦN THÊM VÀO HOẶC ĐẢM BẢO ĐÃ CÓ:
def get_page_list(total_pages: int, page_spec: str) -> list[int]: # Hàm này được dùng bởi manipulate_pdf_pages
    """
    Chuyển đổi đặc tả trang (ví dụ: "all", "1,3-5", "even", "odd")
    thành danh sách các chỉ số trang (0-indexed).
    """
    if not page_spec or page_spec.lower() == "all":
        return list(range(total_pages))
    
    pages_to_process_0_indexed = set()
    if page_spec.lower() == "even":
        return [p for p in range(total_pages) if (p + 1) % 2 == 0]
    if page_spec.lower() == "odd":
        return [p for p in range(total_pages) if (p + 1) % 2 != 0]
    
    try:
        parts = page_spec.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= total_pages):
                    raise ValueError(f"Khoảng trang '{part}' không hợp lệ.")
                for i in range(start - 1, end): 
                    if 0 <= i < total_pages:
                        pages_to_process_0_indexed.add(i)
            else:
                page_num = int(part)
                if not (1 <= page_num <= total_pages):
                    raise ValueError(f"Số trang '{part}' không hợp lệ.")
                if 0 <= (page_num - 1) < total_pages:
                    pages_to_process_0_indexed.add(page_num - 1) 
        
        if not pages_to_process_0_indexed:
            raise ValueError("Không có trang hợp lệ nào được chỉ định.")
        return sorted(list(pages_to_process_0_indexed))
    except Exception as e:
        raise ValueError(f"Định dạng chỉ định trang không hợp lệ ('{page_spec}'): {e}")


def manipulate_pdf_pages(
    pdf_bytes: bytes,
    pages_to_delete: list[int] = None, 
    page_rotations: dict[int, int] = None, 
    new_page_order: list[int] = None, 
    insert_blank_after: dict[int, tuple] = None 
) -> bytes:
    """
    Thực hiện các thao tác xóa, xoay, sắp xếp lại trang, chèn trang trắng.
    LƯU Ý: Các thao tác được thực hiện theo thứ tự: delete, rotate, reorder, insert blank.
    """
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")

        if pages_to_delete:
            for page_num_0_idx in sorted(list(set(pages_to_delete)), reverse=True):
                if 0 <= page_num_0_idx < len(doc):
                    doc.delete_page(page_num_0_idx)
                else:
                    print(f"Cảnh báo: Số trang {page_num_0_idx + 1} không hợp lệ để xóa.")
        
        current_num_pages_after_delete = len(doc) # Cập nhật số trang sau khi xóa

        if page_rotations:
            for page_num_0_idx, angle in page_rotations.items():
                if 0 <= page_num_0_idx < current_num_pages_after_delete and angle in [0, 90, 180, 270]:
                    # Phải load lại trang từ doc hiện tại sau khi có thể đã xóa trang
                    # Hoặc đảm bảo page_rotations dùng chỉ số đúng của doc sau khi xóa
                    # Cách an toàn là chỉ xoay nếu trang đó còn tồn tại
                    if 0 <= page_num_0_idx < len(doc): # Kiểm tra lại với len(doc) hiện tại
                         doc[page_num_0_idx].rotate(angle)
                else:
                    print(f"Cảnh báo: Số trang {page_num_0_idx + 1} hoặc góc xoay {angle} không hợp lệ (sau khi xóa).")
        
        if new_page_order:
            # new_page_order phải là list các chỉ số 0-indexed của các trang *còn lại* trong `doc`
            # theo thứ tự mới mong muốn.
            # Ví dụ, nếu doc có 3 trang [0, 1, 2], new_page_order = [2, 0, 1]
            current_pages_in_doc = len(doc)
            if len(new_page_order) == current_pages_in_doc and \
               all(0 <= p < current_pages_in_doc for p in new_page_order) and \
               len(set(new_page_order)) == current_pages_in_doc:
                
                temp_doc = fitz.open()
                # PyMuPDF >= 1.19.0 hỗ trợ tham số 'pages'
                try:
                    temp_doc.insert_pdf(doc, pages=new_page_order)
                except TypeError: # Fallback cho phiên bản cũ hơn
                    print("DEBUG: PyMuPDF version might not support 'pages' in insert_pdf. Inserting one by one.")
                    for original_page_idx in new_page_order:
                        temp_doc.insert_pdf(doc, from_page=original_page_idx, to_page=original_page_idx, start_at=-1)
                
                doc.close() 
                doc = temp_doc 
            else:
                print(f"Cảnh báo: Thứ tự trang mới không hợp lệ. Số trang hiện tại: {current_pages_in_doc}, thứ tự yêu cầu: {new_page_order}")
        
        current_num_pages_after_reorder = len(doc)

        if insert_blank_after:
            offset = 0 # Để điều chỉnh chỉ số chèn nếu có nhiều trang được chèn
            for page_idx_after_0_indexed, (width, height) in sorted(insert_blank_after.items()):
                insert_at_pno_adjusted = -1 # Mặc định append
                if page_idx_after_0_indexed == -1 : # Chèn ở đầu
                    insert_at_pno_adjusted = 0 + offset
                elif 0 <= page_idx_after_0_indexed < current_num_pages_after_reorder:
                    insert_at_pno_adjusted = page_idx_after_0_indexed + 1 + offset
                
                if insert_at_pno_adjusted != -1 and 0 <= insert_at_pno_adjusted <= len(doc):
                     doc.new_page(pno=insert_at_pno_adjusted, width=width, height=height)
                     offset +=1
                elif insert_at_pno_adjusted == -1 or insert_at_pno_adjusted > len(doc): # Append
                     doc.new_page(pno=-1, width=width, height=height) # Append
                     offset +=1 # Dù append, vẫn coi như đã thêm 1 trang cho các lần chèn sau nếu có
                else:
                     print(f"Cảnh báo: Vị trí chèn trang trắng không hợp lệ: sau trang index {page_idx_after_0_indexed}")


        edited_pdf_bytes = doc.tobytes(garbage=4, deflate=True)
        return edited_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi biên tập trang PDF: {e}")
    finally:
        if doc:
            doc.close()

            


def add_text_overlay_to_page(pdf_bytes: bytes, page_num_0_idx: int, text: str, 
                             rect_tuple: tuple, 
                             fontname: str = "helv", fontsize: int = 11, 
                             color_tuple: tuple = (0,0,0), # đen
                             rotate: int = 0,
                             opacity: float = 1.0, # Thêm opacity
                             font_path: str = None # Thêm font_path
                             ) -> bytes:
    doc = None
    try:
        doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        if not (0 <= page_num_0_idx < len(doc)):
            raise ValueError("Số trang không hợp lệ để thêm text.")
        
        page = doc.load_page(page_num_0_idx)
        rect = fitz.Rect(rect_tuple)
        
        # Để kiểm soát opacity của text, chúng ta cần vẽ lên một PDF con (form XObject)
        # rồi chèn XObject đó với opacity mong muốn.
        # Hoặc đơn giản hơn là dùng lại logic của text watermark nếu nó đã xử lý opacity.
        # Nếu dùng lại logic text_watermark (đã dùng PIL để tạo ảnh text có opacity):
        
        # Tạo ảnh text bằng PIL để kiểm soát opacity và font tốt hơn
        # Ước lượng kích thước ảnh (có thể cần lớn hơn rect_tuple nếu text xoay)
        img_width = int(rect.width) + 2 * fontsize # Thêm padding
        img_height = int(rect.height) + 2 * fontsize
        # Đảm bảo kích thước dương
        img_width = max(img_width, 100)
        img_height = max(img_height, 50)


        img_pil = Image.new("RGBA", (img_width, img_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img_pil)
        
        try:
            pil_font = ImageFont.truetype(font_path, fontsize) if font_path and os.path.exists(font_path) else ImageFont.load_default(fontsize)
        except IOError:
            pil_font = ImageFont.load_default(fontsize)

        pil_color_r = int(color_tuple[0] * 255)
        pil_color_g = int(color_tuple[1] * 255)
        pil_color_b = int(color_tuple[2] * 255)
        pil_alpha = int(opacity * 255)
        
        # Vẽ text vào giữa ảnh PIL tạm (hoặc góc trên trái)
        # text_bbox = draw.textbbox((0,0), text, font=pil_font, anchor="lt")
        # text_actual_width = text_bbox[2] - text_bbox[0]
        # text_actual_height = text_bbox[3] - text_bbox[1]

        # Vẽ text vào điểm bắt đầu của rect (đã được điều chỉnh cho padding của ảnh)
        # draw.text((fontsize, fontsize), text, font=pil_font, fill=(pil_color_r, pil_color_g, pil_color_b, pil_alpha))
        # Để text vừa trong rect_tuple, dùng insert_textbox của PyMuPDF sẽ dễ hơn nếu không cần opacity phức tạp
        # Nếu cần opacity, thì ảnh PIL là cách tốt.
        # Với ảnh PIL, ta vẽ vào (0,0) của ảnh đó, rồi đặt ảnh đó vào rect_tuple trên PDF.

        # Cách 1: Dùng insert_textbox (đơn giản, opacity không trực tiếp)
        # page.insert_textbox(rect, text, fontname=fontname, fontsize=fontsize,
        #                     color=color_tuple, rotate=rotate, align=fitz.TEXT_ALIGN_LEFT)

        # Cách 2: Dùng ảnh PIL (phức tạp hơn, kiểm soát opacity tốt hơn)
        # Vẽ text vào ảnh PIL, xoay ảnh PIL, rồi chèn ảnh PIL vào PDF
        # Giả sử text không quá dài cho rect được cung cấp
        temp_img_for_text = Image.new("RGBA", (int(rect.width), int(rect.height)), (255,255,255,0))
        temp_draw = ImageDraw.Draw(temp_img_for_text)
        temp_draw.text((0,0), text, font=pil_font, fill=(pil_color_r, pil_color_g, pil_color_b, pil_alpha))
        
        if rotate != 0:
            temp_img_for_text = temp_img_for_text.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
            # Nếu xoay, rect có thể cần điều chỉnh lại vị trí để ảnh xoay được đặt đúng
            # Điều này phức tạp, tạm thời giả định người dùng tự điều chỉnh rect cho phù hợp với xoay

        img_bytes = io.BytesIO()
        temp_img_for_text.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        page.insert_image(rect, stream=img_bytes.read(), overlay=True, rotate=0) # Xoay đã được xử lý bởi PIL

        overlayed_pdf_bytes = doc.tobytes(garbage=4, deflate=True)
        return overlayed_pdf_bytes
    except Exception as e:
        raise ValueError(f"Lỗi khi thêm text overlay: {e}")
    finally:
        if doc:
            doc.close()