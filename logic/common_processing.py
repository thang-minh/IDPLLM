# logic/common_processing.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import nltk
import cv2
import numpy as np
import httpx
import asyncio
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


def preprocess_image_ocr(img_pil, resize_factor=1.0): # General purpose preprocessing
    """Preprocesses a PIL image for potentially better OCR results."""
    try:
        img_np = np.array(img_pil.convert('RGB'))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        if resize_factor != 1.0:
            gray = cv2.resize(gray, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_CUBIC)

        # Adaptive thresholding can be better for varying lighting
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        # Denoising
        # thresh = cv2.fastNlMeansDenoising(thresh, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # A bit of blurring can help reduce noise for Tesseract
        # gray = cv2.medianBlur(gray, 3)
        # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return Image.fromarray(thresh)
    except Exception as e:
        # st.warning(f"Lỗi tiền xử lý ảnh: {e}") # UI handles
        print(f"Lỗi tiền xử lý ảnh: {e}")
        return img_pil # Return original if error

def extract_text_from_image_pil(img_pil, lang='vie+eng', preprocess=False):
    """Extracts text from a single PIL image."""
    try:
        if preprocess:
            img_to_ocr = preprocess_image_ocr(img_pil)
        else:
            img_to_ocr = img_pil
        return pytesseract.image_to_string(img_to_ocr, lang=lang)
    except Exception as e:
        # st.warning(f"Lỗi OCR ảnh: {e}") # UI handles
        raise ValueError(f"Lỗi OCR ảnh: {e}")


def extract_text_from_list_of_images(images_pil_list, lang='vie+eng', preprocess=False):
    """Extracts text from a list of PIL images using ThreadPoolExecutor."""
    if not images_pil_list:
        return ""
    
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor: # Adjust max_workers as needed
        futures = [executor.submit(extract_text_from_image_pil, img, lang, preprocess) for img in images_pil_list]
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"\n[Lỗi OCR một trang: {e}]\n") # Capture error per page
    return "\n".join(results)

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
GROQ_MODEL = "llama-3.1-8b-instant"  # Or "mixtral-8x7b-32768" or other valid models
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