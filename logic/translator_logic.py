# logic/translator_logic.py
import asyncio
from .common_processing import generate_groq_response # Sử dụng lại hàm gọi Groq

async def translate_text_with_llm(api_key: str,
                                  text_to_translate: str,
                                  source_language: str, # Ví dụ: "Vietnamese", "English", hoặc "auto"
                                  target_language: str  # Ví dụ: "English", "Vietnamese"
                                 ) -> str:
    """
    Dịch văn bản sử dụng LLM (Groq).
    """
    if not api_key:
        raise ValueError("API Key chưa được cấu hình.")
    if not text_to_translate.strip():
        return "" # Trả về chuỗi rỗng nếu không có gì để dịch

    # Xử lý trường hợp tự động phát hiện ngôn ngữ nguồn
    if source_language.lower() == "auto" or source_language.lower() == "tự động phát hiện":
        source_lang_instruction = "tự động phát hiện ngôn ngữ nguồn"
    else:
        source_lang_instruction = f"ngôn ngữ nguồn là {source_language}"

    system_message = f"Bạn là một trợ lý dịch thuật đa ngôn ngữ chuyên nghiệp. Nhiệm vụ của bạn là dịch văn bản một cách chính xác và tự nhiên nhất có thể. Chỉ trả về nội dung đã dịch, không thêm bất kỳ lời giải thích, mở đầu hay kết thúc nào."

    prompt = f"""
Vui lòng dịch đoạn văn bản sau từ {source_lang_instruction} sang {target_language}:

--- VĂN BẢN CẦN DỊCH ---
{text_to_translate}
--- KẾT THÚC VĂN BẢN ---

Hãy đảm bảo bản dịch giữ đúng ý nghĩa và văn phong của văn bản gốc.
"""

    try:
        # Giới hạn token cho bản dịch có thể cần nhiều hơn mặc định
        # Ví dụ, nếu văn bản gốc có N token, bản dịch có thể có N +/- M token.
        # Tính toán max_tokens một cách tương đối, ví dụ 1.5 lần số từ hoặc 2 lần số ký tự / 3 (ước lượng token)
        # Hoặc đặt một giá trị lớn an toàn, ví dụ 2048 hoặc 3000 cho các đoạn văn bản vừa phải.
        # LLama3 có context window lớn, nên có thể không quá lo lắng với các đoạn text ngắn/trung bình.
        estimated_output_tokens = min(len(text_to_translate.split()) * 3, 3000) # Ước lượng thô

        translated_text = await generate_groq_response(
            api_key,
            prompt,
            system_message=system_message,
            max_tokens=estimated_output_tokens, # Cho phép LLM trả về đủ dài
            temperature=0.3 # Nhiệt độ thấp hơn cho dịch thuật để chính xác hơn
        )
        return translated_text
    except ValueError as ve: # Lỗi từ generate_groq_response (vd: API key)
        raise ve
    except Exception as e:
        print(f"Lỗi không mong muốn khi gọi LLM để dịch: {e}")
        raise ValueError(f"Đã có lỗi xảy ra trong quá trình dịch: {e}")