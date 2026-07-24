import streamlit as st

def render_chat_window():
    """渲染页面头部和大标题，以及所有历史聊天记录"""
    
    st.title("🛡️ 健研检测客服")
    st.markdown("健研检测客服回答你的问题")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image_path" in message and message["image_path"]:
                st.image(message["image_path"], caption="上传的截图", width=250)
            
            # 🌟 关键优化：如果是 AI 回答，将正文和小字合并成一次 markdown 渲染
            if message["role"] == "assistant":
                disclaimer_html = "<div style='font-size: 11px; color: #9ca3af; margin-top: 12px;'>此前由AI生成的内容仅供参考，最终有效信息请以人工客服后续提供的回复为准。</div>"
                st.markdown(message["content"] + disclaimer_html, unsafe_allow_html=True)
            else:
                st.markdown(message["content"])