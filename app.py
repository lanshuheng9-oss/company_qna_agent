# app.py 
import streamlit as st
import os
import tempfile

# 💡 核心导入：直接呼叫我们写好的“智能路由大脑”
from core.query_agent import ask_agent

# ==========================================
# 1. 页面基本配置与大标题
# ==========================================
st.set_page_config(
    page_title="健研检测客服",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ 健研检测客服")
st.markdown("健研检测客服回答你的问题")

# ==========================================
# 2. 聊天历史记录管理
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image_path" in message and message["image_path"]:
            st.image(message["image_path"], caption="上传的截图", width=250)
        st.markdown(message["content"])

# ==========================================
# 3. 悬浮传图小图标组件 (Popover)
# ==========================================
with st.popover("🖼️ 点击上传截图"):
    uploaded_file = st.file_uploader("支持 PNG, JPG", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_file:
        st.success("✅ 图片已就绪，请在下方输入您的问题！")

# ==========================================
# 4. 核心对话与检索生成逻辑
# ==========================================
if user_query := st.chat_input("问问AI吧..."):
    
    # 4.1 处理图片保存 (UI逻辑保留，方便以后多模态扩展)
    image_temp_path = None
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            image_temp_path = tmp_file.name

    # 4.2 渲染用户输入
    message_data = {"role": "user", "content": user_query, "image_path": image_temp_path}
    st.session_state.messages.append(message_data)
    with st.chat_message("user"):
        if image_temp_path:
            st.image(image_temp_path, width=250)
        st.markdown(user_query)

    # 4.3 开启大模型推理 (🚀 流式升级版 + 智能等待动画 + 多轮历史记忆)
    with st.chat_message("assistant"):
        try:
            # 1. 创建一个空的占位符，先显示“思考中”提示
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("**思考中...**")
            
            # 2. 提取除当前问题外的所有历史对话记录
            chat_history = st.session_state.messages[:-1]
            
            # 3. 呼叫后端大脑并传入 history
            answer_generator = ask_agent(user_query, history=chat_history)
            
            # 4. 编写“首字拦截器”
            def intercept_stream(generator):
                is_first_chunk = True
                for chunk in generator:
                    if is_first_chunk:
                        # 💥 拦截到第一个字时，瞬间清空“思考中”提示！
                        thinking_placeholder.empty()
                        is_first_chunk = False
                    yield chunk
            
            # 5. 使用 write_stream 渲染打字机效果
            full_answer = st.write_stream(intercept_stream(answer_generator))
            
        except Exception as e:
            thinking_placeholder.empty() # 报错时清空提示
            full_answer = f"发生异常错误: {str(e)}"
            st.markdown(full_answer)
            
    # 保存助手完整的回答到历史记录中
    st.session_state.messages.append({"role": "assistant", "content": full_answer, "image_path": None})