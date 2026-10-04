# logic/common_processing.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import nltk
import re
import cv2
import numpy as np
import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps, ImageEnhance
from concurrent.futures import ThreadPoolExecutor

# --- PDF & IMAGE PROCESSING ---
def convert_pdf_to_txt(file_data):
    try:
        with fitz.open(stream=file_data, filetype="pdf") as doc:
            return "".join([page.get_text("text") for page in doc])
    except Exception as e:
        # st.error(f"PDF Error: {e}") # UI should handle st.error
        raise ValueError(f"Lỗi xử lý PDF: {e}")

def convert_pdf_to_images(pdf_path_or_bytes, dpi=150, first_page=1, last_page=None, poppler_path=None):
    """
    Converts PDF pages to a list of PIL Images.
    Can accept a file path or bytes.
    If last_page is None, converts all pages from first_page.
    """
    try:
        if isinstance(pdf_path_or_bytes, str): # It's a path
             return convert_from_path(pdf_path_or_bytes, dpi=dpi, first_page=first_page, last_page=last_page, poppler_path=poppler_path)
        else: # It's bytes
             return convert_from_path(pdf_path=None, pdf_file=pdf_path_or_bytes, dpi=dpi, first_page=first_page, last_page=last_page, poppler_path=poppler_path)
    except Exception as e:
        # st.warning(f"⚠️ Lỗi chuyển PDF sang ảnh: {e}") # UI should handle
        raise ValueError(f"Lỗi chuyển PDF sang ảnh (cần Poppler cho Windows): {e}")


def preprocess_image_ocr(img_pil, resize_factor=2.0):
    """
    Tiền xử lý ảnh để OCR tốt hơn:
    - Sửa xoay theo EXIF
    - Ép ảnh về RGB
    - Phóng to ảnh nếu ảnh nhỏ
    - Tăng contrast/sharpness
    - Grayscale
    - Khử nhiễu nhẹ
    - Adaptive threshold

    Return: PIL Image đã xử lý.
    """
    try:
        img_pil = ImageOps.exif_transpose(img_pil)

        if img_pil.mode != "RGB":
            img_pil = img_pil.convert("RGB")

        width, height = img_pil.size

        # Phóng to ảnh để OCR dễ đọc chữ nhỏ
        if resize_factor and resize_factor != 1.0:
            img_pil = img_pil.resize(
                (int(width * resize_factor), int(height * resize_factor)),
                Image.Resampling.LANCZOS
            )

        # Tăng chất lượng chữ
        img_pil = ImageEnhance.Contrast(img_pil).enhance(1.5)
        img_pil = ImageEnhance.Sharpness(img_pil).enhance(1.4)

        img_np = np.array(img_pil)

        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Khử nhiễu nhẹ
        gray = cv2.fastNlMeansDenoising(
            gray,
            None,
            h=10,
            templateWindowSize=7,
            searchWindowSize=21
        )

        # Adaptive threshold phù hợp ảnh chụp/scan
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15
        )

        return Image.fromarray(thresh)

    except Exception as e:
        print(f"Lỗi tiền xử lý ảnh OCR: {e}")
        if img_pil.mode != "RGB":
            return img_pil.convert("RGB")
        return img_pil


def score_ocr_text(text: str) -> int:
    """
    Chấm điểm kết quả OCR để chọn output tốt nhất.
    Ưu tiên text dài, có nhiều chữ/số và ít ký tự rác.
    """
    if not text:
        return 0

    text = text.strip()

    vietnamese_chars = len(re.findall(
        r"[a-zA-ZÀ-ỹ0-9]",
        text
    ))

    junk_chars = len(re.findall(
        r"[~`|{}\[\]<>_^=\\]",
        text
    ))

    useful_keywords = [
        "hóa đơn", "hoa don", "gtgt", "mã số thuế", "mst",
        "sơ yếu", "so yeu", "lý lịch", "ly lich",
        "cộng hòa", "cong hoa", "độc lập", "doc lap",
        "họ tên", "ho ten", "ngày sinh", "ngay sinh",
        "địa chỉ", "dia chi"
    ]

    keyword_score = 0
    lower_text = text.lower()

    for kw in useful_keywords:
        if kw in lower_text:
            keyword_score += 50

    return vietnamese_chars + keyword_score - junk_chars * 3


def extract_text_from_image_pil(img_pil, lang="vie+eng", preprocess=True):
    """
    OCR một ảnh PIL.
    Có thử nhiều cấu hình Tesseract PSM và chọn kết quả tốt nhất.
    """
    try:
        img_pil = ImageOps.exif_transpose(img_pil)

        if img_pil.mode != "RGB":
            img_pil = img_pil.convert("RGB")

        images_to_try = []

        # 1. Ảnh gốc RGB
        images_to_try.append(img_pil)

        # 2. Ảnh đã preprocess
        if preprocess:
            processed = preprocess_image_ocr(img_pil, resize_factor=2.0)
            images_to_try.append(processed)

        configs = [
            "--oem 3 --psm 6",
            "--oem 3 --psm 4",
            "--oem 3 --psm 11",
            "--oem 3 --psm 3",
        ]

        candidates = []

        for image_variant in images_to_try:
            for config in configs:
                text = pytesseract.image_to_string(
                    image_variant,
                    lang=lang,
                    config=config
                ).strip()

                if text:
                    candidates.append(text)

        if not candidates:
            return ""

        best_text = max(candidates, key=score_ocr_text)

        return best_text.strip()

    except Exception as e:
        raise ValueError(f"Lỗi OCR ảnh: {e}")


def extract_text_from_list_of_images(images_pil_list, lang="vie+eng", preprocess=True):
    """
    OCR nhiều ảnh bằng ThreadPoolExecutor.
    """
    if not images_pil_list:
        return ""

    results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(extract_text_from_image_pil, img, lang, preprocess)
            for img in images_pil_list
        ]

        for idx, future in enumerate(futures, start=1):
            try:
                page_text = future.result()
                results.append(f"\n--- Trang {idx} ---\n{page_text}")
            except Exception as e:
                results.append(f"\n--- Trang {idx} ---\n[Lỗi OCR một trang: {e}]")

    return "\n".join(results).strip()

# --- TEXT PROCESSING ---
def preprocess_text_nlp(text):
    """Cleans and tokenizes text into sentences."""
    if not text or not isinstance(text, str):
        return []
    cleaned = ' '.join(text.split())
    return nltk.sent_tokenize(cleaned)

def chunk_text(text, max_chars=4000): # Simplified chunking by characters
    """Chunks text into pieces of max_chars."""
    if not text or not isinstance(text, str):
        return []
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


# --- AI PROCESSING (GROQ) ---
GROQ_MODEL = "openai/gpt-oss-20b"  # Or "mixtral-8x7b-32768" or other valid models
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def generate_groq_response(api_key: str, prompt: str, system_message: str = "You are a helpful assistant.", max_tokens: int = 1024, temperature: float = 0.7):
    """Generic function to get response from Groq API."""
    if not api_key:
        # return {"error": "API Key for Groq/OpenRouter is not configured."} # This is logic, not UI
        raise ValueError("API Key for Groq/OpenRouter is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 1,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client: # Increased timeout
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        # error_details = e.response.json() if e.response.content else {"message": "Unknown API error"}
        # return {"error": f"API Error ({e.response.status_code}): {error_details.get('error', {}).get('message', e.response.text)}"}
        raise ValueError(f"Lỗi API ({e.response.status_code}): {e.response.text}")
    except httpx.RequestError as e:
        # return {"error": f"Request Error: {e}"}
        raise ValueError(f"Lỗi yêu cầu mạng: {e}")
    except Exception as e:
        # return {"error": f"An unexpected error occurred: {e}"}
        raise ValueError(f"Lỗi không mong muốn: {e}")

async def process_document_for_main_smartdoc(api_key: str, text_content: str):
    """
    Processes a document for the main SmartDoc features:
    entities, relationships, summary, classification.
    """
    # Limit text to avoid exceeding token limits (approx. 6000-7000 tokens for Llama3-70B)
    # 1 token ~ 3-4 chars. So, 20000 chars is a safe bet.
    context_limit_chars = 20000
    base_text = text_content[:context_limit_chars]

    if not base_text.strip():
        return "Văn bản trống.", "Văn bản trống.", "Văn bản trống.", "Không xác định."

    # Prompts are in Vietnamese as requested by user's original code
    prompt_entities = f"Trích xuất các thực thể được đặt tên (tên người, tổ chức, địa điểm, ngày tháng, số tiền, chức danh, etc.) từ văn bản sau. Trả lời bằng tiếng Việt:\n\n{base_text}"
    prompt_relationships = f"Tìm và mô tả các mối quan hệ quan trọng giữa các thực thể trong văn bản sau. Trả lời bằng tiếng Việt:\n\n{base_text}"
    prompt_summary = f"Tóm tắt tài liệu sau trong khoảng 3-5 câu súc tích, tập trung vào các ý chính. Trả lời bằng tiếng Việt:\n\n{base_text}"
    prompt_classification = f"Phân loại tài liệu sau vào MỘT trong các danh mục sau: Hợp đồng, Báo cáo, CV/Hồ sơ, Thư từ, Hóa đơn, Pháp lý, Y tế, Giáo dục, Kỹ thuật, Cá nhân, Khác. Chỉ trả về tên danh mục bằng tiếng Việt.\n\nĐoạn văn bản:\n{base_text}"

    tasks = [
        generate_groq_response(api_key, prompt_entities, system_message="Bạn là một chuyên gia trích xuất thực thể.", max_tokens=1024),
        generate_groq_response(api_key, prompt_relationships, system_message="Bạn là một chuyên gia phân tích mối quan hệ văn bản.", max_tokens=1024),
        generate_groq_response(api_key, prompt_summary, system_message="Bạn là một chuyên gia tóm tắt văn bản.", max_tokens=512),
        generate_groq_response(api_key, prompt_classification, system_message="Bạn là một chuyên gia phân loại tài liệu.", max_tokens=50)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True) # Capture exceptions too

    # Check for errors in results
    processed_results = []
    for res in results:
        if isinstance(res, Exception):
            processed_results.append(f"[Lỗi AI: {str(res)}]")
        else:
            processed_results.append(res)
            
    return tuple(processed_results)