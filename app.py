import streamlit as st
import os
import google.generativeai as genai
from g2pk import G2p

# ==========================================
# 1. 配置页面 & CSS 样式 (黑白极简 + 移动端修复 + 蓝色发音)
# ==========================================
st.set_page_config(page_title="Korean Pronunciation Converter", layout="centered")

# 定义自定义 CSS
custom_css = """
<style>
    /* 全局背景设为白色，字体黑色 */
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

    /* 按钮样式 (黑底白字) */
    .stButton>button {
        width: 100%;
        background-color: #000000;
        color: #FFFFFF;
        border: none;
        border-radius: 0;
        height: 50px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: #FFFFFF;
    }

    /* 结果卡片容器 (细边框，统一内边距) */
    .result-card {
        border: 1px solid #000000; /* 统一细边框 */
        padding: 20px;
        margin-top: 20px;
        border-radius: 0;
        background-color: white;
    }

    /* 蓝色发音文本 (极速显示) */
    .pronunciation-text {
        color: #1E88E5; /* 蓝色 */
        font-size: 18px;
        margin-bottom: 15px;
        font-weight: 500;
        word-wrap: break-word; /* 移动端强制换行 */
        word-break: break-all;
        white-space: pre-wrap;
        line-height: 1.6;
    }

    /* 黑色翻译文本 */
    .translation-text {
        color: #000000; /* 黑色 */
        font-size: 16px;
        margin-bottom: 8px;
        word-wrap: break-word; /* 移动端强制换行 */
        word-break: break-all;
        white-space: pre-wrap;
        line-height: 1.5;
    }

    /* 小标签样式 */
    .label-text {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
        font-weight: bold;
    }
    
    /* 分割线 */
    .divider {
        border-top: 1px solid #eee;
        margin: 15px 0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 2. 高性能初始化 (Cache 缓存)
# ==========================================

# 缓存 G2P 引擎，避免每次点击都重新加载 (速度提升 10 倍)
@st.cache_resource
def load_g2p():
    return G2p()

# 尝试获取 API Key (优先从 Streamlit Secrets 获取，其次从环境变量，最后手动填)
try:
    # 如果你在 Streamlit Cloud 部署，Key 会从这里读取
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # 如果你在本地运行，可以直接把 Key 填在这里 (不推荐上传 GitHub)
    # api_key = "你的_API_KEY_粘贴在这里" 
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # 使用 Flash 模型以获得最快速度
    model = genai.GenerativeModel('gemini-1.5-flash')

# 加载发音库
try:
    g2p = load_g2p()
except Exception as e:
    st.error("Error loading g2pk library. Please ensure it is installed.")
    st.stop()

# ==========================================
# 3. 核心逻辑与界面
# ==========================================

st.markdown("<h1 style='text-align: center; font-size: 24px;'>한국어 발음 변환기</h1>", unsafe_allow_html=True)

# 输入框
user_input = st.text_area("Input Korean text here:", height=150, label_visibility="collapsed")

if st.button("ANALYZE"):
    if not user_input.strip():
        st.warning("Please enter some text.")
    else:
        # --- STEP 1: 极速本地处理 (发音) ---
        
        # 预处理：移除换行符，防止单词被切断导致发音错误
        # 将换行符替换为空格，保持句子连贯性
        clean_text = user_input.replace('\n', ' ').replace('\r', ' ')
        
        # 调用 g2pk (整句处理，保证连音/同化准确)
        try:
            pronunciation = g2p(clean_text)
        except Exception as e:
            pronunciation = f"Error processing pronunciation: {e}"

        # 立即显示发音结果 (Placeholder 用于稍后填充翻译)
        result_container = st.container()
        
        with result_container:
            st.markdown(f"""
            <div class="result-card">
                <div class="label-text">PRONUNCIATION</div>
                <div class="pronunciation-text">[{pronunciation}]</div>
                <div id="translation-placeholder"></div>
            </div>
            """, unsafe_allow_html=True)

        # --- STEP 2: 异步加载翻译 (API 调用) ---
        
        if api_key:
            with st.spinner("Translating..."):
                try:
                    # 构造 Prompt
                    prompt = f"""
                    Translate the following Korean text into Chinese (Simplified) and English.
                    Return ONLY the raw translations separated by a pipe symbol (|).
                    Format: Chinese Translation | English Translation
                    
                    Text: {user_input}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        parts = response.text.split('|')
                        if len(parts) >= 2:
                            cn_trans = parts[0].strip()
                            en_trans = parts[1].strip()
                        else:
                            cn_trans = response.text
                            en_trans = ""
                            
                        # 重新渲染整个卡片，带上翻译
                        # 注意：这里我们重新生成 HTML 来包含翻译部分
                        result_container.empty() # 清空之前的纯发音显示
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="label-text">PRONUNCIATION</div>
                            <div class="pronunciation-text">[{pronunciation}]</div>
                            
                            <div class="divider"></div>
                            
                            <div class="label-text">MEANING (CN)</div>
                            <div class="translation-text">{cn_trans}</div>
                            
                            <div class="label-text">MEANING (EN)</div>
                            <div class="translation-text">{en_trans}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Translation Error: {e}")
        else:
            st.warning("Please configure your Google API Key to see translations.")