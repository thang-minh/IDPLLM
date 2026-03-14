# logic/sentiment_analyzer_logic.py
import json
import re
from .common_processing import generate_groq_response

async def analyze_sentiment_with_groq(api_key: str, text_to_analyze: str) -> dict:
    """
    Analyzes sentiment of the given text using Groq.
    Returns a dictionary with sentiment and explanation.
    """
    prompt = f"""
Phân tích cảm xúc của đoạn văn bản sau.
Hãy xác định cảm xúc chính (ví dụ: Rất tích cực, Tích cực, Trung tính, Tiêu cực, Rất tiêu cực).
Cung cấp một điểm số cảm xúc từ -1.0 (rất tiêu cực) đến 1.0 (rất tích cực).
Đưa ra một vài từ khóa chính hoặc cụm từ trong văn bản góp phần vào cảm xúc đó.
Trả lời bằng tiếng Việt và định dạng kết quả dưới dạng JSON như sau:
{{
  "cam_xuc_chinh": "...",
  "diem_so_cam_xuc": 0.0,
  "tu_khoa_cam_xuc": ["...", "..."],
  "giai_thich_ngan": "..."
}}

Đoạn văn bản cần phân tích:
---
{text_to_analyze}
---
CHỈ TRẢ VỀ ĐÚNG MỘT ĐỐI TƯỢNG JSON, không có bất kỳ giải thích hay định dạng markdown nào xung quanh nó.
"""
    system_msg = "Bạn là một AI chuyên gia phân tích cảm xúc văn bản, có khả năng xác định sắc thái và cung cấp điểm số cũng như từ khóa liên quan. Bạn sẽ trả lời bằng tiếng Việt theo định dạng JSON được yêu cầu."

    response_str = await generate_groq_response(api_key, prompt, system_message=system_msg, max_tokens=1024, temperature=0.3)

    try:
        # Thử tìm JSON trong phản hồi
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_str)
        if json_match:
            json_str = json_match.group(1)
        else:
            first_brace = response_str.find('{')
            last_brace = response_str.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = response_str[first_brace : last_brace+1]
            else:
                 return {"error": "AI did not return a clear JSON object for sentiment.", "raw_response": response_str}

        parsed_json = json.loads(json_str)
        return parsed_json
    except json.JSONDecodeError:
        return {"error": "AI returned content that is not valid JSON for sentiment.", "raw_response": response_str}
    except Exception as e:
        return {"error": f"An unexpected error occurred while parsing sentiment AI response: {str(e)}", "raw_response": response_str}