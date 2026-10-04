# # logic/document_classifier_logic.py
# import streamlit as st
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch

# # Đường dẫn đến mô hình đã được fine-tune
# MODEL_PATH = "models/phobert_document_classifier"

# @st.cache_resource # RẤT QUAN TRỌNG: Dùng cache để load model chỉ một lần
# def load_phobert_model_and_tokenizer():
#     """
#     Load mô hình PhoBERT đã fine-tune và tokenizer.
#     Hàm này được cache lại để tăng hiệu năng.
#     """
#     try:
#         tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
#         model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
#         return model, tokenizer
#     except Exception as e:
#         # Nếu không load được model, có thể là do chưa train
#         st.error(f"Lỗi khi tải mô hình phân loại tự huấn luyện: {e}. Vui lòng chạy script 'train_classifier.py' trước.")
#         return None, None

# def classify_document_phobert(text: str):
#     """
#     Phân loại một đoạn văn bản sử dụng mô hình PhoBERT đã fine-tune.
#     """
#     model, tokenizer = load_phobert_model_and_tokenizer()
    
#     if model is None or tokenizer is None:
#         return "Lỗi: Không thể tải mô hình."

#     # Tiền xử lý và tokenization
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)

#     # Đưa ra dự đoán
#     with torch.no_grad(): # Không cần tính gradient khi dự đoán
#         logits = model(**inputs).logits
    
#     # Lấy nhãn có xác suất cao nhất
#     predicted_class_id = logits.argmax().item()
    
#     # Chuyển ID thành tên nhãn
#     predicted_label = model.config.id2label[predicted_class_id]
    
#     return predicted_label.replace("_", " ") # Trả về tên nhãn đã được làm đẹp

# logic/document_classifier_logic.py

import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


MODEL_PATH = "models/phobert_document_classifier"
MAX_LENGTH = 256


@st.cache_resource
def load_phobert_model_and_tokenizer():
    """
    Load mô hình PhoBERT đã fine-tune và tokenizer.
    Cache giúp model chỉ load một lần trong Streamlit.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        model.eval()
        return model, tokenizer
    except Exception as e:
        st.error(
            f"Lỗi khi tải mô hình phân loại PhoBERT: {e}. "
            f"Vui lòng kiểm tra thư mục model: {MODEL_PATH}"
        )
        return None, None


def classify_document_phobert(text: str):
    """
    Phân loại văn bản bằng PhoBERT fine-tune.

    Output:
    {
        "label": "Hoa_don_GTGT",
        "display_label": "Hoa don GTGT",
        "confidence": 0.98,
        "probabilities": {
            "Bien_ban_hop": 0.01,
            "Hoa_don_GTGT": 0.98,
            "Hop_dong_lao_dong": 0.01
        }
    }
    """
    model, tokenizer = load_phobert_model_and_tokenizer()

    if model is None or tokenizer is None:
        return {
            "error": "Không thể tải mô hình PhoBERT."
        }

    if not text or not text.strip():
        return {
            "error": "Văn bản đầu vào đang rỗng."
        }

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=1)[0]

    predicted_class_id = torch.argmax(probs).item()
    predicted_label = model.config.id2label[predicted_class_id]
    confidence = probs[predicted_class_id].item()

    probabilities = {}

    for idx, prob in enumerate(probs):
        label_name = model.config.id2label[idx]
        probabilities[label_name] = float(prob.item())

    return {
        "label": predicted_label,
        "display_label": predicted_label.replace("_", " "),
        "confidence": confidence,
        "probabilities": probabilities
    }