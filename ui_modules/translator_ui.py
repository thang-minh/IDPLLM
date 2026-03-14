# ui_modules/translator_ui.py
import streamlit as st
import asyncio
from logic.translator_logic import translate_text_with_llm # Import hàm logic
from ui_utils.fun_meme import display_random_meme

# Danh sách ngôn ngữ phổ biến (mã ISO 639-1 và tên tiếng Việt)
# Bạn có thể mở rộng danh sách này
SUPPORTED_LANGUAGES = {
    "auto": "Tự động phát hiện",
    "vi": "Tiếng Việt (Vietnamese)",
    "en": "Tiếng Anh (English)",
    "fr": "Tiếng Pháp (French)",
    "es": "Tiếng Tây Ban Nha (Spanish)",
    "de": "Tiếng Đức (German)",
    "ja": "Tiếng Nhật (Japanese)",
    "ko": "Tiếng Hàn (Korean)",
    "zh-CN": "Tiếng Trung - Giản thể (Chinese Simplified)",
    "ru": "Tiếng Nga (Russian)",
    "ar": "Tiếng Ả Rập (Arabic)",
    "hi": "Tiếng Hindi (Hindi)"
}
# Lấy danh sách tên ngôn ngữ để hiển thị trong selectbox
LANGUAGE_DISPLAY_NAMES = list(SUPPORTED_LANGUAGES.values())
# Tạo dict ngược để lấy mã ngôn ngữ từ tên hiển thị
LANGUAGE_CODES = {v: k for k, v in SUPPORTED_LANGUAGES.items()}


def show_translator_ui(api_key: str):
    st.markdown("<h1 style='text-align: center;'>🌐 Dịch Văn bản Đa Ngôn ngữ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Nhập văn bản cần dịch, chọn ngôn ngữ nguồn và ngôn ngữ đích, sau đó để AI thực hiện phần còn lại!</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Khởi tạo session state
    if 'trans_input_text' not in st.session_state:
        st.session_state.trans_input_text = ""
    if 'trans_source_lang_display' not in st.session_state:
        st.session_state.trans_source_lang_display = SUPPORTED_LANGUAGES["auto"] # Mặc định
    if 'trans_target_lang_display' not in st.session_state:
        st.session_state.trans_target_lang_display = SUPPORTED_LANGUAGES["en"] # Mặc định dịch sang tiếng Anh
    if 'trans_translated_text' not in st.session_state:
        st.session_state.trans_translated_text = ""

    col_input, col_output = st.columns(2)

    with col_input:
        with st.container(border=True):
            st.subheader("📜 Văn bản Gốc")
            st.session_state.trans_input_text = st.text_area(
                "Nhập hoặc dán văn bản cần dịch vào đây:",
                value=st.session_state.trans_input_text,
                height=250,
                key="translator_input_text_area",
                placeholder="Xin chào thế giới!"
            )
            # Hiển thị số ký tự để người dùng ước lượng
            st.caption(f"Số ký tự: {len(st.session_state.trans_input_text)}")


    with col_output:
        with st.container(border=True):
            st.subheader("📝 Văn bản Đã Dịch")
            # Để st.text_area ở chế độ disabled để người dùng không sửa được, nhưng vẫn copy được
            st.text_area(
                "Kết quả dịch sẽ hiển thị ở đây:",
                value=st.session_state.trans_translated_text,
                height=250,
                key="translator_output_text_area",
                disabled=True # Không cho sửa, chỉ hiển thị
            )
            if st.session_state.trans_translated_text:
                st.download_button(
                    label="📥 Tải bản dịch (.txt)",
                    data=st.session_state.trans_translated_text.encode("utf-8"),
                    file_name="translated_text.txt",
                    mime="text/plain",
                    key="translator_download_button"
                )

    st.markdown("---")
    
    # Lựa chọn ngôn ngữ và nút dịch
    col_lang1, col_lang2, col_button = st.columns([2,2,1])
    with col_lang1:
        st.session_state.trans_source_lang_display = st.selectbox(
            "Từ ngôn ngữ:",
            options=LANGUAGE_DISPLAY_NAMES,
            index=LANGUAGE_DISPLAY_NAMES.index(st.session_state.trans_source_lang_display), # Giữ lựa chọn cũ
            key="translator_source_lang_select"
        )
    with col_lang2:
        st.session_state.trans_target_lang_display = st.selectbox(
            "Sang ngôn ngữ:",
            options=[lang for lang in LANGUAGE_DISPLAY_NAMES if lang != SUPPORTED_LANGUAGES["auto"]], # Không cho chọn "auto" làm target
            index=[lang for lang in LANGUAGE_DISPLAY_NAMES if lang != SUPPORTED_LANGUAGES["auto"]].index(st.session_state.trans_target_lang_display) if st.session_state.trans_target_lang_display != SUPPORTED_LANGUAGES["auto"] else 0,
            key="translator_target_lang_select"
        )
    
    # Nút để đảo ngược ngôn ngữ nguồn và đích
    def swap_languages():
        source_display = st.session_state.trans_source_lang_display
        target_display = st.session_state.trans_target_lang_display
        # Không cho swap nếu một trong hai là "Tự động phát hiện" và cái kia sẽ thành "Tự động phát hiện"
        if source_display != SUPPORTED_LANGUAGES["auto"] and target_display != SUPPORTED_LANGUAGES["auto"]:
            st.session_state.trans_source_lang_display = target_display
            st.session_state.trans_target_lang_display = source_display
        elif source_display == SUPPORTED_LANGUAGES["auto"] and target_display != SUPPORTED_LANGUAGES["auto"]:
             # Nếu nguồn là auto, và đích không phải auto -> không làm gì hoặc đặt nguồn là đích, đích là một ngôn ngữ mặc định khác
             # Để đơn giản, tạm thời không cho swap nếu nguồn là auto
             st.toast("Không thể đảo ngôn ngữ khi ngôn ngữ nguồn là 'Tự động phát hiện'.")

        # Đảo cả nội dung text nếu có
        temp_text = st.session_state.trans_input_text
        st.session_state.trans_input_text = st.session_state.trans_translated_text
        st.session_state.trans_translated_text = temp_text


    with col_button:
        st.button("🔄 Đảo Ngôn ngữ", on_click=swap_languages, key="translator_swap_lang_button", use_container_width=True, help="Đảo ngược ngôn ngữ nguồn và đích, đồng thời đảo nội dung văn bản.")


    if st.button("🌍 Dịch Văn bản Ngay", type="primary", use_container_width=True, key="translator_translate_button", disabled=not st.session_state.trans_input_text.strip()):
        if not api_key:
            st.error("API Key chưa được cấu hình. Không thể thực hiện dịch thuật.")
            return
        if not st.session_state.trans_input_text.strip():
            st.warning("Vui lòng nhập văn bản cần dịch.")
            return
        if st.session_state.trans_source_lang_display == st.session_state.trans_target_lang_display and st.session_state.trans_source_lang_display != SUPPORTED_LANGUAGES["auto"]:
            st.warning("Ngôn ngữ nguồn và ngôn ngữ đích giống nhau. Vui lòng chọn khác nhau.")
            return

        source_lang_code = LANGUAGE_CODES[st.session_state.trans_source_lang_display]
        target_lang_code = LANGUAGE_CODES[st.session_state.trans_target_lang_display]
        
        # Lấy tên ngôn ngữ đầy đủ hơn để truyền cho LLM (ví dụ: "Vietnamese" thay vì "vi")
        source_lang_for_llm = source_lang_code if source_lang_code != "auto" else "auto"
        target_lang_for_llm = st.session_state.trans_target_lang_display.split('(')[0].strip() # Lấy phần tên Tiếng Việt/Anh


        with st.spinner(f"Đang dịch từ {st.session_state.trans_source_lang_display} sang {st.session_state.trans_target_lang_display}..."):
            try:
                translated_text = asyncio.run(translate_text_with_llm(
                    api_key,
                    st.session_state.trans_input_text,
                    source_language=source_lang_for_llm, # Truyền tên ngôn ngữ đầy đủ
                    target_language=target_lang_for_llm
                ))
                st.session_state.trans_translated_text = translated_text
                # Không cần st.success ở đây vì kết quả đã hiển thị trong text_area
            except ValueError as ve:
                st.error(f"Lỗi dịch: {ve}")
                st.session_state.trans_translated_text = ""
            except Exception as e_trans:
                st.error(f"Lỗi không mong muốn khi dịch: {e_trans}")
                st.session_state.trans_translated_text = ""
            # Trigger rerun để cập nhật text_area output (dù st.text_area với session_state thường tự cập nhật)
            st.rerun()

    if st.session_state.trans_input_text or st.session_state.trans_translated_text:
        st.markdown("---")
        display_random_meme()