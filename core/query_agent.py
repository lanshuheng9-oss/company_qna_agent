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

# 🚀【新增了 history 参数，默认值为空列表】
def ask_agent(user_query: str, history: list = None):
    if history is None:
        history = []
        
    print(f"\n【用户原始问题】: {user_query}")
    
    # 提前实例化 ChatModel，因为我们要先用它来评估和改写问题意图
    chat_model = ChatModel()
    
    # ==========================================
    # 🧠 【架构升级：Query Rewrite 问题重写】
    # ==========================================
    search_query = user_query
    if history:
        print("0. 正在根据历史上下文重写用户意图...")
        search_query = chat_model.rewrite_query(user_query, history)
        if search_query != user_query:
            print(f"   -> 🎯 意图识别完毕: [{user_query}] ===> [{search_query}]")
        else:
            print("   -> 🎯 意图已完整，无需改写。")

    print(f"1. 正在将问题【{search_query}】转换为向量，并在知识库中搜索相关规定...")
    
    embeddings = DashScopeEmbeddings(dashscope_api_key=settings.DASHSCOPE_API_KEY)
    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    
    # 🧠 【升级 1】：注意这里传给数据库搜索的是改写后的准确词 search_query！
    docs_and_scores = vectorstore.similarity_search_with_score(search_query, k=15)
    
    if not docs_and_scores:
        print("未能在知识库中检索到相关内容。")
        # 找不到时也用流式方法，防止前端报错
        return chat_model.generate_answer_stream(user_query, "", QA_SYSTEM_PROMPT, history=history)

    # 🧠 【升级 2】：在终端打印分数，帮你监控数据库到底捞出了什么
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
    retrieved_context = "\n\n".join([doc.page_content for doc in docs])
    
    # 呼叫大模型，把动态选中的 Prompt 喂给它
    # ⚠️ 【注意】：这里传给大模型生成回答的，依然是用户的原话 user_query
    answer_generator = chat_model.generate_answer_stream(
        query=user_query, 
        context=retrieved_context, 
        system_prompt_template=active_system_prompt,
        history=history  # 👈 记忆历史通道
    )
    # 直接把生成器抛给前端去慢慢读取
    return answer_generator

if __name__ == "__main__":
    # 这是一个本地测试代码，可以直接右键运行测试
    query = "白色硅酸盐水泥有哪些检测项目？"
    result = ask_agent(query)
    print("\n========== [客服智能体回答] ==========")
    # 适配了流式输出的打印方式
    for chunk in result:
        print(chunk, end="", flush=True)
    print("\n======================================")