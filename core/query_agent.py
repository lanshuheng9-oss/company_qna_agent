# query_agent.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from config.config import settings
from core.llm_engine.chat_model import ChatModel

def ask_agent(user_query: str):
    print(f"【用户问】: {user_query}")
    print("1. 正在将您的问题转换为向量，并在知识库中搜索相关规定...")
    
    # 初始化百炼的向量翻译官
    embeddings = DashScopeEmbeddings(dashscope_api_key=settings.DASHSCOPE_API_KEY)
    
    # 连接本地的 Chroma 数据库
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 在数据库里搜索与问题最相关的 3 个段落
    docs = vectorstore.similarity_search(user_query, k=3)
    
    if not docs:
        print("未能在知识库中检索到相关内容。")
        return

    # 把捞出来的段落拼接成大模型需要的上下文
    retrieved_context = "\n\n".join([doc.page_content for doc in docs])
    print("   -> 成功找到相关参考内容，准备让客服智能体组织语言...\n")
    
    # 呼叫大模型，把真实搜索到的 context 喂给它
    chat_model = ChatModel()
    answer = chat_model.generate_answer(query=user_query, context=retrieved_context)
    
    print("========== [客服智能体回答] ==========")
    print(answer)
    print("======================================")

if __name__ == "__main__":
    # 你随时可以在这里修改你想问的问题！
    query = "你好，我这两天准备送检一批散装水泥，请问每批数量有什么限制吗？取样怎么做？"
    ask_agent(query)