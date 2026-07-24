import streamlit as st
import os
import tempfile

def render_input_area():
    """渲染经典的底部输入区，带有清爽的折叠传图面板，输入框严格吸底"""
    
    # 用一个精简的 expander 或 popover 放在输入框上方，模拟大厂的折叠菜单
    with st.popover("＋", help="点击展开图片上传"):
        uploaded_file = st.file_uploader(
            "支持 PNG, JPG 格式截图", 
            type=["png", "jpg", "jpeg"], 
            label_visibility="collapsed"
        )
        if uploaded_file:
            st.success("✅ 图片已就绪，请直接在下方输入框发送问题！")

    # 核心聊天输入框（回归原生：由于没有 columns 挤压，它会自动牢牢吸在浏览器最底部）
    user_query = st.chat_input("问问AI吧...")

    # 处理图片暂存与落盘逻辑
    if 'current_uploaded_file' not in st.session_state:
        st.session_state.current_uploaded_file = None
        
    if locals().get('uploaded_file') is not None:
        st.session_state.current_uploaded_file = uploaded_file

    image_temp_path = None
    if user_query:
        target_file = st.session_state.current_uploaded_file
        if target_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(target_file.name)[1]) as tmp_file:
                tmp_file.write(target_file.getvalue())
                image_temp_path = tmp_file.name
            st.session_state.current_uploaded_file = None
            
    return user_query, image_temp_path

