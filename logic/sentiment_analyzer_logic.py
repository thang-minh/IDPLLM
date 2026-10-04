# # logic/sentiment_analyzer_logic.py
# import json
# import re
# from .common_processing import generate_groq_response

# async def analyze_sentiment_with_groq(api_key: str, text_to_analyze: str) -> dict:
#     """
#     Analyzes sentiment of the given text using Groq.
#     Returns a dictionary with sentiment and explanation.
#     """
#     prompt = f"""
# Phân tích cảm xúc của đoạn văn bản sau.
# Hãy xác định cảm xúc chính (ví dụ: Rất tích cực, Tích cực, Trung tính, Tiêu cực, Rất tiêu cực).
# Cung cấp một điểm số cảm xúc từ -1.0 (rất tiêu cực) đến 1.0 (rất tích cực).
# Đưa ra một vài từ khóa chính hoặc cụm từ trong văn bản góp phần vào cảm xúc đó.
# Trả lời bằng tiếng Việt và định dạng kết quả dưới dạng JSON như sau:
# {{
#   "cam_xuc_chinh": "...",
#   "diem_so_cam_xuc": 0.0,
#   "tu_khoa_cam_xuc": ["...", "..."],
#   "giai_thich_ngan": "..."
# }}

# Đoạn văn bản cần phân tích:
# ---
# {text_to_analyze}
# ---
# CHỈ TRẢ VỀ ĐÚNG MỘT ĐỐI TƯỢNG JSON, không có bất kỳ giải thích hay định dạng markdown nào xung quanh nó.
# """
#     system_msg = "Bạn là một AI chuyên gia phân tích cảm xúc văn bản, có khả năng xác định sắc thái và cung cấp điểm số cũng như từ khóa liên quan. Bạn sẽ trả lời bằng tiếng Việt theo định dạng JSON được yêu cầu."

#     response_str = await generate_groq_response(api_key, prompt, system_message=system_msg, max_tokens=1024, temperature=0.3)

#     try:
#         # Thử tìm JSON trong phản hồi
#         json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_str)
#         if json_match:
#             json_str = json_match.group(1)
#         else:
#             first_brace = response_str.find('{')
#             last_brace = response_str.rfind('}')
#             if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
#                 json_str = response_str[first_brace : last_brace+1]
#             else:
#                  return {"error": "AI did not return a clear JSON object for sentiment.", "raw_response": response_str}

#         parsed_json = json.loads(json_str)
#         return parsed_json
#     except json.JSONDecodeError:
#         return {"error": "AI returned content that is not valid JSON for sentiment.", "raw_response": response_str}
#     except Exception as e:
#         return {"error": f"An unexpected error occurred while parsing sentiment AI response: {str(e)}", "raw_response": response_str}


# logic/sentiment_analyzer_logic.py

import json
import re
from typing import Dict, Any

from .common_processing import generate_groq_response


def extract_json_from_response(response_str: str) -> Dict[str, Any]:
    """
    Cố gắng lấy JSON hợp lệ từ phản hồi của LLM.
    """
    if not response_str:
        return {
            "error": "AI không trả về nội dung.",
            "raw_response": response_str
        }

    response_str = response_str.strip()

    try:
        return json.loads(response_str)
    except Exception:
        pass

    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_str)

    if json_match:
        json_str = json_match.group(1).strip()
    else:
        first_brace = response_str.find("{")
        last_brace = response_str.rfind("}")

        if first_brace == -1 or last_brace == -1 or last_brace <= first_brace:
            return {
                "error": "AI không trả về JSON rõ ràng.",
                "raw_response": response_str
            }

        json_str = response_str[first_brace:last_brace + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "error": "AI trả về nội dung không phải JSON hợp lệ.",
            "raw_response": response_str
        }


def normalize_sentiment_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuẩn hóa kết quả để UI luôn đọc được.
    """
    if "error" in data:
        return data

    score = data.get("diem_so_cam_xuc", 0.0)

    try:
        score = float(score)
    except Exception:
        score = 0.0

    score = max(-1.0, min(1.0, score))

    confidence = data.get("do_tin_cay", 0.0)

    try:
        confidence = float(confidence)
    except Exception:
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    keywords = data.get("tu_khoa_cam_xuc", [])

    if isinstance(keywords, str):
        keywords = [keywords]

    if not isinstance(keywords, list):
        keywords = []

    suggestions = data.get("goi_y_xu_ly", [])

    if isinstance(suggestions, str):
        suggestions = [suggestions]

    if not isinstance(suggestions, list):
        suggestions = []

    emotions = data.get("cam_xuc_phu", [])

    if isinstance(emotions, str):
        emotions = [emotions]

    if not isinstance(emotions, list):
        emotions = []

    return {
        "cam_xuc_chinh": data.get("cam_xuc_chinh", "Không xác định"),
        "cam_xuc_phu": emotions,
        "diem_so_cam_xuc": score,
        "do_tin_cay": confidence,
        "muc_do": data.get("muc_do", "Không xác định"),
        "tu_khoa_cam_xuc": keywords,
        "giai_thich_ngan": data.get("giai_thich_ngan", ""),
        "goi_y_xu_ly": suggestions,
        "ngon_ngu": data.get("ngon_ngu", "Không xác định")
    }


async def analyze_sentiment_with_groq(api_key: str, text_to_analyze: str) -> dict:
    """
    Phân tích cảm xúc văn bản bằng Groq/LLM.
    """
    if not api_key:
        return {
            "error": "Thiếu API key."
        }

    if not text_to_analyze or not text_to_analyze.strip():
        return {
            "error": "Văn bản đầu vào đang rỗng."
        }

    text_to_analyze = text_to_analyze.strip()

    prompt = f"""
Bạn là hệ thống phân tích cảm xúc văn bản tiếng Việt/tiếng Anh.

Hãy phân tích cảm xúc của đoạn văn bản bên dưới và trả về ĐÚNG MỘT JSON hợp lệ.
Không dùng markdown. Không giải thích ngoài JSON.

Schema bắt buộc:
{{
  "cam_xuc_chinh": "Rất tích cực | Tích cực | Trung tính | Tiêu cực | Rất tiêu cực",
  "cam_xuc_phu": ["các cảm xúc phụ nếu có"],
  "diem_so_cam_xuc": 0.0,
  "do_tin_cay": 0.0,
  "muc_do": "Nhẹ | Trung bình | Mạnh",
  "tu_khoa_cam_xuc": ["từ/cụm từ ảnh hưởng đến cảm xúc"],
  "giai_thich_ngan": "giải thích ngắn gọn bằng tiếng Việt",
  "goi_y_xu_ly": ["gợi ý phản hồi hoặc xử lý phù hợp"],
  "ngon_ngu": "Vietnamese | English | Mixed | Other"
}}

Quy tắc điểm:
- diem_so_cam_xuc nằm trong [-1.0, 1.0]
- -1.0 là rất tiêu cực
- 0.0 là trung tính
- 1.0 là rất tích cực
- do_tin_cay nằm trong [0.0, 1.0]
- Không tự bịa thông tin ngoài văn bản

Văn bản cần phân tích:
{text_to_analyze}
"""

    system_msg = (
        "Bạn là chuyên gia phân tích cảm xúc. "
        "Bạn chỉ trả về JSON hợp lệ theo schema được yêu cầu."
    )

    try:
        response_str = await generate_groq_response(
            api_key=api_key,
            prompt=prompt,
            system_message=system_msg,
            max_tokens=1200,
            temperature=0.2
        )

        parsed = extract_json_from_response(response_str)
        normalized = normalize_sentiment_result(parsed)

        return normalized

    except TypeError:
        # Fallback nếu generate_groq_response bản cũ không nhận system_message/max_tokens/temperature
        response_str = await generate_groq_response(api_key, prompt)
        parsed = extract_json_from_response(response_str)
        normalized = normalize_sentiment_result(parsed)

        return normalized

    except Exception as e:
        return {
            "error": f"Lỗi khi gọi AI phân tích cảm xúc: {str(e)}"
        }