# train_classifier.py
import os
from pathlib import Path
from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import accuracy_score

# --- CẤU HÌNH ---
MODEL_NAME = "vinai/phobert-base-v2"
DATA_PATH = "data/document_classification"
OUTPUT_DIR = "models/phobert_document_classifier"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_custom_dataset(data_path):
    data_path = Path(data_path)
    train_data = {"text": [], "label": []}
    test_data = {"text": [], "label": []}
    label_to_id = {}
    label_names = []

    for split in ["train", "test"]:
        split_path = data_path / split
        if not split_path.exists():
            raise ValueError(f"Không tìm thấy thư mục: {split_path}")

        for label_dir in split_path.iterdir():
            if not label_dir.is_dir():
                continue
            label_name = label_dir.name
            if label_name not in label_to_id:
                label_to_id[label_name] = len(label_to_id)
                label_names.append(label_name)

            label_id = label_to_id[label_name]

            for txt_file in label_dir.glob("*.txt"):
                try:
                    text = txt_file.read_text(encoding="utf-8").strip()
                    if not text:
                        continue
                    if split == "train":
                        train_data["text"].append(text)
                        train_data["label"].append(label_id)
                    else:
                        test_data["text"].append(text)
                        test_data["label"].append(label_id)
                except Exception as e:
                    print(f"Lỗi đọc {txt_file}: {e}")

    if not train_data["text"] or not test_data["text"]:
        raise ValueError("Không tìm thấy dữ liệu train hoặc test!")

    train_dataset = Dataset.from_dict(train_data)
    test_dataset = Dataset.from_dict(test_data)

    return DatasetDict({
        "train": train_dataset,
        "test": test_dataset
    }), label_names, label_to_id

def main():
    print("BẮT ĐẦU FINE-TUNING PHOBERT")

    # 1. TẢI DỮ LIỆU
    print(f"Đang tải dữ liệu từ '{DATA_PATH}'...")
    raw_datasets, label_names, label2id = load_custom_dataset(DATA_PATH)
    id2label = {i: name for name, i in label2id.items()}
    num_labels = len(label_names)

    print(f"Đã tìm thấy {num_labels} lớp: {label_names}")
    print(f"Train: {len(raw_datasets['train'])} mẫu | Test: {len(raw_datasets['test'])} mẫu")

    # 2. TOKENIZER
    print(f"Tải tokenizer '{MODEL_NAME}'...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def preprocess(examples):
        return tokenizer(examples["text"], truncation=True, padding=True, max_length=256)

    print("Đang tokenize...")
    tokenized = raw_datasets.map(preprocess, batched=True)

    # 3. MÔ HÌNH
    print(f"Tải mô hình '{MODEL_NAME}'...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        label2id=label2id,
        id2label=id2label
    )

    # 4. TRAINING ARGS 
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",           
        save_strategy="epoch",           
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_steps=10,
        save_total_limit=2,
        report_to=[],
        logging_dir="./logs",
        disable_tqdm=False,
    )

    # 5. ĐÁNH GIÁ
    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        preds = np.argmax(preds, axis=1)
        return {"accuracy": accuracy_score(labels, preds)}

    # 6. TRAINER
    print("Khởi tạo Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["test"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    print("BẮT ĐẦU HUẤN LUYỆN...")
    trainer.train()

    print(f"HOÀN TẤT! Lưu mô hình vào: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("MÔ HÌNH ĐÃ SẴN SÀNG!")

if __name__ == "__main__":
    main()