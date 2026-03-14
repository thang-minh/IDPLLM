# ui_utils/fun_meme.py
import os
import random
from PIL import Image
import streamlit as st # Import Streamlit for st.image

MEME_FOLDER = "memes" # Đảm bảo thư mục này tồn tại ở root dự án

def get_random_meme_path():
    if not os.path.exists(MEME_FOLDER) or not os.path.isdir(MEME_FOLDER):
        return None
    try:
        meme_files = [f for f in os.listdir(MEME_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not meme_files:
            return None
        return os.path.join(MEME_FOLDER, random.choice(meme_files))
    except FileNotFoundError:
        return None


def get_meme_message():
    messages = [
        "Xong rồi nhaaa! Giờ nghỉ giải lao tí đi! 😎",
        "Tài liệu đã được xử lý xong, chill tí nào! 🍹",
        "Hoàn thành xuất sắc! Bạn xứng đáng một cái bánh 🥳",
        "Done! Tạm nghỉ ngơi, rồi quay lại thôi! 🚀",
        "Bản báo cáo đã sẵn sàng, giờ bật nhạc lên và thư giãn thôi! 🎧"
    ]
    return random.choice(messages)

def display_random_meme(width=350):
    st.success(get_meme_message())
    meme_path = get_random_meme_path()
    if meme_path:
        try:
            meme_img = Image.open(meme_path)
            st.image(meme_img, caption="Một chút thư giãn!", width=width)
        except Exception as e:
            st.warning(f"Không thể tải meme: {e}")
    else:
        st.info("Không tìm thấy meme nào trong thư mục 'memes'.")