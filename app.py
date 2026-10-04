# # app.py
# import streamlit as st
# import os
# from dotenv import load_dotenv
# import nltk
# import pytesseract # Chỉ import ở đây để cấu hình path
# from datetime import datetime

# POPPLER_PATH_ENV_CONFIG = os.getenv("POPPLER_PATH")


# # --- CONFIG BAN ĐẦU (PHẢI LÀ LỆNH STREAMLIT ĐẦU TIÊN) ---
# st.set_page_config(
#     page_title="SmartDoc - Trợ lý Tài liệu Thông minh",
#     page_icon="",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://www.example.com/help', # Thay bằng link của bạn
#         'Report a bug': "https://www.example.com/bug", # Thay bằng link của bạn
#         'About': "# SmartDoc AI \nPhiên bản 1.0\nPhát triển để hỗ trợ xử lý tài liệu thông minh."
#     }
# )

# # --- SETUP BIẾN MÔI TRƯỜNG VÀ ĐƯỜNG DẪN ---
# load_dotenv()

# # Cấu hình Tesseract OCR
# TESSERACT_PATH_ENV = os.getenv("TESSERACT_CMD")
# tesseract_found = False
# if TESSERACT_PATH_ENV and os.path.exists(TESSERACT_PATH_ENV):
#     pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH_ENV
#     tesseract_found = True
# elif os.name == 'nt': # Windows
#     common_paths = [r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe", r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"]
#     for path in common_paths:
#         if os.path.exists(path):
#             pytesseract.pytesseract.tesseract_cmd = path
#             TESSERACT_PATH_ENV = path # Cập nhật để biết là đã tìm thấy
#             tesseract_found = True
#             break

# # Cấu hình Poppler (chủ yếu cho pdf2image trên Windows)
# POPPLER_PATH_ENV_CONFIG = os.getenv("POPPLER_PATH") # Thường trỏ đến thư mục cha của 'bin' (vd: C:\poppler-24.02.0\Library)
# # Logic tìm 'bin' từ POPPLER_PATH_ENV_CONFIG sẽ nằm trong common_processing.convert_pdf_to_images

# # API Keys
# OPENROUTER_API_KEY_ENV = os.getenv("OPENROUTER_API_KEY")
# GROQ_API_KEY_ENV = os.getenv("GROQ_API_KEY")
# # Ưu tiên Groq API key nếu có
# API_KEY_CONFIG = GROQ_API_KEY_ENV if GROQ_API_KEY_ENV else OPENROUTER_API_KEY_ENV

# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:  # <--- THAY ĐỔI Ở ĐÂY
#     print("Downloading NLTK 'punkt' tokenizer...") # Thêm print để theo dõi nếu chạy từ console
#     nltk.download('punkt', quiet=False) # quiet=False để xem output nếu có lỗi tải
#     print("'punkt' downloaded.")
# try:
#     nltk.data.find('corpora/wordnet')
# except LookupError:  # <--- THAY ĐỔI Ở ĐÂY
#     print("Downloading NLTK 'wordnet' resource...")
#     nltk.download('wordnet', quiet=False)
#     print("'wordnet' downloaded.")
# try:
#     nltk.data.find('corpora/omw-1.4') # Một số mô hình wordnet tiếng Việt cần cái này
# except LookupError:
#     print("Downloading NLTK 'omw-1.4' resource...")
#     nltk.download('omw-1.4', quiet=False)
#     print("'omw-1.4' downloaded.")



# # --- IMPORT CÁC MODULE UI VÀ LOGIC ---
# # (Import sau khi các biến môi trường và path đã được load/xử lý)
# # UI Modules
# from ui_modules.main_smartdoc_ui import show_main_smartdoc_ui
# from ui_modules.form_extractor_ui import show_form_extractor_ui
# from ui_modules.sentiment_analyzer_ui import show_sentiment_analyzer_ui
# from ui_modules.table_extractor_ui import show_table_extractor_ui
# from ui_modules.compare_module_ui import show_compare_module_ui
# from ui_modules.pdf_signer_ui import show_pdf_signer_ui
# from ui_modules.version_manager_ui import show_version_manager_ui
# from ui_modules.multi_doc_qna_ui import show_multi_doc_qna_ui # <--- ĐẢM BẢO DÒNG NÀY CÓ VÀ ĐÚNG
# from ui_modules.translator_ui import show_translator_ui # <--- ĐẢM BẢO DÒNG NÀY CÓ VÀ ĐÚNG
# from ui_modules.pdf_merge_ui import show_pdf_merge_ui     # <<<<----- THÊM IMPORT NÀY
# from ui_modules.pdf_split_ui import show_pdf_split_ui     # <<<<----- THÊM IMPORT NÀY
# from ui_modules.pdf_watermark_ui import show_pdf_watermark_ui # <<<<----- THÊM IMPORT NÀY
# from ui_modules.pdf_unlock_ui import show_pdf_unlock_ui       # <<<<----- THÊM IMPORT NÀY
# from ui_modules.pdf_protect_ui import show_pdf_protect_ui     # <<<<----- THÊM IMPORT NÀY
# from ui_modules.pdf_editor_ui import show_pdf_editor_ui # <<<<----- THÊM IMPORT NÀY
# from ui_modules.converter_ui import show_converter_ui  # <--- THÊM DÒNG NÀY
# from ui_modules.pdf_redaction_ui import show_pdf_redaction_ui
# from ui_modules.knowledge_graph_ui import show_knowledge_graph_ui

# # Utility UI Modules
# from ui_utils.dark_mode import manage_dark_mode
# from ui_utils.quotes import get_random_quote
# # --- SIDEBAR ---
# with st.sidebar:
#     # Thêm logo nếu có file logo.png trong thư mục gốc
#     if os.path.exists("logo.png"):
#         st.image("logo.png", width=100, use_column_width='auto')
#     else:
#         st.markdown("<h1 style='text-align: center; font-weight: bold; font-size: 28px;'>🧰</h1>", unsafe_allow_html=True)

#     st.markdown("<h1 style='text-align: center; font-weight: bold;'>SmartDoc AI</h1>", unsafe_allow_html=True)
#     st.caption(f"<p style='text-align: center;'>{get_random_quote()}</p>", unsafe_allow_html=True)
#     st.markdown("---")

#     manage_dark_mode() # Checkbox bật/tắt dark mode
#     st.markdown("---")

#     st.header("Chọn Chức Năng")
#     app_mode = st.radio(
#         "Công cụ:",
#         [
#             "Trí tuệ Tài liệu (PDF)",
#             "Trích xuất Form (Ảnh)",
#             "Phân tích Cảm xúc",
#             "Trích xuất Bảng (PDF)",
#             "Biên tập PDF Cơ bản",
#             "Ký PDF",
#             "Ghép PDF",                
#             "Tách PDF", 
#             "Công cụ Chuyển đổi Tài liệu (Local)",
#             "Đóng dấu Watermark PDF",
#             "Hỏi đáp Đa Tài liệu",
#             "Dịch Văn bản",
#             "So sánh Tài liệu (Ảnh)",
#             "Mở khóa PDF",            
#             "Bảo vệ PDF" ,
#             "Knowledge Graph (Mới)",
#             "Redaction AI (Che thông tin)",
#             "Quản lý Phiên bản"
        
#         ],
#         label_visibility="collapsed",
#         key="app_mode_selector"
#     )
    
#     st.markdown("---")
#     with st.expander("ℹ️ Thông tin Hệ thống", expanded=False):
#         st.info(f"Tesseract OCR: {'Sẵn sàng' if tesseract_found else ' Không tìm thấy/cấu hình'}")
#         st.info(f"Poppler Path: {'Đã cấu hình trong .env' if POPPLER_PATH_ENV_CONFIG else '⚠️ Chưa cấu hình (cần cho Windows)'}")
#         st.info(f"API Key (AI): {' Sẵn sàng' if API_KEY_CONFIG else ' Chưa cấu hình'}")
#     st.markdown("---")
#     st.caption(f"© {datetime.now().year} SmartDoc AI by Minh Thắng")


# # --- HIỂN THỊ UI CỦA MODULE ĐƯỢC CHỌN ---
# # Truyền các config cần thiết vào từng UI module
# if app_mode == "Trí tuệ Tài liệu (PDF)":
#     show_main_smartdoc_ui(api_key=API_KEY_CONFIG, poppler_path_env=POPPLER_PATH_ENV_CONFIG)
# elif app_mode == "Trích xuất Form (Ảnh)":
#     show_form_extractor_ui(api_key=API_KEY_CONFIG)
# elif app_mode == "Phân tích Cảm xúc":
#     show_sentiment_analyzer_ui(api_key=API_KEY_CONFIG)
# elif app_mode == "Trích xuất Bảng (PDF)":
#     show_table_extractor_ui()
# elif app_mode == "Ký PDF":
#     show_pdf_signer_ui()
# elif app_mode == "Quản lý Phiên bản":
#     show_version_manager_ui(api_key_for_analysis=API_KEY_CONFIG) # Nếu cần phân tích AI khi lưu version
# elif app_mode == "Hỏi đáp Đa Tài liệu":
#     show_multi_doc_qna_ui(api_key=API_KEY_CONFIG, poppler_path_env=POPPLER_PATH_ENV_CONFIG)
# elif app_mode == "Dịch Văn bản":  # <<<<----- THÊM KHỐI ELIF NÀY
#     show_translator_ui(api_key=API_KEY_CONFIG)
# elif app_mode == "Ghép PDF":        # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_merge_ui()
# elif app_mode == "Tách PDF":         # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_split_ui()
# elif app_mode == " Công cụ Chuyển đổi Tài liệu (Local)":         # <<<<----- THÊM KHỐI ELIF NÀY
#     show_converter_ui()
# elif app_mode == "Đóng dấu Watermark PDF":  # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_watermark_ui()
# elif app_mode == "So sánh Tài liệu (Ảnh)":
#     show_compare_module_ui() # Module này tự xử lý tesseract
# elif app_mode == "Mở khóa PDF":      # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_unlock_ui()
# elif app_mode == "Bảo vệ PDF":       # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_protect_ui()
# elif app_mode == "Biên tập PDF Cơ bản":  # <<<<----- THÊM KHỐI ELIF NÀY
#     show_pdf_editor_ui()
# elif app_mode == "Redaction AI (Che thông tin)":
#     show_pdf_redaction_ui()
# elif app_mode == "Knowledge Graph (Mới)":
#     show_knowledge_graph_ui(api_key=API_KEY_CONFIG)

# app.py
import streamlit as st
import os
from dotenv import load_dotenv
import nltk
import pytesseract
from datetime import datetime

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="SmartDoc AI - Trợ lý Tài liệu Thông minh",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.example.com/help",
        "Report a bug": "https://www.example.com/bug",
        "About": "# SmartDoc AI\nPhiên bản 1.0\nHệ thống xử lý tài liệu thông minh."
    }
)

# ==========================
# ENV CONFIG
# ==========================

load_dotenv()

TESSERACT_PATH_ENV = os.getenv("TESSERACT_CMD")
POPPLER_PATH_ENV_CONFIG = os.getenv("POPPLER_PATH")

OPENROUTER_API_KEY_ENV = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY_ENV = os.getenv("GROQ_API_KEY")
API_KEY_CONFIG = GROQ_API_KEY_ENV if GROQ_API_KEY_ENV else OPENROUTER_API_KEY_ENV

tesseract_found = False

if TESSERACT_PATH_ENV and os.path.exists(TESSERACT_PATH_ENV):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH_ENV
    tesseract_found = True
elif os.name == "nt":
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]

    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            TESSERACT_PATH_ENV = path
            tesseract_found = True
            break


# ==========================
# NLTK SETUP
# ==========================

def ensure_nltk_resource(resource_path, download_name):
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(download_name, quiet=True)


ensure_nltk_resource("tokenizers/punkt", "punkt")
ensure_nltk_resource("corpora/wordnet", "wordnet")
ensure_nltk_resource("corpora/omw-1.4", "omw-1.4")


# ==========================
# IMPORT UI MODULES
# ==========================

from ui_modules.main_smartdoc_ui import show_main_smartdoc_ui
from ui_modules.form_extractor_ui import show_form_extractor_ui
from ui_modules.sentiment_analyzer_ui import show_sentiment_analyzer_ui
from ui_modules.table_extractor_ui import show_table_extractor_ui
from ui_modules.compare_module_ui import show_compare_module_ui
from ui_modules.pdf_signer_ui import show_pdf_signer_ui
from ui_modules.version_manager_ui import show_version_manager_ui
from ui_modules.multi_doc_qna_ui import show_multi_doc_qna_ui
from ui_modules.translator_ui import show_translator_ui
from ui_modules.pdf_merge_ui import show_pdf_merge_ui
from ui_modules.pdf_split_ui import show_pdf_split_ui
from ui_modules.pdf_watermark_ui import show_pdf_watermark_ui
from ui_modules.pdf_unlock_ui import show_pdf_unlock_ui
from ui_modules.pdf_protect_ui import show_pdf_protect_ui
from ui_modules.pdf_editor_ui import show_pdf_editor_ui
from ui_modules.converter_ui import show_converter_ui
from ui_modules.pdf_redaction_ui import show_pdf_redaction_ui
from ui_modules.knowledge_graph_ui import show_knowledge_graph_ui

from ui_utils.dark_mode import manage_dark_mode
from ui_utils.quotes import get_random_quote


# ==========================
# FEATURE CONFIG
# ==========================

FEATURE_GROUPS = {
    "🏠 Tổng quan": {
        "Trang chủ": {
            "description": "Xem tổng quan hệ thống và trạng thái các thành phần.",
            "requires": []
        }
    },

    "🤖 AI xử lý tài liệu": {
        "Trí tuệ Tài liệu (PDF)": {
            "description": "OCR, phân loại, tóm tắt và phân tích nội dung PDF.",
            "requires": ["api", "ocr", "poppler"]
        },
        "Trích xuất Form (Ảnh)": {
            "description": "Phân loại ảnh tài liệu bằng EfficientNetV2B0, OCR và trích xuất thông tin bằng LLM.",
            "requires": ["api", "ocr"]
        },
        "Hỏi đáp Đa Tài liệu": {
            "description": "Hỏi đáp trên nhiều tài liệu bằng RAG/FAISS.",
            "requires": ["api", "ocr", "poppler"]
        },
        "Knowledge Graph": {
            "description": "Tạo biểu đồ tri thức từ nội dung văn bản/tài liệu.",
            "requires": ["api"]
        },
        "Redaction AI": {
            "description": "Che thông tin nhạy cảm trong tài liệu.",
            "requires": ["api", "ocr"]
        },
    },

    "🧠 Phân tích ngôn ngữ": {
        "Phân tích Cảm xúc": {
            "description": "Phân tích sắc thái tích cực/tiêu cực của văn bản.",
            "requires": ["api"]
        },
        "Dịch Văn bản": {
            "description": "Dịch văn bản sang ngôn ngữ khác.",
            "requires": ["api"]
        },
    },

    "📑 Công cụ PDF": {
        "Ghép PDF": {
            "description": "Gộp nhiều file PDF thành một file.",
            "requires": []
        },
        "Tách PDF": {
            "description": "Tách PDF theo khoảng trang.",
            "requires": []
        },
        "Biên tập PDF Cơ bản": {
            "description": "Xoay, xóa, sắp xếp lại trang PDF.",
            "requires": []
        },
        "Ký PDF": {
            "description": "Thêm chữ ký/ảnh ký vào PDF.",
            "requires": []
        },
        "Đóng dấu Watermark PDF": {
            "description": "Thêm watermark văn bản hoặc ảnh vào PDF.",
            "requires": []
        },
        "Bảo vệ PDF": {
            "description": "Đặt mật khẩu cho PDF.",
            "requires": []
        },
        "Mở khóa PDF": {
            "description": "Mở khóa PDF nếu có mật khẩu hợp lệ.",
            "requires": []
        },
    },

    "📊 Trích xuất dữ liệu": {
        "Trích xuất Bảng (PDF)": {
            "description": "Trích xuất bảng từ PDF sang dữ liệu có cấu trúc.",
            "requires": []
        },
        "Chuyển đổi Tài liệu (Local)": {
            "description": "Chuyển đổi tài liệu bằng công cụ local.",
            "requires": []
        },
    },

    "🗂️ Quản lý & so sánh": {
        "So sánh Tài liệu (Ảnh)": {
            "description": "So sánh hai ảnh tài liệu.",
            "requires": ["ocr"]
        },
        "Quản lý Phiên bản": {
            "description": "Lưu, xem và phân tích các phiên bản tài liệu.",
            "requires": ["api"]
        },
    }
}


# ==========================
# ROUTER
# ==========================

def run_feature(app_mode):
    routes = {
        "Trí tuệ Tài liệu (PDF)": lambda: show_main_smartdoc_ui(
            api_key=API_KEY_CONFIG,
            poppler_path_env=POPPLER_PATH_ENV_CONFIG
        ),
        "Trích xuất Form (Ảnh)": lambda: show_form_extractor_ui(
            api_key=API_KEY_CONFIG
        ),
        "Phân tích Cảm xúc": lambda: show_sentiment_analyzer_ui(
            api_key=API_KEY_CONFIG
        ),
        "Trích xuất Bảng (PDF)": lambda: show_table_extractor_ui(),
        "Biên tập PDF Cơ bản": lambda: show_pdf_editor_ui(),
        "Ký PDF": lambda: show_pdf_signer_ui(),
        "Ghép PDF": lambda: show_pdf_merge_ui(),
        "Tách PDF": lambda: show_pdf_split_ui(),
        "Chuyển đổi Tài liệu (Local)": lambda: show_converter_ui(),
        "Đóng dấu Watermark PDF": lambda: show_pdf_watermark_ui(),
        "Hỏi đáp Đa Tài liệu": lambda: show_multi_doc_qna_ui(
            api_key=API_KEY_CONFIG,
            poppler_path_env=POPPLER_PATH_ENV_CONFIG
        ),
        "Dịch Văn bản": lambda: show_translator_ui(
            api_key=API_KEY_CONFIG
        ),
        "So sánh Tài liệu (Ảnh)": lambda: show_compare_module_ui(),
        "Mở khóa PDF": lambda: show_pdf_unlock_ui(),
        "Bảo vệ PDF": lambda: show_pdf_protect_ui(),
        "Knowledge Graph": lambda: show_knowledge_graph_ui(
            api_key=API_KEY_CONFIG,
            poppler_path_env=POPPLER_PATH_ENV_CONFIG
        ),
        "Redaction AI": lambda: show_pdf_redaction_ui(),
        "Quản lý Phiên bản": lambda: show_version_manager_ui(
            api_key_for_analysis=API_KEY_CONFIG
        ),
    }

    if app_mode == "Trang chủ":
        show_home_dashboard()
        return

    feature = routes.get(app_mode)

    if feature:
        feature()
    else:
        st.error(f"Chức năng chưa được cấu hình route: {app_mode}")


# ==========================
# HOME DASHBOARD
# ==========================

def status_badge(ok, ok_text="Sẵn sàng", fail_text="Chưa cấu hình"):
    return ok_text if ok else fail_text


def show_home_dashboard():
    st.markdown(
        "<h1 style='text-align: center;'>📄 SmartDoc AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align: center; font-size: 18px;'>
        Hệ thống hỗ trợ xử lý tài liệu thông minh: OCR, phân loại tài liệu, trích xuất thông tin,
        hỏi đáp tài liệu, xử lý PDF và quản lý phiên bản.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("OCR Engine", status_badge(tesseract_found, "Ready", "Missing"))

    with col2:
        st.metric("AI API", status_badge(bool(API_KEY_CONFIG), "Ready", "Missing"))

    with col3:
        st.metric("Poppler", status_badge(bool(POPPLER_PATH_ENV_CONFIG), "Configured", "Optional/Missing"))

    st.markdown("### Nhóm chức năng")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info("🤖 **AI xử lý tài liệu**\n\nPhân loại, OCR, trích xuất form, hỏi đáp và Knowledge Graph.")

    with c2:
        st.success("📑 **Công cụ PDF**\n\nGhép, tách, ký, watermark, bảo vệ và biên tập PDF.")

    with c3:
        st.warning("📊 **Trích xuất dữ liệu**\n\nTrích xuất bảng PDF, chuyển đổi tài liệu và phân tích văn bản.")

    st.markdown("### Quy trình demo đề xuất")

    st.write(
        """
        1. Vào **Trích xuất Form (Ảnh)** để demo model EfficientNetV2B0 phân loại ảnh tài liệu.
        2. Vào **Trí tuệ Tài liệu (PDF)** để demo OCR + PhoBERT + LLM phân tích tài liệu PDF.
        3. Vào **Hỏi đáp Đa Tài liệu** để demo RAG/FAISS.
        4. Vào nhóm **Công cụ PDF** để demo các chức năng xử lý file thực tế.
        """
    )


# ==========================
# SIDEBAR
# ==========================

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    else:
        st.markdown(
            "<h1 style='text-align: center; font-size: 34px;'>📄</h1>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<h1 style='text-align: center; font-weight: 800;'>SmartDoc AI</h1>",
        unsafe_allow_html=True
    )

    st.caption(f"<p style='text-align: center;'>{get_random_quote()}</p>", unsafe_allow_html=True)

    st.markdown("---")

    manage_dark_mode()

    st.markdown("---")

    st.subheader("Điều hướng")

    selected_group = st.selectbox(
        "Nhóm chức năng",
        list(FEATURE_GROUPS.keys()),
        key="selected_feature_group"
    )

    feature_names = list(FEATURE_GROUPS[selected_group].keys())

    selected_feature = st.radio(
        "Chức năng",
        feature_names,
        label_visibility="collapsed",
        key="selected_feature"
    )

    selected_meta = FEATURE_GROUPS[selected_group][selected_feature]

    st.caption(selected_meta["description"])

    st.markdown("---")

    with st.expander("Trạng thái hệ thống", expanded=False):
        st.write(f"OCR/Tesseract: {'✅ Sẵn sàng' if tesseract_found else '⚠️ Chưa tìm thấy'}")
        st.write(f"Poppler: {'✅ Đã cấu hình' if POPPLER_PATH_ENV_CONFIG else '⚠️ Chưa cấu hình'}")
        st.write(f"AI API Key: {'✅ Sẵn sàng' if API_KEY_CONFIG else '⚠️ Chưa cấu hình'}")

        if TESSERACT_PATH_ENV:
            st.caption(f"Tesseract path: {TESSERACT_PATH_ENV}")

        if POPPLER_PATH_ENV_CONFIG:
            st.caption(f"Poppler path: {POPPLER_PATH_ENV_CONFIG}")

    st.markdown("---")

    st.caption(f"© {datetime.now().year} SmartDoc AI")


# ==========================
# MAIN CONTENT
# ==========================

run_feature(selected_feature)