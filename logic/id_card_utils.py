# logic/id_card_utils.py
import re
import numpy as np
import cv2
from PIL import Image
import pytesseract

# Hàm này có thể không cần thiết nếu AI model đã làm tốt việc trích xuất từ text OCR thô
def extract_personal_info_regex(text): # Đổi tên để rõ là dùng regex
    # Regex cho CCCD (12 số, có thể có dấu cách/gạch ngang)
    cccd_pattern = r"\b(?:\d{3,4}[\s-]?){2}\d{3,4}\b" # Cải thiện regex CCCD
    # Regex cho ngày sinh (dd/mm/yyyy hoặc dd-mm-yyyy, dd.mm.yyyy)
    dob_pattern = r"\b(0?[1-9]|[12][0-9]|3[01])[-/.](0?[1-9]|1[0-2])[-/.](19\d{2}|20\d{2})\b"
    # Regex cho họ tên (viết hoa chữ cái đầu mỗi từ, có dấu, ít nhất 2 từ)
    # Cần cải thiện regex này cho tên Việt Nam
    name_pattern = r"Họ và tên(?:\s*|[:])\s*([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*(?:\s+[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*)+)"
    # name_pattern = r"\b([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s[A-ZÀ-Ỹ][a-zà-ỹ]+)+)\b" # Một regex tên đơn giản hơn

    info = {
        "cccd": re.findall(cccd_pattern, text),
        "dob": re.findall(dob_pattern, text),
        "full_name_guess": re.findall(name_pattern, text) # Nên để AI làm việc này
    }
    # Lấy kết quả đầu tiên nếu có
    for key, value in info.items():
        if isinstance(value, list) and value:
            info[key] = value[0]
        elif isinstance(value, list) and not value:
            info[key] = None
    return info

def preprocess_image_for_id_card(img_pil: Image.Image) -> Image.Image:
    """Tiền xử lý ảnh PIL cho việc OCR CCCD/giấy tờ tương tự."""
    try:
        np_img = np.array(img_pil.convert('L')) # Chuyển sang ảnh xám
        
        # Làm sắc nét ảnh có thể hữu ích
        # kernel_sharpening = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
        # sharpened_img = cv2.filter2D(np_img, -1, kernel_sharpening)

        # Cân bằng histogram để tăng độ tương phản
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        # equalized_img = clahe.apply(np_img)
        equalized_img = cv2.equalizeHist(np_img)


        # Ngưỡng hóa thích nghi
        thresh = cv2.adaptiveThreshold(equalized_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 15, 5) # Điều chỉnh params nếu cần (blockSize, C)

        # Có thể thử một chút GaussianBlur trước threshold nếu ảnh nhiễu
        # gray = cv2.GaussianBlur(np_img, (3, 3), 0)
        # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return Image.fromarray(thresh)
    except Exception as e:
        print(f"Lỗi tiền xử lý ảnh CCCD: {e}")
        return img_pil # Trả về ảnh gốc nếu lỗi

def ocr_text_from_id_card_image(img_pil: Image.Image, lang="vie", preprocess=True) -> str:
    """OCR text từ ảnh PIL của CCCD, có tùy chọn tiền xử lý."""
    try:
        if preprocess:
            processed_img = preprocess_image_for_id_card(img_pil)
        else:
            processed_img = img_pil
        # Cấu hình Tesseract page segmentation mode có thể hữu ích
        # custom_config = r'--oem 3 --psm 6' # Assume a single uniform block of text.
        # custom_config = r'--oem 3 --psm 11' # Sparse text. Find as much text as possible in no particular order.
        # custom_config = r'--oem 3 --psm 3' # Fully automatic page segmentation, but no OSD. (Default)
        text = pytesseract.image_to_string(processed_img, lang=lang) #, config=custom_config)
        return text
    except Exception as e:
        raise ValueError(f"Lỗi OCR ảnh CCCD: {e}")