# core/llm_engine/test_chat.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core.llm_engine.chat_model import ChatModel

def run_test():
    chat_model = ChatModel()
    
    # 【模拟环境】捞出来的带 ID 的业务文档
    mock_retrieved_context = """
    文件片段ID: [019f4977-b9c7-7910-bcbe-b100425a251b]
    内容：水泥送检批次划分：袋装水泥每批不超过200吨，散装水泥每批不超过500吨。取样方法需从20个不同点位等量取样混合，确保总量不少于12千克。
    
    文件片段ID: [019f497a-db26-759a-8b7d-079c74995eb7]
    内容：送检时需提供出厂合格证，委托单上应注明厂家、品种、强度等级等信息。
    """
    
    # 模拟客户的提问
    user_query = "你好，我这边有一批散装水泥要送检，大概要取多少样品啊？还需要带什么资料吗？"
    
    print("正在请求智能客服回答，请稍候...\n")
    answer = chat_model.generate_answer(query=user_query, context=mock_retrieved_context)
    
    print("========== [客服智能体回答] ==========")
    print(answer)
    print("======================================")

if __name__ == "__main__":
    run_test()