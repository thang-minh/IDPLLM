# logic/image_classifier_logic.py
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os

# --- CẬP NHẬT ĐƯỜNG DẪN DỰA TRÊN HÌNH ẢNH CỦA BẠN ---
# Đường dẫn trỏ vào thư mục con 'model_AI_documen'
# MODEL_PATH = "models/model_AI_documen/document_image_classifier.keras"
MODEL_PATH = "models/model_AI_documen/document_classifiers.keras"
CLASS_NAMES_PATH = "models/model_AI_documen/class_names.txt"

@st.cache_resource
def load_image_classifier_model():
    """Tải mô hình Keras và danh sách tên các lớp."""
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASS_NAMES_PATH):
        st.error(f"Lỗi: Không tìm thấy file mô hình.\nĐường dẫn đang tìm: '{MODEL_PATH}' và '{CLASS_NAMES_PATH}'.\nHãy kiểm tra lại cấu trúc thư mục.")
        return None, None
    
    try:
        # Tải mô hình
        model = tf.keras.models.load_model(MODEL_PATH)
        
        # Tải tên các lớp (nhãn)
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            class_names = [line.strip() for line in f.readlines()]
            
        return model, class_names
    except Exception as e:
        st.error(f"Lỗi khi tải mô hình phân loại ảnh: {e}")
        return None, None

def classify_document_image(image: Image.Image):
    """
    Phân loại một ảnh tài liệu bằng mô hình đã huấn luyện.
    """
    model, class_names = load_image_classifier_model()
    if model is None or class_names is None:
        return "Lỗi tải mô hình", 0.0

    try:
        # Tiền xử lý ảnh (đảm bảo ảnh là 3 kênh màu RGB)
        img_rgb = image.convert("RGB")
        # Resize về kích thước mà mô hình yêu cầu (thường là 224x224 nếu dùng EfficientNet/MobileNet)
        img_resized = img_rgb.resize((224, 224)) 
        
        # Chuyển sang mảng numpy và thêm chiều batch
        img_array = tf.keras.utils.img_to_array(img_resized)
        img_array = tf.expand_dims(img_array, 0) 

        # Đưa ra dự đoán
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        
        # Lấy kết quả có xác suất cao nhất
        predicted_class = class_names[np.argmax(score)]
        confidence = 100 * np.max(score)

        return predicted_class.replace("_", " "), confidence
    except Exception as e:
        return f"Lỗi dự đoán: {e}", 0.0