import re
import streamlit as st

# ==========================================
# 0. 尝试导入 g2pk
# ==========================================
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

    /* 按钮统一样式 */
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
# 2. 初始化 g2pk 引擎
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
# 3. URL 参数：支持 ?q=검색어 （给欧路词典等用）
# ==========================================
query_params = st.query_params
auto_word = query_params.get("q", "")
auto_word = auto_word.strip()
auto_run = bool(auto_word)

# ==========================================
# 4. 一般清理：空格 / 标点
# ==========================================
def normalize_spaces(text: str) -> str:
    # 连续空格压成一个
    text = re.sub(r"\s+", " ", text)
    # 去掉标点前面的空格
    text = re.sub(r"\s+([.,!?…·，．？！、:;:\]])", r"\1", text)
    # 去掉首尾空格
    return text.strip()

# ==========================================
# 5. 釜大风格音变补丁层
# ==========================================
def apply_pnu_rules(text: str) -> str:
    """
    在 g2pk 的基础发音结果上，加一层“釜大风格”修正。
    可以根据需要继续往里加规则。
    """

    # ---- 5.1 助词/语尾：에는 → 에느 ----
    particle_patches = [
        ("에는요", "에느요"),
        ("에는도", "에느도"),
        ("에는만", "에느만"),
        ("에는까지", "에느까지"),
        ("에는", "에느"),
    ]
    for before, after in particle_patches:
        text = text.replace(before, after)

    # ---- 5.2 常见连音 / 비음화 / 경음화 修正 ----
    pnu_patches = [
        ("일정", "닐정"),   # 일정 → 닐정
        ("일주", "닐주"),   # 일주 → 닐주
        ("물질", "물찔"),   # 물질 → 물찔
        # 需要时可以继续添加：
        # ("할지", "할지") 等等
    ]
    for before, after in pnu_patches:
        text = text.replace(before, after)

    return text

# ==========================================
# 6. “完整的釜大风格发音模块”
# ==========================================
def pnu_g2p(text: str) -> str:
    """
    1) 用 g2pk 做基础音变；
    2) 清理空格/标点；
    3) 用釜大规则修正；
    """
    base = g2p(text)
    base = normalize_spaces(base)
    refined = apply_pnu_rules(base)
    refined = normalize_spaces(refined)
    return refined

# ==========================================
# 7. 界面逻辑
# ==========================================
st.markdown(
    "<h1 style='text-align: center; font-size: 24px; margin-bottom: 30px;'>한국어 발음 변환기</h1>",
    unsafe_allow_html=True
)

user_input = st.text_area(
    "Input",
    value=auto_word,           # 如果是从 ?q= 进来，自动填入
    height=150,
    label_visibility="collapsed",
    placeholder="Paste Korean text here..."
)
st.write("")

# 按钮放在中间列
left_col, mid_col, right_col = st.columns([1, 2, 1])
with mid_col:
    analyze_clicked = st.button("ANALYZE", use_container_width=True)

# ==========================================
# 8. 执行转换逻辑
# ==========================================
text_to_convert = None

if analyze_clicked:
    # 用户点按钮时，以当前文本框内容为准
    text_to_convert = user_input.strip()
elif auto_run:
    # 没点按钮，但 URL 里带 q=，自动跑一次
    text_to_convert = auto_word

if text_to_convert:
    clean_text = text_to_convert.replace("\n", " ").replace("\r", " ")
    try:
        pronunciation = pnu_g2p(clean_text)
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
    if analyze_clicked:
        st.warning("Please enter text.")

