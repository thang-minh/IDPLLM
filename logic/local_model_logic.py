# logic/local_model_logic.py
import tensorflow as tf
import numpy as np
from PIL import Image
import os

# Cấu hình đường dẫn model (Sửa lại cho đúng với máy bạn nếu cần)
# Dựa trên ảnh bạn gửi, model nằm trong folder 'models'
# MODEL_PATH = "models/model_AI_documen/document_image_classifier.keras"
MODEL_PATH = "models/model_AI_documen/document_classifiers.keras"
CLASS_NAMES_PATH = "models/model_AI_documen/class_names.txt"

# Biến toàn cục để cache model (tránh load lại nhiều lần làm chậm)
_cached_model = None
_cached_class_names = None

def load_local_model():
    global _cached_model, _cached_class_names
    
    if _cached_model is None:
        if not os.path.exists(MODEL_PATH):
            return None, None, f"Không tìm thấy file model tại {MODEL_PATH}"
        
        try:
            print("Đang tải model từ đĩa...")
            _cached_model = tf.keras.models.load_model(MODEL_PATH)
            
            # Load class names
            if os.path.exists(CLASS_NAMES_PATH):
                with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
                    _cached_class_names = f.read().splitlines()
            else:
                # Fallback nếu không thấy file text, tự định nghĩa tạm
                _cached_class_names = ["Bien_ban", "Giay_to_khac", "Hoa_don", "Hop_dong", "So_yeu_ly_lich"] 
                
        except Exception as e:
            return None, None, str(e)
            
    return _cached_model, _cached_class_names, None

def predict_image_type(pil_image):
    """
    Dự đoán loại giấy tờ từ ảnh PIL sử dụng model local.
    """
    model, class_names, error = load_local_model()
    if error:
        return {"error": error}

    try:
        # 1. Tiền xử lý ảnh cho đúng chuẩn input của model (224x224)
        img = pil_image.resize((224, 224))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) # Tạo batch dimension (1, 224, 224, 3)

        # Lưu ý: Model train code của bạn đã có lớp Rescaling(1./255) bên trong,
        # nên ta không cần chia 255 ở đây nữa nếu input là 0-255.
        
        # 2. Dự đoán
        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0]) # Tính xác suất
        
        predicted_class_index = np.argmax(score)
        confidence = 100 * np.max(score)
        label_name = class_names[predicted_class_index]

        return {
            "label": label_name,
            "confidence": confidence,
            "details": {name: float(prob) * 100 for name, prob in zip(class_names, predictions[0])} # Trả về % của tất cả các lớp
        }
    except Exception as e:
        return {"error": f"Lỗi khi dự đoán: {str(e)}"}