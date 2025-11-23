import re
import streamlit as st

# 尝试导入，如果连包都找不到，这里就会报错
try:
    from g2pk import G2p
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    st.stop()

# ==========================================
# 1. 页面配置 & CSS
# ==========================================
st.set_page_config(
    page_title="Korean Pronunciation Converter",
    layout="centered"
)

custom_css = """
<style>
    .stApp { 
        background-color: #FFFFFF; 
        color: #000000; 
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    }

    /* textarea 样式 */
    .stTextArea textarea { 
        font-size: 16px; 
        border: 1px solid #333; 
        border-radius: 4px; 
    }

    /* 按钮统一样式，高度&字体 */
    .stButton > button { 
        background-color: #000000; 
        color: #FFFFFF; 
        border: none; 
        height: 45px; 
        font-weight: bold; 
        margin-top: 10px; 
    }
    .stButton > button:hover { 
        background-color: #333333; 
        color: #FFFFFF; 
    }

    /* 结果卡片 */
    .result-card { 
        border: 1px solid #000000; 
        padding: 20px; 
        margin-top: 20px; 
        background-color: #FFFFFF; 
    }
    .label-text { 
        font-size: 12px; 
        color: #666; 
        font-weight: bold; 
        margin-bottom: 8px; 
    }
    .pronunciation-text { 
        color: #1E88E5; 
        font-size: 18px; 
        font-weight: 500; 
        word-wrap: break-word; 
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 初始化引擎 (带缓存)
# ==========================================
@st.cache_resource
def load_g2p():
    return G2p()

try:
    g2p = load_g2p()
except Exception as e:
    st.error(f"System Error Details: {e}")
    st.warning("Tip: This usually means 'packages.txt' is missing or 'mecab' is not installed.")
    st.stop()

# ==========================================
# 3. 一点点后处理，让音变结果更干净
# ==========================================
def postprocess_pron(text: str) -> str:
    # 把连续空格压成一个
    text = re.sub(r'\s+', ' ', text)
    # 去掉中文/韩文标点前面的空格
    text = re.sub(r'\s+([.,!?…·，．？！、:;:\]])', r'\1', text)
    # 去掉首尾空格
    text = text.strip()
    return text

# ==========================================
# 4. 界面逻辑
# ==========================================
st.markdown(
    "<h1 style='text-align: center; font-size: 24px; margin-bottom: 30px;'>한국어 발음 변환기</h1>",
    unsafe_allow_html=True
)

user_input = st.text_area(
    "Input",
    height=150,
    label_visibility="collapsed",
    placeholder="Paste Korean text here..."
)
st.write("")

# --------- 中间居中的按钮 ----------
left_col, mid_col, right_col = st.columns([1, 2, 1])
with mid_col:
    analyze_clicked = st.button("ANALYZE", use_container_width=True)

# --------- 点击按钮后处理 ----------
if analyze_clicked:
    if user_input.strip():
        # 保留原来的句子，只把换行变空格
        clean_text = user_input.replace('\n', ' ').replace('\r', ' ')
        try:
            raw_pron = g2p(clean_text)
            pronunciation = postprocess_pron(raw_pron)

            st.markdown(
                f"""
                <div class="result-card">
                    <div class="label-text">PRONUNCIATION</div>
                    <div class="pronunciation-text">[{pronunciation}]</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Analysis Failed: {e}")
    else:
        st.warning("Please enter text.")
