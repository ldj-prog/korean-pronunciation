import streamlit as st
from g2pk import G2p

# ==========================================
# 1. 页面配置 & CSS (黑白极简 + 蓝色高亮 + 按钮居中优化)
# ==========================================
st.set_page_config(page_title="Korean Pronunciation Converter", layout="centered")

custom_css = """
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    /* 输入框样式 */
    .stTextArea textarea {
        font-size: 16px;
        border: 1px solid #333;
        border-radius: 4px;
    }
    /* 按钮样式 */
    .stButton>button {
        width: 100%;
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        height: 45px; /* 稍微调矮一点，更精致 */
        font-weight: bold;
        font-size: 16px;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: #FFFFFF;
    }
    /* 结果卡片 */
    .result-card {
        border: 1px solid #000000;
        padding: 20px;
        margin-top: 20px;
        background-color: white;
    }
    .label-text {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-weight: bold;
    }
    .pronunciation-text {
        color: #1E88E5; /* 核心蓝色 */
        font-size: 18px;
        font-weight: 500;
        word-wrap: break-word;
        word-break: break-all;
        line-height: 1.6;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 初始化引擎
# ==========================================
@st.cache_resource
def load_g2p():
    return G2p()

try:
    g2p = load_g2p()
except Exception:
    st.error("Error: G2P library not found.")
    st.stop()

# ==========================================
# 3. 界面逻辑
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 24px; margin-bottom: 30px;'>한국어 발음 변환기</h1>", unsafe_allow_html=True)

# 输入框
user_input = st.text_area("Input", height=150, label_visibility="collapsed", placeholder="Paste Korean text here...")

# --- 按钮居中布局 ---
st.write("") # 加一点空行
col1, col2, col3 = st.columns([1, 2, 1]) # 左1份，中2份，右1份

with col2: # 按钮放在中间的格子里
    analyze_click = st.button("ANALYZE")

# --- 点击后的逻辑 ---
if analyze_click:
    if user_input.strip():
        # 预处理
        clean_text = user_input.replace('\n', ' ').replace('\r', ' ')
        
        # 转换
        pronunciation = g2p(clean_text)

        # 显示结果
        st.markdown(f"""
        <div class="result-card">
            <div class="label-text">PRONUNCIATION</div>
            <div class="pronunciation-text">[{pronunciation}]</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Please enter text.")
