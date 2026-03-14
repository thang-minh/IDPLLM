# logic/form_extractor_logic.py
import json
import re
from .common_processing import generate_groq_response # Import from common_processing

async def parse_text_with_groq_form(api_key: str, text_content: str) -> dict:
    """
    Parses text extracted from a form (ID card, invoice, application) using Groq.
    """
    # Using the more detailed prompt from user's code
    prompt = f"""
Đây là văn bản trích xuất từ mẫu đơn hoặc giấy tờ, có thể là CMND/CCCD hoặc đơn xin việc hoặc hóa đơn điện tử:

{text_content}

Hãy tự động nhận diện loại giấy tờ và trích xuất thông tin vào một cấu trúc JSON duy nhất.
Nếu đây là CMND/CCCD, bao gồm các trường:
- loai_giay_to: "CMND/CCCD"
- so_cmnd_cccd: (string)
- ho_ten: (string)
- ngay_sinh: (string, "DD/MM/YYYY")
- gioi_tinh: (string, "Nam" hoặc "Nữ")
- dan_toc: (string)
- quoc_tich: (string, mặc định "Việt Nam" nếu không có)
- que_quan: (string)
- noi_thuong_tru: (string) # Hoặc noi_dang_ky_thuong_tru
- dac_diem_nhan_dang: (string, tùy chọn)
- ngay_cap: (string, "DD/MM/YYYY")
- noi_cap: (string)
- co_gia_tri_den: (string, "DD/MM/YYYY", tùy chọn cho CCCD)

Nếu đây là Hóa đơn/Hóa đơn điện tử, bao gồm các trường:
- loai_giay_to: "Hóa đơn"
- ky_hieu_mau_so: (string)
- ky_hieu_hoa_don: (string)
- so_hoa_don: (string)
- ngay_lap_hoa_don: (string, "DD/MM/YYYY")
- ten_don_vi_ban: (string)
- mst_don_vi_ban: (string)
- dia_chi_don_vi_ban: (string)
- dien_thoai_don_vi_ban: (string, tùy chọn)
- email_don_vi_ban: (string, tùy chọn)
- stk_don_vi_ban: (string, tùy chọn)
- ten_ngan_hang_don_vi_ban: (string, tùy chọn)
- ten_don_vi_mua: (string, tùy chọn)
- ten_nguoi_mua: (string)
- mst_nguoi_mua: (string, tùy chọn)
- dia_chi_nguoi_mua: (string)
- dien_thoai_nguoi_mua: (string, tùy chọn)
- hinh_thuc_thanh_toan: (string)
- chi_tiet_hang_hoa_dich_vu: (array of objects, mỗi object có: stt, ten_hang_hoa, don_vi_tinh, so_luong, don_gia, thanh_tien_chua_thue, thue_suat_gtgt, tien_thue_gtgt, thanh_tien_co_thue)
- tong_cong_tien_hang_chua_thue: (number)
- tong_tien_thue_gtgt: (number)
- tong_tien_thanh_toan_bang_so: (number)
- tong_tien_thanh_toan_bang_chu: (string)
- chu_ky_so_nguoi_ban: (string, "Có" hoặc "Không" hoặc chi tiết)
- chu_ky_so_nguoi_mua: (string, "Có" hoặc "Không" hoặc chi tiết)


Nếu đây là Đơn xin việc (CV), bao gồm các trường:
- loai_giay_to: "Đơn xin việc/CV"
- ho_ten_ung_vien: (string)
- ngay_sinh_ung_vien: (string, "DD/MM/YYYY")
- gioi_tinh_ung_vien: (string)
- dia_chi_lien_he: (string)
- so_dien_thoai_lien_he: (string)
- email_lien_he: (string)
- vi_tri_ung_tuyen: (string)
- trinh_do_hoc_van: (string hoặc array of objects)
- kinh_nghiem_lam_viec: (string hoặc array of objects, mỗi object có: ten_cong_ty, chuc_vu, thoi_gian_lam_viec, mo_ta_cong_viec)
- ky_nang: (array of strings hoặc string)
- chung_chi: (array of strings hoặc string, tùy chọn)
- muc_tieu_nghe_nghiep: (string)
- so_thich: (string, tùy chọn)
- nguoi_tham_chieu: (string hoặc array of objects, tùy chọn)

Nếu là loại giấy tờ khác không thuộc các loại trên, hãy đặt "loai_giay_to": "Khác" và trích xuất các trường thông tin chung nhất có thể.
Ưu tiên các trường được liệt kê. Nếu không tìm thấy thông tin cho một trường, hãy để giá trị là null hoặc một chuỗi rỗng.
CHỈ TRẢ VỀ ĐÚNG MỘT ĐỐI TƯỢNG JSON, không có bất kỳ giải thích hay định dạng markdown nào xung quanh nó.
"""
    system_msg = "Bạn là một AI chuyên gia trích xuất thông tin từ văn bản OCR của các loại giấy tờ như CMND/CCCD, hóa đơn, và đơn xin việc/CV. Nhiệm vụ của bạn là nhận diện loại giấy tờ và trả về thông tin dưới dạng một đối tượng JSON duy nhất."
    
    response_str = await generate_groq_response(api_key, prompt, system_message=system_msg, max_tokens=3000, temperature=0.1) # Increase max_tokens for complex forms

    try:
        # Thử tìm JSON trong phản hồi, có thể bị bao bởi ```json ... ```
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_str)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Nếu không có markdown, giả sử toàn bộ là JSON (hoặc có thể bắt đầu bằng { và kết thúc bằng })
            first_brace = response_str.find('{')
            last_brace = response_str.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response_str[first_brace : last_brace+1]
            else: # Không tìm thấy JSON rõ ràng
                 return {"error": "AI did not return a clear JSON object.", "raw_response": response_str}
        
        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError:
        return {"error": "AI returned content that is not valid JSON.", "raw_response": response_str}
    except Exception as e: # Bắt các lỗi khác
        return {"error": f"An unexpected error occurred while parsing AI response: {str(e)}", "raw_response": response_str}