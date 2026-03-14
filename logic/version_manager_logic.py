# logic/version_manager_logic.py
import os
import json
from datetime import datetime
import shutil # For restoring

# Thư mục gốc để lưu các phiên bản, có thể cấu hình qua .env nếu muốn
VERSIONS_ROOT_DIR = "document_versions"
os.makedirs(VERSIONS_ROOT_DIR, exist_ok=True)

def get_doc_versions_path(doc_id: str) -> str:
    """Trả về đường dẫn đến thư mục chứa các phiên bản của một doc_id."""
    return os.path.join(VERSIONS_ROOT_DIR, doc_id)

def save_version(doc_id: str, file_data: bytes, metadata: dict, analysis_results: dict = None) -> str:
    """
    Lưu một phiên bản mới của tài liệu.
    Tạo một thư mục con với timestamp là tên.
    Lưu file PDF, file metadata.json, và file analysis.json (nếu có).
    """
    if not doc_id.strip():
        raise ValueError("Document ID không được để trống.")

    doc_path = get_doc_versions_path(doc_id)
    os.makedirs(doc_path, exist_ok=True)

    version_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    version_dir = os.path.join(doc_path, version_timestamp)
    os.makedirs(version_dir, exist_ok=True)

    # Lưu file PDF
    pdf_filename = metadata.get("original_filename", f"{doc_id}.pdf")
    # Đảm bảo tên file an toàn
    safe_pdf_filename = "".join(c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in pdf_filename)
    if not safe_pdf_filename.lower().endswith(".pdf"):
        safe_pdf_filename += ".pdf"

    pdf_path = os.path.join(version_dir, safe_pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(file_data)

    # Lưu metadata
    metadata["_version_id"] = version_timestamp # Thêm version_id vào metadata
    metadata["_pdf_filename"] = safe_pdf_filename # Lưu tên file PDF đã lưu
    metadata_path = os.path.join(version_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    # Lưu kết quả phân tích (nếu có)
    if analysis_results:
        analysis_path = os.path.join(version_dir, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=4)
            
    return version_dir # Trả về đường dẫn đến thư mục phiên bản vừa lưu

def list_versions(doc_id: str) -> list:
    """Liệt kê các ID phiên bản (timestamp) đã lưu cho một doc_id, sắp xếp mới nhất trước."""
    if not doc_id.strip(): return []
    doc_path = get_doc_versions_path(doc_id)
    if not os.path.exists(doc_path):
        return []
    
    versions = [d for d in os.listdir(doc_path) if os.path.isdir(os.path.join(doc_path, d))]
    # Sắp xếp theo timestamp giảm dần (mới nhất trước)
    versions.sort(reverse=True)
    return versions

def load_version(doc_id: str, version_id: str) -> dict:
    """
    Tải thông tin của một phiên bản cụ thể.
    Trả về dict chứa "metadata", "analysis" (nếu có), và "pdf_path".
    """
    if not doc_id.strip() or not version_id.strip():
        raise ValueError("Document ID và Version ID không được để trống.")

    version_dir = os.path.join(get_doc_versions_path(doc_id), version_id)
    if not os.path.exists(version_dir) or not os.path.isdir(version_dir):
        raise FileNotFoundError(f"Không tìm thấy thư mục phiên bản: {version_dir}")

    data = {}
    # Tải metadata
    metadata_path = os.path.join(version_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            data["metadata"] = json.load(f)
    else:
        data["metadata"] = {"error": "Không tìm thấy file metadata.json"}

    # Tải analysis
    analysis_path = os.path.join(version_dir, "analysis.json")
    if os.path.exists(analysis_path):
        with open(analysis_path, "r", encoding="utf-8") as f:
            data["analysis"] = json.load(f)
    else:
        data["analysis"] = None # Hoặc {} tùy bạn muốn

    # Lấy đường dẫn PDF
    # Tên file PDF được lưu trong metadata khi save_version
    pdf_filename_in_meta = data.get("metadata", {}).get("_pdf_filename")
    if pdf_filename_in_meta:
        data["pdf_path"] = os.path.join(version_dir, pdf_filename_in_meta)
    else: # Fallback: tìm file .pdf đầu tiên nếu không có trong metadata (không khuyến khích)
        found_pdf = [f for f in os.listdir(version_dir) if f.lower().endswith(".pdf")]
        if found_pdf:
            data["pdf_path"] = os.path.join(version_dir, found_pdf[0])
        else:
            data["pdf_path"] = None
            data["metadata"]["error"] = data["metadata"].get("error","") + " Không tìm thấy file PDF."


    if not data.get("pdf_path") or not os.path.exists(data["pdf_path"]):
         data["pdf_path"] = None # Đảm bảo trả về None nếu file không tồn tại

    return data


def restore_version(doc_id: str, version_id: str, restore_base_path: str = "./restored_documents") -> str:
    """
    Phục hồi một phiên bản PDF ra một đường dẫn cụ thể.
    Tạo thư mục restore_base_path nếu chưa có.
    """
    if not doc_id.strip() or not version_id.strip():
        raise ValueError("Document ID và Version ID không được để trống.")

    version_data = load_version(doc_id, version_id)
    pdf_path_to_restore = version_data.get("pdf_path")

    if not pdf_path_to_restore or not os.path.exists(pdf_path_to_restore):
        raise FileNotFoundError(f"Không tìm thấy file PDF của phiên bản {version_id} cho tài liệu {doc_id}.")

    os.makedirs(restore_base_path, exist_ok=True)
    
    # Tạo tên file phục hồi duy nhất hơn
    original_filename = version_data.get("metadata", {}).get("_pdf_filename", f"{doc_id}_{version_id}.pdf")
    restore_filename = f"RESTORED_{version_id}_{original_filename}"
    
    destination_path = os.path.join(restore_base_path, restore_filename)
    
    try:
        shutil.copy2(pdf_path_to_restore, destination_path) # copy2 giữ metadata file
        return destination_path
    except Exception as e:
        raise IOError(f"Lỗi khi sao chép file để phục hồi: {e}")