import re
import streamlit as st

# ==========================================
# 0. g2pk 导入
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
# 3. 一般清理：空格 / 标点
# ==========================================
def normalize_spaces(text: str) -> str:
    # 连续空格压成一个
    text = re.sub(r"\s+", " ", text)
    # 去掉标点前面的空格
    text = re.sub(r"\s+([.,!?…·，．？！、:;:\]])", r"\1", text)
    # 去掉首尾空格
    return text.strip()

# ==========================================
# 4. 釜大风格音变补丁层（比原始 g2pk 更接近釜山大转换器）
# ==========================================
def apply_pnu_rules(text: str) -> str:
    """
    在 g2pk 的基础发音结果上，叠加一层“釜大风格”的规则。
    这里只是第一版：先覆盖常见、明显的差异，
    后续如果你发现新的例子，可以继续往下加规则。
    """

    # ---- 4.1 助词/语尾类：에는 → 에느 ----
    # 顺序：先匹配长串，再匹配短串
    particle_patches = [
        ("에는요", "에느요"),
        ("에는도", "에느도"),
        ("에는만", "에느만"),
        ("에는까지", "에느까지"),
        ("에는", "에느"),
    ]
    for before, after in particle_patches:
        text = text.replace(before, after)

    # ---- 4.2 部分连音 / 비음화 / 경음화：일정 → 닐정 等 ----
    # 这里只写了你已经发现、以及非常常用的一些模式，
    # 以后可以继续加。
    pnu_patches = [
        ("일정", "닐정"),   # 일정 → 닐정
        ("일주", "닐주"),   # 일주 → 닐주
        ("물질", "물찔"),   # 물질 → 물찔
        ("핣지", "핮지"),   # 예: 할지 → 핮지（如果前面已经变成 핣지）
        # 你可以根据需要继续往下面追加规则
    ]
    for before, after in pnu_patches:
        text = text.replace(before, after)

    return text

# ==========================================
# 5. “完整的釜大风格发音模块”
# ==========================================
def pnu_g2p(text: str) -> str:
    """
    比单独 g2pk 更精确的版本：
    1) 用 g2pk 先做形态分析 + 基础音变；
    2) 再做一遍空格/标点清理；
    3) 套用我们自定义的釜大风格规则。
    """
    base = g2p(text)          # g2pk 基础发音
    base = normalize_spaces(base)
    refined = apply_pnu_rules(base)
    refined = normalize_spaces(refined)
    return refined

# ==========================================
# 6. 界面逻辑
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

# 中间居中的按钮
left_col, mid_col, right_col = st.columns([1, 2, 1])
with mid_col:
    analyze_clicked = st.button("ANALYZE", use_container_width=True)

# 点击按钮后处理
if analyze_clicked:
    if user_input.strip():
        clean_text = user_input.replace("\n", " ").replace("\r", " ")
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
        st.warning("Please enter text.")
