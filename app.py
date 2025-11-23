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

    .stTextArea textarea { 
        font-size: 16px; 
        border: 1px solid #333; 
        border-radius: 4px; 
    }

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
# 3. 通用空格 / 标点清理
# ==========================================
def normalize_spaces(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?…·，．？！、:;:\]])", r"\1", text)
    return text.strip()

# ==========================================
# 4. 釜大风格：在“原始韩文”上做的规则（真正决定发音写法）
# ==========================================
def apply_pnu_input_rules(text: str) -> str:
    """
    在送入 g2pk 之前，对「正字韩文」做一次替换，
    让它长得更像釜山大发音转换器的结果。
    """

    # 1) 助词「에는」系 → 「에느」
    #   以后如果你发现别的类似情况，可以继续往下加。
    particle_rules = [
        ("에는요", "에느요"),
        ("에는도", "에느도"),
        ("에는만", "에느만"),
        ("에는까지", "에느까지"),
        ("에는", "에느"),
    ]
    for before, after in particle_rules:
        text = text.replace(before, after)

    # 2) 常见连音 / 비음화：일정 → 닐정 等
    #   这里直接把原文里的字改掉，再交给 g2pk。
    word_rules = [
        ("일정이", "닐정이"),
        ("일정은", "닐정은"),
        ("일정을", "닐정을"),
        ("일정도", "닐정도"),
        ("일정", "닐정"),   # 最后一条兜底（单独出现时）
        # 后续可以根据需要继续加：
        # ("일주일", "닐주일"),
        # ("일주가", "닐주가"),
    ]
    for before, after in word_rules:
        text = text.replace(before, after)

    return text

# ==========================================
# 5. 完整的「釜大风格」发音模块
# ==========================================
def pnu_g2p(text: str) -> str:
    """
    1) 先在原文上套用釜大规则（에느 / 닐정 等）；
    2) 再交给 g2pk 做其余音变；
    3) 最后整理空格。
    """
    preprocessed = apply_pnu_input_rules(text)
    result = g2p(preprocessed)
