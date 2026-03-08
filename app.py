import streamlit as st
from openai import OpenAI
import os
import requests
import json
from datetime import datetime, timedelta

# ==========================================
# 1. 核心配置
# ==========================================
APP_CODE = "wordsmith"
BASE_URL = "https://api.deepseek.com"

st.set_page_config(page_title="机关笔杆子Pro", page_icon="✒️", layout="centered")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 延迟初始化 API_KEY，避免 ScriptRunContext 警告
API_KEY = st.secrets["DEEPSEEK_KEY"] 
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 初始化会话状态
if "is_auth" not in st.session_state:
    st.session_state.is_auth = False
if "vip_info" not in st.session_state:
    st.session_state.vip_info = None
if "user_id" not in st.session_state:
    st.session_state.user_id = "default"

# ==========================================
# 2. 云端验证函数 (避免 auth.py 中的 ScriptRunContext 问题)
# ==========================================
def check_license_safe(input_key, current_app_code):
    """
    安全的卡密验证函数，避免 ScriptRunContext 警告
    """
    try:
        # 直接在这里实现验证逻辑，避免调用 auth.py
        token = st.secrets["GITHUB_TOKEN"]
        gist_id = st.secrets["GIST_ID"]
        filename = "matrix_licenses.json"
        
        headers = {"Authorization": f"token {token}"}
        url = f"https://api.github.com/gists/{gist_id}?t={datetime.now().timestamp()}"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            return False, f"云端连接失败 (HTTP {resp.status_code})", None
        
        data = resp.json()['files'][filename]['content']
        db = json.loads(data)
        
        # 验证卡密是否存在
        if input_key not in db:
            return False, "❌ 无效卡密，请检查输入", None
        
        card_info = db[input_key]
        
        # 验证适用范围
        app_scope = card_info.get('app_scope', '')
        if app_scope != 'ALL' and app_scope != current_app_code:
            return False, f"⚠️ 此卡是【{card_info.get('type_name', '未知类型')}】，不能用于本项目", None
        
        # 验证状态
        status = card_info.get('status', 'UNKNOWN')
        
        if status == 'BANNED':
            return False, "🚫 此卡已被封禁", None
        
        if status == 'UNUSED':
            type_name = card_info.get('type_name', '会员')
            is_admin = card_info.get('is_admin', False)
            
            if is_admin:
                return True, f"👑 管理员已激活", card_info
            else:
                return True, f"✅ {type_name}已激活", card_info
            
        elif status == 'ACTIVE':
            # 检查是否过期
            start_date = card_info.get('start_date')
            if start_date:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                    validity_days = card_info.get('validity_days', 30)
                    expiry = start + timedelta(days=validity_days)
                    
                    if datetime.now() > expiry:
                        return False, "⚠️ 此卡已过期", card_info
                except:
                    pass  # 日期解析失败，忽略过期检查
            
            is_admin = card_info.get('is_admin', False)
            if is_admin:
                return True, f"👑 欢迎回来，管理员", card_info
            else:
                return True, f"👋 欢迎回来，{card_info.get('type_name', '会员')}", card_info
        
        return False, "⚠️ 卡密状态异常，请联系客服", None
        
    except requests.exceptions.Timeout:
        return False, "❌ 连接超时，请检查网络", None
    except requests.exceptions.ConnectionError:
        return False, "❌ 网络连接错误", None
    except Exception as e:
        return False, f"❌ 验证失败: {str(e)}", None

# ==========================================
# 3. 商业闭环 (收钱的逻辑在这里！)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/wechat.png", width=50)
    st.markdown("### 🔓 解锁完整版")
    
    if not st.session_state.is_auth:
        st.info("🔒 系统已加密，请获取卡密解锁")
        
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
        
        st.markdown("---")
        
        # 卡密输入框
        license_key = st.text_input("🔑 输入卡密", type="password", placeholder="WORD-xxxx 或 ALL-xxxx")
        st.markdown("(客服微信: liao13689209126)")
        
        if st.button("🚀 联网激活"):
            with st.spinner("验证中..."):
                # 使用安全的验证函数
                success, info, card_info = check_license_safe(license_key, APP_CODE)
                if success:
                    st.session_state.is_auth = True
                    st.session_state.vip_info = info
                    st.session_state.user_id = license_key.strip()
                    st.balloons()
                    st.rerun()
                else:
                    st.error(info)
        
        st.info("💡 为什么要收费？\n因为集成了昂贵的 DeepSeek-V3 商业版模型，确保生成的公文最地道。")
    else:
        st.success(f"💎 {st.session_state.vip_info}")
        st.markdown(f"**通行证 ID:** `***{st.session_state.user_id[-4:]}`")
        
        st.markdown("---")
        if st.button("🔒 退出登录"):
            st.session_state.is_auth = False
            st.session_state.user_id = "default"
            st.session_state.vip_info = None
            st.rerun()

# ==========================================
# 4. 逻辑判断
# ==========================================
if not st.session_state.is_auth:
    st.title("✒️ 机关笔杆子 Pro")
    st.warning("🔒 请在左侧输入卡密解锁使用。")
    st.markdown("#### 它可以帮你：")
    st.markdown("- ✅ 一键润色周报")
    st.markdown("- ✅ 口语秒变公文")
    st.markdown("- ✅ 自动扩写汇报材料")
    st.info("👈 **请点击左上角 `>` 箭头展开侧边栏，进行支付与激活。**")
    st.stop()

# ==========================================
# 5. 只有解锁后才会显示的主程序
# ==========================================
SYSTEM_PROMPT = """
你是一位拥有 20 年工龄的体制内资深"笔杆子"。
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

st.title(f"✒️ 机关笔杆子 Pro ({st.session_state.vip_info})")
user_input = st.text_area("请输入素材：", height=150, placeholder="例：去社区看了看，发现卫生很差...")

if st.button("🚀 立即润色", type="primary"):
    if not user_input:
        st.warning("请先输入内容！")
    else:
        with st.spinner("AI 正在奋笔疾书..."):
            result = polish_text(user_input)
            st.markdown(result)
            st.success("生成的真不错！")