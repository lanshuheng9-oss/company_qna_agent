# core/query_agent.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from config.config import settings
from core.llm_engine.chat_model import ChatModel

# 这里导入我们刚刚新建的两个专属 Prompt
from prompts.qa_prompt import QA_SYSTEM_PROMPT
from prompts.guide_prompt import GUIDE_SYSTEM_PROMPT

def ask_agent(user_query: str):
    print(f"\n【用户问】: {user_query}")
    print("1. 正在将您的问题转换为向量，并在知识库中搜索相关规定...")
    
    embeddings = DashScopeEmbeddings(dashscope_api_key=settings.DASHSCOPE_API_KEY)
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 🧠 【升级 1】：使用带分数的检索，并将 k 值扩大到 15，防止长项目被截断！
    docs_and_scores = vectorstore.similarity_search_with_score(user_query, k=15)
    
    if not docs_and_scores:
        print("未能在知识库中检索到相关内容。")
        chat_model = ChatModel()
        return chat_model.generate_answer(user_query, "", QA_SYSTEM_PROMPT)

    # 🧠 【升级 2】：在终端打印分数，帮你监控数据库到底捞出了什么（Chroma 默认分数越低越相似）
    print(f"   -> 数据库共捞出 {len(docs_and_scores)} 条候选数据：")
    docs = []
    for i, (doc, score) in enumerate(docs_and_scores):
        source = doc.metadata.get("source", "未知来源")
        # 只打印前 5 条的分数供参考，避免屏幕太乱
        if i < 5:
            print(f"      [{i+1}] 距离得分: {score:.4f} | 来源: {source}")
        docs.append(doc)
    if len(docs_and_scores) > 5:
        print(f"      ... (已折叠剩余 {len(docs_and_scores)-5} 条)")

    # 提取前 3 条文档的来源标签，用来做智能路由
    top_3_sources = [doc.metadata.get("source", "") for doc in docs[:3]]
    
    # 只要前 3 条里有任何一条命中了“业务问答”库，就赋予它最高优先级
    is_qa_hit = False
    for source in top_3_sources:
        if "问答" in source or "AI业务问答" in source:
            is_qa_hit = True
            break

    # 根据优先级动态挑选对应的 Prompt
    if is_qa_hit:
        active_system_prompt = QA_SYSTEM_PROMPT
        print("   -> 智能路由：检测到【问答库】命中，已强制切换为【业务问答专属 Prompt】")
    else:
        active_system_prompt = GUIDE_SYSTEM_PROMPT
        print("   -> 智能路由：未命中问答库，已自动切换为【受理指南专属 Prompt】")

    # 把捞出来的所有 15 个段落拼接成上下文
    # 放心：即使后面几条是不相关的“凑数”数据，大模型的 Prompt 也会让它自动过滤噪音
    retrieved_context = "\n\n".join([doc.page_content for doc in docs])
    
    # 呼叫大模型，把动态选中的 Prompt 喂给它
    chat_model = ChatModel()
    answer = chat_model.generate_answer(
        query=user_query, 
        context=retrieved_context, 
        system_prompt_template=active_system_prompt
    )
    
    return answer

if __name__ == "__main__":
    # 这是一个本地测试代码，可以直接右键运行测试
    query = "白色硅酸盐水泥有哪些检测项目？"
    result = ask_agent(query)
    print("\n========== [客服智能体回答] ==========")
    print(result)
    print("======================================")