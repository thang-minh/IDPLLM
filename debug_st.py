import sys
import traceback

print(f"--- Đang chạy trên Python: {sys.executable} ---")

print("\n1. Thử import TORCH...")
try:
    import torch
    print(f"✅ OK! Torch version: {torch.__version__}")
except ImportError:
    print("❌ LỖI IMPORT TORCH!")
    traceback.print_exc()
except Exception:
    print("❌ LỖI KHÁC KHI LOAD TORCH:")
    traceback.print_exc()

print("\n2. Thử import SENTENCE_TRANSFORMERS...")
try:
    import sentence_transformers
    from sentence_transformers import SentenceTransformer
    print(f"✅ OK! SentenceTransformers version: {sentence_transformers.__version__}")
except ImportError:
    print("❌ LỖI IMPORT SENTENCE_TRANSFORMERS!")
    traceback.print_exc()
except Exception:
    print("❌ LỖI KHÁC KHI LOAD SENTENCE_TRANSFORMERS:")
    traceback.print_exc()