# app.py 
import streamlit as st
import os
import tempfile
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from dashscope import MultiModalConversation

from config.config import settings
# 核心找回：导入你之前写好的专属客服系统 Prompt！
from prompts.system_prompt import QNA_SYSTEM_PROMPT 

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
# 2. 初始化系统（支持云端自动建库）
# ==========================================
@st.cache_resource
def init_rag_system(show_spinner=False):
    embeddings = DashScopeEmbeddings(dashscope_api_key=settings.DASHSCOPE_API_KEY)
    persist_directory = "./chroma_db"
    
    # 如果没检测到数据库（比如在云端），就自动现场搭一个
    if not os.path.exists(persist_directory) or not os.listdir(persist_directory):
        loader = DirectoryLoader(
            './data', 
            glob="**/*.md", 
            loader_cls=TextLoader, 
            loader_kwargs={'encoding': 'utf-8'}
        )
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_directory)
    else:
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        
    return vectorstore

vectorstore = init_rag_system()

# ==========================================
# 3. 聊天历史记录管理
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image_path" in message and message["image_path"]:
            st.image(message["image_path"], caption="上传的截图", width=250)
        st.markdown(message["content"])

# ==========================================
# 4. 悬浮传图小图标组件 (Popover)
# ==========================================
with st.popover("🖼️ 点击上传截图"):
    uploaded_file = st.file_uploader("支持 PNG, JPG", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_file:
        st.success("✅ 图片已就绪，请在下方输入您的问题！")

# ==========================================
# 5. 核心对话与检索生成逻辑
# ==========================================
if user_query := st.chat_input("问问AI吧..."):
    
    # 5.1 处理图片保存
    image_temp_path = None
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            image_temp_path = tmp_file.name

    # 5.2 渲染用户输入
    message_data = {"role": "user", "content": user_query, "image_path": image_temp_path}
    st.session_state.messages.append(message_data)
    with st.chat_message("user"):
        if image_temp_path:
            st.image(image_temp_path, width=250)
        st.markdown(user_query)

    # 5.3 开启大模型推理
    with st.chat_message("assistant"):
        with st.spinner("正在查阅知识库并生成解答，请稍候..."):
            try:
                # 【关键修复】先去本地 Chroma 数据库里查资料！
                docs = vectorstore.similarity_search(user_query, k=3)
                context_text = "\n\n".join([doc.page_content for doc in docs])
                
                # 【关键修复】将你的专属 Prompt、检索到的规范资料、以及用户问题，拼装成最终的完整 Prompt
                final_text_prompt = f"""
                {QNA_SYSTEM_PROMPT}

                【参考文档】
                {context_text}

                【客户提问】
                {user_query}
                """
                
                # 如果传了图，稍微补一句让它结合图片
                if image_temp_path:
                    final_text_prompt += "\n\n[注：客户还提供了一张相关业务系统截图，请结合图片内容与送检规范一并解答或提供优化建议。]"

                # 构建请求参数
                content_list = []
                if image_temp_path:
                    content_list.append({"image": f"file://{image_temp_path}"})
                content_list.append({"text": final_text_prompt})

                messages = [{'role': 'user', 'content': content_list}]
                
                # 调用多模态大模型
                response = MultiModalConversation.call(
                    model='qwen-vl-max', 
                    messages=messages,
                    api_key=settings.DASHSCOPE_API_KEY
                )
                
                if response.status_code == 200:
                    answer = response.output.choices[0].message.content[0]["text"]
                else:
                    answer = f"调用大模型出错，错误信息: {response.message}"
                
            except Exception as e:
                answer = f"发生异常错误: {str(e)}"
            
            st.markdown(answer)
            
    # 保存助手回答
    st.session_state.messages.append({"role": "assistant", "content": answer, "image_path": None})