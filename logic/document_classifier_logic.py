# logic/document_classifier_logic.py
import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Đường dẫn đến mô hình đã được fine-tune
MODEL_PATH = "models/phobert_document_classifier"

@st.cache_resource # RẤT QUAN TRỌNG: Dùng cache để load model chỉ một lần
def load_phobert_model_and_tokenizer():
    """
    Load mô hình PhoBERT đã fine-tune và tokenizer.
    Hàm này được cache lại để tăng hiệu năng.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        return model, tokenizer
    except Exception as e:
        # Nếu không load được model, có thể là do chưa train
        st.error(f"Lỗi khi tải mô hình phân loại tự huấn luyện: {e}. Vui lòng chạy script 'train_classifier.py' trước.")
        return None, None

def classify_document_phobert(text: str):
    """
    Phân loại một đoạn văn bản sử dụng mô hình PhoBERT đã fine-tune.
    """
    model, tokenizer = load_phobert_model_and_tokenizer()
    
    if model is None or tokenizer is None:
        return "Lỗi: Không thể tải mô hình."

    # Tiền xử lý và tokenization
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)

    # Đưa ra dự đoán
    with torch.no_grad(): # Không cần tính gradient khi dự đoán
        logits = model(**inputs).logits
    
    # Lấy nhãn có xác suất cao nhất
    predicted_class_id = logits.argmax().item()
    
    # Chuyển ID thành tên nhãn
    predicted_label = model.config.id2label[predicted_class_id]
    
    return predicted_label.replace("_", " ") # Trả về tên nhãn đã được làm đẹp