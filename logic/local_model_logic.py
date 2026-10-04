# # logic/local_model_logic.py
# import tensorflow as tf
# import numpy as np
# from PIL import Image
# import os

# # Cấu hình đường dẫn model (Sửa lại cho đúng với máy bạn nếu cần)
# # MODEL_PATH = "models/model_AI_documen/document_image_classifier.keras"
# MODEL_PATH = "models/model_AI_documen/best_document_image_classifier_2classes.keras"
# CLASS_NAMES_PATH = "models/model_AI_documen/class_names.txt"

# # Biến toàn cục để cache model (tránh load lại nhiều lần làm chậm)
# _cached_model = None
# _cached_class_names = None

# def load_local_model():
#     global _cached_model, _cached_class_names
    
#     if _cached_model is None:
#         if not os.path.exists(MODEL_PATH):
#             return None, None, f"Không tìm thấy file model tại {MODEL_PATH}"
        
#         try:
#             print("Đang tải model từ đĩa...")
#             _cached_model = tf.keras.models.load_model(MODEL_PATH)
            
#             # Load class names
#             if os.path.exists(CLASS_NAMES_PATH):
#                 with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
#                     _cached_class_names = f.read().splitlines()
#             else:
#                 # Fallback nếu không thấy file text, tự định nghĩa tạm
#                 _cached_class_names = ["Bien_ban", "Giay_to_khac", "Hoa_don", "Hop_dong", "So_yeu_ly_lich"] 
                
#         except Exception as e:
#             return None, None, str(e)
            
#     return _cached_model, _cached_class_names, None

# def predict_image_type(pil_image):
#     """
#     Dự đoán loại giấy tờ từ ảnh PIL sử dụng model local.
#     """
#     model, class_names, error = load_local_model()
#     if error:
#         return {"error": error}

#     try:
#         # 1. Tiền xử lý ảnh cho đúng chuẩn input của model (224x224)
#         img = pil_image.resize((224, 224))
#         img_array = tf.keras.utils.img_to_array(img)
#         img_array = tf.expand_dims(img_array, 0) # Tạo batch dimension (1, 224, 224, 3)

#         # Lưu ý: Model train code của bạn đã có lớp Rescaling(1./255) bên trong,
#         # nên ta không cần chia 255 ở đây nữa nếu input là 0-255.
        
#         # 2. Dự đoán
#         predictions = model.predict(img_array)
#         score = tf.nn.softmax(predictions[0]) # Tính xác suất
        
#         predicted_class_index = np.argmax(score)
#         confidence = 100 * np.max(score)
#         label_name = class_names[predicted_class_index]

#         return {
#             "label": label_name,
#             "confidence": confidence,
#             "details": {name: float(prob) * 100 for name, prob in zip(class_names, predictions[0])} # Trả về % của tất cả các lớp
#         }
#     except Exception as e:
#         return {"error": f"Lỗi khi dự đoán: {str(e)}"}

# logic/local_model_logic.py

import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


# =========================================================
# CONFIG
# =========================================================

MODEL_PATH = Path("models/model_AI_documen/best_document_image_classifier_2classes.keras")
CLASS_NAMES_PATH = Path("models/model_AI_documen/class_names.txt")

IMG_SIZE = (224, 224)

_cached_model = None
_cached_class_names = None


# =========================================================
# LOAD MODEL
# =========================================================

def load_local_model():
    """
    Load model ảnh EfficientNetV2B0 và class_names.txt.
    Dùng biến cache toàn cục để tránh load model nhiều lần.
    """
    global _cached_model, _cached_class_names

    if _cached_model is not None and _cached_class_names is not None:
        return _cached_model, _cached_class_names, None

    if not MODEL_PATH.exists():
        return None, None, f"Không tìm thấy file model tại: {MODEL_PATH}"

    if not CLASS_NAMES_PATH.exists():
        return None, None, f"Không tìm thấy file class_names tại: {CLASS_NAMES_PATH}"

    try:
        _cached_model = tf.keras.models.load_model(str(MODEL_PATH))

        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            _cached_class_names = [
                line.strip()
                for line in f.readlines()
                if line.strip()
            ]

        if not _cached_class_names:
            return None, None, "File class_names.txt đang rỗng."

        output_units = int(_cached_model.output_shape[-1])

        if output_units != len(_cached_class_names):
            return None, None, (
                f"Số output của model là {output_units}, "
                f"nhưng class_names.txt có {len(_cached_class_names)} nhãn. "
                f"Hãy kiểm tra lại thứ tự class_names.txt."
            )

        return _cached_model, _cached_class_names, None

    except Exception as e:
        return None, None, f"Lỗi khi load model ảnh: {str(e)}"


# =========================================================
# PREPROCESS
# =========================================================

def preprocess_image_for_model(pil_image):
    """
    Chuẩn hóa ảnh về đúng format model:
    - PIL Image
    - RGB 3 channels
    - Resize 224x224
    - Batch shape: (1, 224, 224, 3)

    Fix lỗi phổ biến:
    Incompatible shapes: [1,224,224,4] vs [1,1,1,3]
    do ảnh PNG/RGBA có 4 kênh.
    """
    if isinstance(pil_image, np.ndarray):
        pil_image = Image.fromarray(pil_image)

    if not isinstance(pil_image, Image.Image):
        raise ValueError("Input phải là PIL.Image hoặc numpy array.")

    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    pil_image = pil_image.resize(IMG_SIZE)

    img_array = tf.keras.utils.img_to_array(pil_image)

    if img_array.ndim != 3 or img_array.shape[-1] != 3:
        raise ValueError(f"Ảnh sau xử lý có shape không hợp lệ: {img_array.shape}")

    img_array = np.expand_dims(img_array, axis=0).astype("float32")

    return img_array


def normalize_predictions(predictions):
    """
    Chuẩn hóa output model thành xác suất.
    Nếu model đã có softmax thì dùng trực tiếp.
    Nếu model trả logits thì áp dụng softmax.
    """
    predictions = np.asarray(predictions, dtype="float32")

    pred_sum = float(np.sum(predictions))
    pred_min = float(np.min(predictions))
    pred_max = float(np.max(predictions))

    if 0.99 <= pred_sum <= 1.01 and pred_min >= 0 and pred_max <= 1:
        return predictions

    return tf.nn.softmax(predictions).numpy()


# =========================================================
# PREDICT
# =========================================================

def predict_image_type(pil_image):
    """
    Dự đoán loại ảnh tài liệu bằng model ảnh local.

    Return:
    {
        "label": "Hoa_don",
        "display_label": "Hoa don",
        "confidence": 98.5,
        "details": {
            "Hoa_don": 98.5,
            "So_yeu_ly_lich": 1.5
        }
    }
    """
    model, class_names, error = load_local_model()

    if error:
        return {"error": error}

    try:
        img_array = preprocess_image_for_model(pil_image)

        predictions = model.predict(img_array, verbose=0)[0]
        probabilities = normalize_predictions(predictions)

        predicted_index = int(np.argmax(probabilities))
        label_name = class_names[predicted_index]
        confidence = float(probabilities[predicted_index] * 100)

        details = {
            class_names[i]: float(probabilities[i] * 100)
            for i in range(len(class_names))
        }

        return {
            "label": label_name,
            "display_label": label_name.replace("_", " "),
            "confidence": confidence,
            "details": details
        }

    except Exception as e:
        return {
            "error": f"Lỗi khi dự đoán ảnh: {str(e)}"
        }


def clear_local_model_cache():
    """
    Dùng khi cần reload model sau khi thay file .keras hoặc class_names.txt.
    """
    global _cached_model, _cached_class_names
    _cached_model = None
    _cached_class_names = None