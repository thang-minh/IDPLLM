# export_contract_only.py
import os
import random
from pathlib import Path
from datasets import load_dataset

HF_TOKEN = os.getenv("HF_TOKEN")
CACHE_DIR = r"D:\HF_CACHE"
MAX_DOCS = 300           # số hợp đồng (mỗi hợp đồng có nhiều trang)
TRAIN_RATIO = 0.8

BASE_DIR = Path(__file__).resolve().parent
TRAIN_DIR = BASE_DIR / "data_images" / "train" / "Hop_dong"
VAL_DIR = BASE_DIR / "data_images" / "validation" / "Hop_dong"

DATASET_NAME = "chenghao/sec-material-contracts-qa-splitted"
SPLIT = "train"


def export_contract():
    print(f"\n=== EXPORT ẢNH HỢP ĐỒNG ({DATASET_NAME}) ===")

    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    # Load dataset
    ds = load_dataset(
        DATASET_NAME,
        split=SPLIT,
        token=HF_TOKEN,
        cache_dir=CACHE_DIR
    )

    if len(ds) == 0:
        print("[WARN] Dataset rỗng.")
        return

    # Dataset này dùng cột "images" (LIST ảnh)
    image_col = "images"

    if image_col not in ds.column_names:
        print(f"[ERROR] Không thấy cột '{image_col}'")
        return

    total_docs = min(len(ds), MAX_DOCS)
    num_train = int(total_docs * TRAIN_RATIO)
    num_val = total_docs - num_train

    indices = list(range(total_docs))
    random.shuffle(indices)

    print(f"[INFO] Số hợp đồng lấy: {total_docs} (train {num_train}, val {num_val})")

    for i, idx in enumerate(indices):
        doc = ds[idx]
        pages = doc[image_col]    # LIST ảnh

        for page_idx, img in enumerate(pages):
            if img is None:
                continue

            # train hay val
            if i < num_train:
                out_path = TRAIN_DIR / f"Hop_dong_{i:04d}_p{page_idx}.jpg"
            else:
                out_path = VAL_DIR / f"Hop_dong_{i - num_train:04d}_p{page_idx}.jpg"

            img.save(out_path)

        if i % 20 == 0:
            print(f"[INFO] Export {i}/{total_docs} hợp đồng...")

    print("\n=== XUẤT ẢNH HỢP ĐỒNG HOÀN TẤT ✔ ===")


if __name__ == "__main__":
    export_contract()
