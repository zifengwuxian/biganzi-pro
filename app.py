import streamlit as st
from openai import OpenAI
import os

# ==========================================
# 1. 核心配置
# ==========================================
# 从云端保险箱读取密钥
API_KEY = st.secrets["DEEPSEEK_KEY"] 
BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

st.set_page_config(page_title="机关笔杆子Pro", page_icon="✒️", layout="centered")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ==========================================
# 2. 商业闭环 (收钱的逻辑在这里！)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/wechat.png", width=50) # 微信图标
    st.markdown("### 🔓 解锁完整版")
    st.markdown("扫码或加V：**liao13689209126**") # ★★★ 改成你的微信号
    st.markdown("获取专属访问密码，仅需 9.9元/月")
    
    # 支付二维码展示
    st.markdown("#### 📲 扫码购卡")
    pay_tab1, pay_tab2 = st.tabs(["🟢 微信", "🔵 支付宝"])
    with pay_tab1:
        if os.path.exists("pay_wechat.png"):
            st.image("pay_wechat.png")
        elif os.path.exists("pay_wechat.jpg"):
            st.image("pay_wechat.jpg")
        else:
            st.warning("⚠️ 请上传 pay_wechat.png")
    with pay_tab2:
        if os.path.exists("pay_alipay.png"):
            st.image("pay_alipay.png")
        elif os.path.exists("pay_alipay.jpg"):
            st.image("pay_alipay.jpg")
        else:
            st.warning("⚠️ 请上传 pay_alipay.png")
    
    # 密码输入框
    secret_pass = st.text_input("请输入访问密码", type="password")
    
    st.info("💡 为什么要收费？\n因为集成了昂贵的 DeepSeek-V3 商业版模型，确保生成的公文最地道。")

# ==========================================
# 3. 逻辑判断
# ==========================================
# 只有密码对，或者没输密码时给个预览，才能往下走
# 这里我们设置密码为 "8888" (你可以自己改)
if secret_pass != "3361":
    st.title("✒️ 机关笔杆子 Pro")
    st.warning("🔒 请在左侧输入密码解锁使用。")
    st.markdown("#### 它可以帮你：")
    st.markdown("- ✅ 一键润色周报")
    st.markdown("- ✅ 口语秒变公文")
    st.markdown("- ✅ 自动扩写汇报材料")
    st.stop() # 停止运行下面的代码

# ==========================================
# 4. 只有解锁后才会显示的主程序
# ==========================================
SYSTEM_PROMPT = """
你是一位拥有 20 年工龄的体制内资深“笔杆子”。
要求：彻底去口语化，结构化输出（一、二、三），词汇升级，政治站位高，禁止废话。
"""

def polish_text(user_text):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=1.3,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 出错: {str(e)}"

st.title("✒️ 机关笔杆子 Pro (已解锁)")
user_input = st.text_area("请输入素材：", height=150, placeholder="例：去社区看了看，发现卫生很差...")

if st.button("🚀 立即润色", type="primary"):
    if not user_input:
        st.warning("请先输入内容！")
    else:
        with st.spinner("AI 正在奋笔疾书..."):
            result = polish_text(user_input)
            st.markdown(result)
            st.success("生成的真不错！")