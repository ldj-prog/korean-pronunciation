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
st.set_page_config(page_title="Korean Pronunciation Converter", layout="centered")

custom_css = """
<style>
    .stApp { background-color: #FFFFFF; color: #000000; font-family: sans-serif; }
    .stTextArea textarea { font-size: 16px; border: 1px solid #333; border-radius: 4px; }
    .stButton { display: flex; justify-content: center; }
    .stButton > button { 
        width: 50% !important; min-width: 200px; 
        background-color: #000000; color: #FFFFFF; border: none; height: 45px; font-weight: bold; margin-top: 10px; 
    }
    .stButton>button:hover { background-color: #333333; color: #FFFFFF; }
    .result-card { border: 1px solid #000000; padding: 20px; margin-top: 20px; background-color: white; }
    .label-text { font-size: 12px; color: #666; font-weight: bold; margin-bottom: 8px; }
    .pronunciation-text { color: #1E88E5; font-size: 18px; font-weight: 500; word-wrap: break-word; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 初始化引擎 (带详细报错)
# ==========================================
@st.cache_resource
def load_g2p():
    return G2p()

try:
    g2p = load_g2p()
except Exception as e:
    # 【关键修改】这里会打印出具体的错误代码！
    st.error(f"System Error Details: {e}")
    st.warning("Tip: This usually means 'packages.txt' is missing or 'mecab' is not installed.")
    st.stop()

# ==========================================
# 3. 界面逻辑
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 24px; margin-bottom: 30px;'>한국어 발음 변환기</h1>", unsafe_allow_html=True)

user_input = st.text_area("Input", height=150, label_visibility="collapsed", placeholder="Paste Korean text here...")
st.write("") 

if st.button("ANALYZE"):
    if user_input.strip():
        clean_text = user_input.replace('\n', ' ').replace('\r', ' ')
        try:
            pronunciation = g2p(clean_text)
            st.markdown(f"""
            <div class="result-card">
                <div class="label-text">PRONUNCIATION</div>
                <div class="pronunciation-text">[{pronunciation}]</div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Analysis Failed: {e}")
    else:
        st.warning("Please enter text.")
