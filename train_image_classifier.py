# train_image_classifier.py
import os
import random
from pathlib import Path

from datasets import load_dataset
import tensorflow as tf
from tensorflow.keras import layers, models

# ==========================
# CẤU HÌNH ĐƯỜNG DẪN TRÊN Ổ D
# ==========================
# Nếu project không nằm ở D:\AI_Document_Classifier
# thì sửa lại BASE_DIR cho đúng thư mục trên ổ D:
BASE_DIR = Path(r"D:\AI_Document_Classifier")

DATA_DIR = BASE_DIR / "data_images"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "validation"
MODEL_DIR = BASE_DIR / "models"

# Cache HuggingFace trên ổ D:
CACHE_DIR = Path(r"D:\HF_CACHE")

# ==========================
# CẤU HÌNH HUẤN LUYỆN
# ==========================
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15

TRAIN_RATIO = 0.8
MAX_IMAGES_PER_CLASS = 300  # tối đa số mẫu mỗi loại khi export (đủ xài là được)

HF_TOKEN = os.getenv("HF_TOKEN")  # set trong terminal: $env:HF_TOKEN="hf_xxx"


# ==========================
# HÀM EXPORT ẢNH TỪ DATASET HF
# ==========================

def export_from_hf(dataset_name, split, class_name, multi_page=False, max_docs=None):
    """
    Export ảnh từ HuggingFace về data_images/train & data_images/validation.

    - multi_page = False: mỗi sample có 1 ảnh (cột "image")
    - multi_page = True: mỗi sample là 1 list ảnh (cột "images"), ví dụ hợp đồng nhiều trang
    """

    train_out = TRAIN_DIR / class_name
    val_out = VAL_DIR / class_name
    train_out.mkdir(parents=True, exist_ok=True)
    val_out.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Đang tải dataset {dataset_name} cho class '{class_name}' ...")

    ds = load_dataset(
        dataset_name,
        split=split,
        token=HF_TOKEN,
        cache_dir=str(CACHE_DIR)  # cache trên ổ D
    )

    if len(ds) == 0:
        print(f"[WARN] Dataset {dataset_name} rỗng, bỏ qua class '{class_name}'.")
        return

    # Số "hợp đồng"/mẫu gốc sẽ dùng
    total_docs = len(ds)
    if max_docs is not None:
        total_docs = min(total_docs, max_docs)

    num_train_docs = int(total_docs * TRAIN_RATIO)
    num_val_docs = total_docs - num_train_docs

    indices = list(range(total_docs))
    random.seed(42)
    random.shuffle(indices)
    indices = indices[:total_docs]

    print(f"[INFO] Tổng mẫu sẽ dùng cho '{class_name}': {total_docs} "
          f"(train: {num_train_docs}, val: {num_val_docs})")

    exported = 0

    for doc_idx, idx in enumerate(indices):
        item = ds[idx]

        # ---- MỖI SAMPLE CÓ 1 ẢNH ----
        if not multi_page:
            img = item["image"]
            imgs = [img]  # convert thành list cho thống nhất
        # ---- MỖI SAMPLE LÀ LIST ẢNH (images[]) ----
        else:
            imgs = item["images"]  # list ảnh (các trang hợp đồng)

        # train hay val theo doc_idx
        is_train = doc_idx < num_train_docs
        base_dir = train_out if is_train else val_out
        doc_id = doc_idx if is_train else (doc_idx - num_train_docs)

        for page_idx, img in enumerate(imgs):
            out_name = f"{class_name}_{doc_id:04d}_p{page_idx}.jpg"
            out_path = base_dir / out_name
            img.save(out_path)
            exported += 1

        if doc_idx % 20 == 0:
            print(f"[INFO] Đã xử lý {doc_idx}/{total_docs} mẫu cho '{class_name}'...")

    print(f"[DONE] Export xong {exported} ảnh cho class '{class_name}' ✔")


def export_all_datasets():
    """Chỉ export nếu chưa có thư mục train."""
    if TRAIN_DIR.exists():
        print("[INFO] Đã có data_images/train → bỏ qua bước export HuggingFace.")
        return

    print("===== BẮT ĐẦU EXPORT DATASET VỀ Ổ D =====")

    # 1. HÓA ĐƠN: 1 ảnh / sample, cột "image"
    export_from_hf(
        dataset_name="5CD-AI/Viet-Receipt-VQA",
        split="train",
        class_name="Hoa_don",
        multi_page=False,
        max_docs=MAX_IMAGES_PER_CLASS
    )

    # 2. SƠ YẾU LÝ LỊCH: 1 ảnh / sample, cột "image"
    export_from_hf(
        dataset_name="5CD-AI/Viet-Resume-VQA",
        split="train",
        class_name="So_yeu_ly_lich",
        multi_page=False,
        max_docs=MAX_IMAGES_PER_CLASS
    )

    # 3. HỢP ĐỒNG: mỗi sample là list ảnh (cột "images")
    export_from_hf(
        dataset_name="chenghao/sec-material-contracts-qa-splitted",
        split="train",
        class_name="Hop_dong",
        multi_page=True,
        max_docs=MAX_IMAGES_PER_CLASS
    )

    print("===== EXPORT DATASET HOÀN TẤT =====")


# ==========================
# HÀM HUẤN LUYỆN MODEL
# ==========================

def train_model():
    print("\n===== BẮT ĐẦU HUẤN LUYỆN =====")
    print(f"[INFO] Load ảnh từ: {TRAIN_DIR} và {VAL_DIR}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    class_names = train_ds.class_names
    print("[INFO] Các lớp:", class_names)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
    val_ds = val_ds.cache().prefetch(AUTOTUNE)

    # Data augmentation đơn giản
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.05),
    ])

    # Transfer learning với EfficientNet
    base_model = tf.keras.applications.EfficientNetV2B0(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    model = tf.keras.Sequential([
        layers.Rescaling(1. / 255),
        data_augmentation,
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.2),
        layers.Dense(len(class_names), activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "document_image_classifier.keras"
    model.save(model_path)

    with open(MODEL_DIR / "class_names.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(class_names))

    print(f"\n===== HUẤN LUYỆN XONG =====")
    print(f"[INFO] Model lưu tại: {model_path}")
    print(f"[INFO] Class list lưu tại: {MODEL_DIR / 'class_names.txt'}")


# ==========================
# MAIN
# ==========================

def main():
    # B1: export dataset về ổ D nếu chưa có
    export_all_datasets()
    # B2: train model
    train_model()


if __name__ == "__main__":
    main()
