# ui_utils/dark_mode.py
import streamlit as st

DARK_MODE_CSS = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-color: #1E1E1E; /* Màu nền chính tối hơn */
    color: #E0E0E0;
}
[data-testid="stSidebar"] {
    background-color: #252526; /* Màu nền sidebar */
    color: #E0E0E0;
}
h1, h2, h3, h4, h5, h6 {
    color: #00A9FF; /* Màu tiêu đề chính */
}
.stButton>button {
    background-color: #007ACC; /* Màu nút */
    color: white;
    border-radius: 5px;
    border: none;
}
.stButton>button:hover {
    background-color: #005C99;
    color: white;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #2D2D30;
    color: #E0E0E0;
    border: 1px solid #3E3E40;
    border-radius: 5px;
}
div[data-baseweb="select"] > div { /* Specific for selectbox */
    background-color: #2D2D30 !important;
    border: 1px solid #3E3E40 !important;
}
div[data-baseweb="select"] ul { /* Dropdown list */
    background-color: #2D2D30;
    border: 1px solid #3E3E40;
}
div[data-baseweb="select"] ul li:hover {
    background-color: #3E3E40;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #2D2D30;
}
::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
    background: #777;
}
/* Expander styling */
.streamlit-expanderHeader {
    background-color: #2D2D30;
    color: #00A9FF; /* Header color for expander */
    border-radius: 5px;
}
/* Tab styling */
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #2D2D30;
    color: #00A9FF; /* Active tab color */
    border-bottom: 2px solid #00A9FF !important;
}
div[data-baseweb="tab-list"] button {
    color: #E0E0E0; /* Inactive tab color */
}
</style>
"""

LIGHT_MODE_CSS = """
<style>
/* Optionally define light mode specific styles if needed, or remove to use Streamlit default */
[data-testid="stAppViewContainer"] > .main {
    background-color: #FFFFFF;
    color: #333333;
}
[data-testid="stSidebar"] {
    background-color: #F5F5F5;
}
h1, h2, h3, h4, h5, h6 {
    color: #007ACC;
}
/* Add other light mode specific styles here if you want to override defaults */
</style>
"""

def manage_dark_mode():
    if 'dark_mode_on' not in st.session_state:
        st.session_state.dark_mode_on = False
         

    is_dark = st.checkbox("🌙 Chế độ Tối", value=st.session_state.dark_mode_on, key="dark_mode_toggle",
                          on_change=toggle_dark_mode)

    if is_dark:
        st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)
    else:
        # Để quay về light mode, có thể cần clear CSS của dark mode hoặc inject CSS của light mode
        # Cách đơn giản là không inject gì cả để Streamlit dùng theme mặc định của nó
        # Hoặc inject CSS light mode nếu bạn đã tùy chỉnh nhiều
        st.markdown(f"<style>body {{ background-color: white; color: black; }}</style>", unsafe_allow_html=True) # Dòng này chỉ là ví dụ đơn giản
        pass # Hoặc st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)

def toggle_dark_mode():
    st.session_state.dark_mode_on = not st.session_state.dark_mode_on