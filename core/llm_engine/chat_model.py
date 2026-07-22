# core/llm_engine/chat_model.py
import sys
import os
# 确保能正确导入项目根目录的其他模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from openai import OpenAI
from config.config import settings
from prompts.system_prompt import QNA_SYSTEM_PROMPT

class ChatModel:
    def __init__(self):
        # 初始化百炼的大模型客户端
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.DEFAULT_MODEL

    def generate_answer(self, query: str, context: str) -> str:
        """
        根据用户问题和检索到的文档上下文生成回答
        """
        # 将检索到的文档填入提示词的 {context} 槽位中
        formatted_system_prompt = QNA_SYSTEM_PROMPT.format(context=context)
        
        messages = [
            {"role": "system", "content": formatted_system_prompt},
            {"role": "user", "content": query}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                # temperature 控制随机性。设为 0.1 可以让大模型的回答更稳定、更严谨，不易脱离文档发散
                temperature=0.1, 
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成回答时发生系统错误：{e}"