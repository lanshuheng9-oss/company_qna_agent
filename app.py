import streamlit as st
import os

# 💡 引入我们写好的 UI 模块与核心大脑
from ui.chat_window import render_chat_window
from ui.input_area import render_input_area
from core.query_agent import ask_agent

# ==========================================
# 1. 页面基本配置与全局样式加载
# ==========================================
st.set_page_config(
    page_title="健研检测客服",
    page_icon="🛡️",
    layout="centered"
)

# 加载 assets/style.css 样式美化文件
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==========================================
# 2. 渲染侧边栏并获取配置
# ==========================================

# ==========================================
# 3. 渲染主界面（大标题与历史聊天记录）
# ==========================================
render_chat_window()

# ==========================================
# 4. 渲染输入区域并获取用户输入与图片
# ==========================================
user_query, image_temp_path = render_input_area()

# ==========================================
# 5. 核心对话与检索生成逻辑
# ==========================================
if user_query:
    # 5.1 渲染并记录用户输入
    message_data = {"role": "user", "content": user_query, "image_path": image_temp_path}
    st.session_state.messages.append(message_data)
    
    with st.chat_message("user"):
        if image_temp_path:
            st.image(image_temp_path, width=250)
        st.markdown(user_query)

    # 5.2 开启大模型推理 (流式 + 思考中动画 + 历史记忆)
    with st.chat_message("assistant"):
        try:
            # 1. 思考中提示
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("**思考中...**")
            
            chat_history = st.session_state.messages[:-1]
            answer_generator = ask_agent(user_query, history=chat_history)
            
            def intercept_stream(generator):
                is_first_chunk = True
                for chunk in generator:
                    if is_first_chunk:
                        thinking_placeholder.empty()
                        is_first_chunk = False
                    yield chunk
            
            # 🌟 关键优化：创建一个专门的占位符来承载打字效果
            message_placeholder = st.empty()
            full_answer = message_placeholder.write_stream(intercept_stream(answer_generator))
            
            # 🌟 关键优化：打字一结束，立刻将正文与免责声明合并，用 markdown 瞬间覆盖原占位符！
            # 这样就不会有任何卡顿感，是一次性渲染的。
            disclaimer_html = "<div style='font-size: 11px; color: #9ca3af; margin-top: 12px;'>此前由AI生成的内容仅供参考，最终有效信息请以人工客服后续提供的回复为准。</div>"
            message_placeholder.markdown(full_answer + disclaimer_html, unsafe_allow_html=True)
            
        except Exception as e:
            thinking_placeholder.empty()
            full_answer = f"发生异常错误: {str(e)}"
            st.markdown(full_answer)
            
    # 5.3 保存历史记录（仍然只保存 full_answer，保护 AI 记忆不被污染）
    st.session_state.messages.append({"role": "assistant", "content": full_answer, "image_path": None})