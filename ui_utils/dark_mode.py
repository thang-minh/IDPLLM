# ui_utils/dark_mode.py
import streamlit as st

SAAS_LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* =========================================================
   1. RESET & CORE COLOR DESIGN SYSTEM (STRIPE & LINEAR)
   ========================================================= */
:root {
    color-scheme: light !important;
}

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: #F8FAFC !important;
    color: #334155 !important;
    letter-spacing: -0.011em !important;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Headings chuẩn SaaS */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* Nền tổng thể: Slate 50 (#F8FAFC) */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {
    background-color: #F8FAFC !important;
    color: #334155 !important;
}

/* =========================================================
   2. HEADER & TOOLBAR & NÚT MỞ SIDEBAR
   ========================================================= */
header[data-testid="stHeader"], header {
    background-color: transparent !important;
    display: flex !important;
    visibility: visible !important;
    z-index: 1000 !important;
}

header > div:first-child {
    background-color: transparent !important;
}

[data-testid="stToolbar"] {
    background-color: transparent !important;
    visibility: visible !important;
    display: flex !important;
}

/* Ẩn các nút deploy và menu thừa của Streamlit */
#MainMenu, footer, .stDeployButton, [data-testid="stAppDeployButton"], [data-testid="stStatusWidget"] {
    visibility: hidden !important;
    display: none !important;
}

/* Nút mở lại Sidebar (Expand Sidebar) */
[data-testid="stExpandSidebarButton"],
button[aria-label="Expand sidebar"],
button[title="Expand sidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    color: #4F46E5 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}

[data-testid="stExpandSidebarButton"]:hover,
button[aria-label="Expand sidebar"]:hover,
button[title="Expand sidebar"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover {
    background-color: #EEF2FF !important;
    border-color: #4F46E5 !important;
    color: #4338CA !important;
    transform: translateX(2px) !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.18) !important;
}

[data-testid="stExpandSidebarButton"] svg,
button[aria-label="Expand sidebar"] svg,
button[title="Expand sidebar"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg {
    fill: #4F46E5 !important;
    stroke: #4F46E5 !important;
    color: #4F46E5 !important;
    width: 20px !important;
    height: 20px !important;
}

/* Nút đóng Sidebar */
[data-testid="stSidebarCollapseButton"],
button[aria-label="Collapse sidebar"] {
    border-radius: 6px !important;
    border: 1px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebarCollapseButton"]:hover,
button[aria-label="Collapse sidebar"]:hover {
    background-color: #F1F5F9 !important;
    border-color: #CBD5E1 !important;
}

/* =========================================================
   3. SIDEBAR (260px, WHITE, STRIPE DASHBOARD STYLE)
   ========================================================= */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: none !important;
    min-width: 260px !important;
    max-width: 275px !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.25rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

[data-testid="stSidebar"] label {
    color: #475569 !important;
    font-weight: 600 !important;
}

/* Selectbox trong Sidebar */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
}

div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    min-height: 40px !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #94A3B8 !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
}

div[data-baseweb="select"] * {
    color: #0F172A !important;
    background-color: transparent !important;
}

/* Dropdown Menu */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08) !important;
}

li[data-baseweb="menu-item"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
}

li[data-baseweb="menu-item"]:hover,
li[data-baseweb="menu-item"][aria-selected="true"] {
    background-color: #EEF2FF !important;
    color: #4F46E5 !important;
}

/* Navigation items in sidebar (Radio buttons) */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
    padding: 8px 12px !important;
    border-radius: 8px !important;
    margin-bottom: 2px !important;
    cursor: pointer !important;
    transition: all 0.12s ease !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    background-color: #F8FAFC !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background-color: #EEF2FF !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #4F46E5 !important;
    font-weight: 600 !important;
}

/* =========================================================
   4. FILE UPLOADER (SUBTLE DASHED INDIGO BORDER)
   ========================================================= */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 1.5px dashed #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.02) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #4F46E5 !important;
    background-color: #FAFAFD !important;
}

[data-testid="stFileUploader"] section {
    background-color: transparent !important;
}

[data-testid="stFileUploader"] section button {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}

[data-testid="stFileUploader"] section button:hover {
    background-color: #F8FAFC !important;
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span {
    color: #64748B !important;
}

/* =========================================================
   5. NÚT BẤM (BUTTONS - STRIPE SAAS STYLE)
   ========================================================= */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 0.5rem 1.2rem !important;
    border: 1px solid #CBD5E1 !important;
    background-color: #FFFFFF !important;
    color: #334155 !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
}

.stButton > button:hover {
    border-color: #94A3B8 !important;
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    transform: translateY(-1px) !important;
}

/* Primary Button (Indigo #4F46E5, Hover #4338CA) */
.stButton > button[kind="primary"] {
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
    border: 1px solid #4338CA !important;
    box-shadow: 0 1px 3px 0 rgba(79, 70, 229, 0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #4338CA !important;
    border-color: #3730A3 !important;
    box-shadow: 0 4px 10px 0 rgba(79, 70, 229, 0.35) !important;
}

.stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
}

/* =========================================================
   6. METRIC CARDS & CONTAINERS
   ========================================================= */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03) !important;
}

[data-testid="stMetricLabel"] p {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    font-weight: 700 !important;
    color: #64748B !important;
}

[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    color: #0F172A !important;
    margin-top: 4px !important;
}

[data-testid="stVerticalBlock"] > div[style*="border:"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03) !important;
}

/* =========================================================
   7. INPUTS & TEXTAREA
   ========================================================= */
.stTextInput input, .stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #4F46E5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
}

/* =========================================================
   8. ALERTS & NOTIFICATIONS
   ========================================================= */
.stAlert > div {
    background-color: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    color: #1E40AF !important;
    border-radius: 10px !important;
}

.stAlert > div * {
    color: #1E40AF !important;
}

/* =========================================================
   9. SOFT BADGES DESIGN SYSTEM
   ========================================================= */
.badge-soft-success {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #F0FDFA;
    color: #0D9488;
    border: 1px solid #99F6E4;
}

.badge-soft-warning {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #FFFBEB;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.badge-soft-danger {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #FEF2F2;
    color: #EF4444;
    border: 1px solid #FECACA;
}

.badge-soft-info {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #EFF6FF;
    color: #2563EB;
    border: 1px solid #BFDBFE;
}

.badge-soft-indigo {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #EEF2FF;
    color: #4F46E5;
    border: 1px solid #C7D2FE;
}

.badge-soft-neutral {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* Stepper Component */
.pipeline-step-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 18px;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}

.pipeline-step {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13.5px;
    font-weight: 600;
    color: #94A3B8;
}

.pipeline-step.active {
    color: #4F46E5;
}

.pipeline-step.completed {
    color: #0D9488;
}

.pipeline-separator {
    color: #CBD5E1;
    font-size: 13px;
    font-weight: 600;
}
</style>
"""

def manage_dark_mode():
    st.markdown(SAAS_LIGHT_CSS, unsafe_allow_html=True)
